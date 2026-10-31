import os
from pathlib import Path

# Load variables from .env if present
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get('SECRET_KEY', 'farmdirect-dev-secret-key-2026')
    
    # Database Settings
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'farmdirect')

    # Fixed delivery fee in INR
    DELIVERY_FEE = 30.00

    # Image Upload Settings (Max 5MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

    # Upload Subdirectories relative to project root
    UPLOAD_FOLDER_PRODUCTS = 'static/uploads/products'
    UPLOAD_FOLDER_PROFILES = 'static/uploads/profiles'
    UPLOAD_FOLDER_FARMERS = 'static/uploads/profiles/farmers'
    UPLOAD_FOLDER_CUSTOMERS = 'static/uploads/profiles/customers'
    UPLOAD_FOLDER_DELIVERY = 'static/uploads/profiles/delivery'
    UPLOAD_FOLDER_ADMIN = 'static/uploads/profiles/admin'
