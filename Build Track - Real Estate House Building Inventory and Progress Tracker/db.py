import os
import re
import mysql.connector
from mysql.connector import Error
from config import Config

def get_raw_connection(use_db=True):
    """Establish a direct MySQL connection."""
    kwargs = {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'autocommit': False
    }
    if use_db:
        kwargs['database'] = Config.DB_NAME
    return mysql.connector.connect(**kwargs)

def get_db():
    """Return a database connection with dictionary cursor support."""
    try:
        conn = get_raw_connection(use_db=True)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database '{Config.DB_NAME}': {e}")
        raise

def query_db(query, args=(), one=False, commit=False):
    """Execute a query and return results as dictionary or inserted ID."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            result = cursor.lastrowid
        else:
            rows = cursor.fetchall()
            result = (rows[0] if rows else None) if one else rows
    except Error as e:
        if commit:
            conn.rollback()
        print(f"Database query error: {e}\nQuery: {query}\nArgs: {args}")
        raise
    finally:
        cursor.close()
        conn.close()
    return result

def init_db():
    """Initialize database and create all tables from schema.sql."""
    try:
        # Step 1: Connect to MySQL server without database
        conn = get_raw_connection(use_db=False)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cursor.close()
        conn.close()

        # Step 2: Connect to the created database and execute schema.sql
        conn = get_raw_connection(use_db=True)
        cursor = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8-sig') as f:
                sql_content = f.read()

            # Remove multi-line comments
            sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)

            # Split statements by semicolon
            raw_statements = sql_content.split(';')
            for stmt in raw_statements:
                # Remove single line comments
                lines = [line for line in stmt.splitlines() if not line.strip().startswith('--')]
                stmt_clean = '\n'.join(lines).strip()
                if stmt_clean:
                    cursor.execute(stmt_clean)
            conn.commit()
            print(f"Schema initialized successfully in database '{Config.DB_NAME}'.")
        else:
            print(f"Warning: schema file not found at {schema_path}")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization failed: {repr(e)}")
        return False

if __name__ == '__main__':
    print("Initializing Database...")
    success = init_db()
    if success:
        print("Database ready!")
    else:
        print("Database initialization encountered an issue.")
