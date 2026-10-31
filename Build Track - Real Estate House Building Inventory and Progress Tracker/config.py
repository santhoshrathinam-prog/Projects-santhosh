import os
from dotenv import load_dotenv

# Load .env file from the current directory or project root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'buildtrack_default_secret_key_2026')
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'sandy24')
    DB_NAME = os.getenv('DB_NAME', 'real_estate_inventory')
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
