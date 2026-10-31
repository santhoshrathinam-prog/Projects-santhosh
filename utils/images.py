import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """
    Validates that a filename has an allowed image extension.
    Allowed extensions: jpg, jpeg, png, webp.
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def save_uploaded_image(file_storage, folder_rel_path, prefix='img'):
    """
    Saves an uploaded file to the specified target directory with a unique, secure name.
    
    :param file_storage: Werkzeug FileStorage object from request.files
    :param folder_rel_path: Relative folder path (e.g., 'static/uploads/products')
    :param prefix: Prefix for the unique filename (e.g., 'prod', 'farmer')
    :return: Tuple (success: bool, result_or_error: str)
             If success=True, returns the stored relative web path (e.g., 'uploads/products/prod_123.jpg')
    """
    if not file_storage or file_storage.filename == '':
        return False, "No file selected."

    if not allowed_file(file_storage.filename):
        return False, "Invalid image format. Allowed formats: JPG, JPEG, PNG, WEBP."

    # Validate file size if stream length is available
    file_storage.seek(0, os.SEEK_END)
    file_length = file_storage.tell()
    file_storage.seek(0)
    
    if file_length > Config.MAX_CONTENT_LENGTH:
        return False, "File size exceeds the 5MB maximum limit. Please upload a smaller image."

    # Generate secure, unique filename
    raw_name = secure_filename(file_storage.filename)
    clean_name = raw_name if raw_name else 'image.jpg'
    unique_id = uuid.uuid4().hex[:10]
    final_filename = f"{prefix}_{unique_id}_{clean_name}"

    # Ensure target directory exists
    target_dir = Config.BASE_DIR / folder_rel_path
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / final_filename
    
    try:
        file_storage.save(str(file_path))
        # Return path relative to static/
        # e.g., 'uploads/products/prod_xyz.jpg'
        sub_path = str(Path(folder_rel_path).relative_to('static') / final_filename).replace('\\', '/')
        return True, sub_path
    except Exception as e:
        print(f"[Image Save Error]: {e}")
        return False, f"Failed to save image: {str(e)}"

def remove_uploaded_file(sub_path):
    """
    Safely removes an existing uploaded file from disk when replaced or deleted.
    Only allows deleting files inside static/uploads/.
    """
    if not sub_path:
        return
    try:
        full_path = Config.BASE_DIR / 'static' / sub_path
        # Security check: must reside inside static/uploads/
        uploads_root = (Config.BASE_DIR / 'static' / 'uploads').resolve()
        if uploads_root in full_path.resolve().parents and full_path.exists() and full_path.is_file():
            full_path.unlink()
    except Exception as e:
        print(f"[Image Delete Error]: {e}")

def get_product_image_url(image_filename):
    """Returns the web URL for a product image, or default SVG if none."""
    if image_filename:
        # Check if file exists on disk
        full_path = Config.BASE_DIR / 'static' / image_filename
        if full_path.exists():
            return f"/static/{image_filename}"
    return "/static/images/default_product.svg"

def get_user_avatar_url(profile_image, role='customer'):
    """Returns the web URL for a user profile avatar, or role-based default SVG."""
    if profile_image:
        full_path = Config.BASE_DIR / 'static' / profile_image
        if full_path.exists():
            return f"/static/{profile_image}"
    if role == 'farmer':
        return "/static/images/default_farmer.svg"
    return "/static/images/default_avatar.svg"
