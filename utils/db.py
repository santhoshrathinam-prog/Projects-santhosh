import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from config import Config

_schema_verified = False

def init_upload_dirs():
    """Ensures all static upload directories exist on disk."""
    dirs = [
        Config.UPLOAD_FOLDER_PRODUCTS,
        Config.UPLOAD_FOLDER_FARMERS,
        Config.UPLOAD_FOLDER_CUSTOMERS,
        Config.UPLOAD_FOLDER_DELIVERY,
        Config.UPLOAD_FOLDER_ADMIN,
    ]
    for rel_path in dirs:
        abs_path = Config.BASE_DIR / rel_path
        abs_path.mkdir(parents=True, exist_ok=True)

# Create folders at startup
init_upload_dirs()

def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    Raises an error if the connection fails.
    """
    global _schema_verified
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        if not _schema_verified:
            ensure_schema(connection)
            _schema_verified = True
        return connection
    except Error as e:
        print(f"[Database Connection Error]: {e}")
        return None

def ensure_schema(conn):
    """
    Ensures that any optional/extended columns exist without destroying
    or altering any existing user data:
    1. products.approval_status
    2. products.image_filename
    3. users.profile_image
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Check approval_status in products
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'products' AND COLUMN_NAME = 'approval_status';
        """, (Config.DB_NAME,))
        if not cursor.fetchone():
            print("[Database]: Adding approval_status column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN approval_status ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' 
                AFTER product_status;
            """)
            cursor.execute("UPDATE products SET approval_status = 'approved' WHERE product_status = 'available';")
            conn.commit()
            print("[Database]: approval_status column successfully initialized.")

        # 2. Check image_filename in products
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'products' AND COLUMN_NAME = 'image_filename';
        """, (Config.DB_NAME,))
        if not cursor.fetchone():
            print("[Database]: Adding image_filename column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN image_filename VARCHAR(255) DEFAULT NULL;
            """)
            conn.commit()
            print("[Database]: image_filename column successfully initialized.")

        # 3. Check profile_image in users
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'profile_image';
        """, (Config.DB_NAME,))
        if not cursor.fetchone():
            print("[Database]: Adding profile_image column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN profile_image VARCHAR(255) DEFAULT NULL;
            """)
            conn.commit()
            print("[Database]: profile_image column successfully initialized.")

        # 4. Check transaction_id in orders
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'transaction_id';
        """, (Config.DB_NAME,))
        if not cursor.fetchone():
            print("[Database]: Adding transaction_id column to orders table...")
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN transaction_id VARCHAR(100) DEFAULT NULL 
                AFTER payment_status;
            """)
            conn.commit()
            print("[Database]: transaction_id column successfully initialized.")

        cursor.close()
    except Error as e:
        print(f"[Database Schema Check Warning]: {e}")

def query_db(query, params=None, one=False, commit=False):
    """
    Executes a parameterized SQL query safely and cleans up resources.
    
    :param query: SQL query string with %s placeholders
    :param params: Tuple or list of parameters to substitute
    :param one: If True, returns a single dictionary record
    :param commit: If True, commits the transaction and returns lastrowid (or rowcount)
    :return: List of dicts, single dict, lastrowid, or None
    """
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            return last_id if last_id else row_count
        
        if one:
            return cursor.fetchone()
        return cursor.fetchall()
    except Error as e:
        print(f"[SQL Execution Error]: {e}")
        if commit and conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def check_db_health():
    """Quick ping check for server startup health."""
    conn = get_db_connection()
    if conn:
        conn.close()
        return True
    return False
