"""
FarmDirect – Farmer-to-Consumer Agricultural Marketplace
Academic College Mini-Project Web Application
Technology Stack: Python 3.13, Flask, MySQL 8.0, Bootstrap 5, Jinja2
"""

from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from utils.db import query_db, get_db_connection, check_db_health
from utils.decorators import login_required, role_required
from utils.images import (
    allowed_file, 
    save_uploaded_image, 
    remove_uploaded_file, 
    get_product_image_url, 
    get_user_avatar_url
)

app = Flask(__name__)
app.config.from_object(Config)

# --------------------------------------------------------------------------
# Password and Authentication Helpers
# --------------------------------------------------------------------------
def verify_user_password(stored_hash, password):
    """
    Verifies user password.
    Supports Werkzeug hashed passwords for newly registered users,
    as well as fallback for mock hashes in synthetic seed dataset.
    """
    if not stored_hash or not password:
        return False
    
    # 1. Standard Werkzeug hash check
    try:
        if check_password_hash(stored_hash, password):
            return True
    except Exception:
        pass
    
    # 2. Seed dataset demo placeholder hash support (e.g. '$2y$10$demoFarmHash001')
    if stored_hash.startswith('$2y$10$demo') or 'demo' in stored_hash.lower():
        # Allow standard demo password 'password123' or 'admin123' or 'demo123'
        if password in ['password123', 'admin123', 'demo123', '123456', 'password']:
            return True
        
    # 3. Plaintext fallback (if direct demo records exist in database)
    if stored_hash == password:
        return True
        
    return False


# --------------------------------------------------------------------------
# Global Template Context Processors & Filters
# --------------------------------------------------------------------------
@app.context_processor
def inject_global_context():
    """Injects useful variables and image helpers into all Jinja2 templates."""
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    return {
        'today': date.today().strftime('%Y-%m-%d'),
        'current_year': datetime.now().year,
        'cart_item_count': cart_count,
        'get_product_image_url': get_product_image_url,
        'get_user_avatar_url': get_user_avatar_url
    }


# ==========================================================================
# PUBLIC & COMMON ROUTES
# ==========================================================================

@app.route('/')
def index():
    """
    Homepage: showcases featured fresh agricultural products.
    RULE: Customers only see products where BOTH:
    1. Farmer verification_status = 'verified'
    2. Product approval_status = 'approved'
    """
    query = """
        SELECT p.product_id, p.product_name, p.description, p.price, p.unit, 
               p.available_quantity, p.image_filename, c.category_name, 
               f.farmer_id, f.farm_name, u.city, u.profile_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE p.product_status = 'available' 
          AND p.approval_status = 'approved'
          AND f.verification_status = 'verified'
        ORDER BY p.product_id DESC
        LIMIT 8;
    """
    featured = query_db(query) or []
    return render_template('index.html', featured_products=featured)


@app.route('/about')
def about():
    """About Page: explains the direct farmer-to-consumer model and technical architecture."""
    return render_template('about.html')


@app.route('/products')
def products():
    """
    Public Marketplace: search, filter by category, and sort agricultural produce.
    RULE: Only verified farmer + approved product combinations are visible to customers.
    """
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    sql = """
        SELECT p.product_id, p.product_name, p.description, p.price, p.unit, 
               p.available_quantity, p.harvest_date, p.product_status, p.approval_status,
               p.image_filename, c.category_id, c.category_name, 
               f.farmer_id, f.farm_name, u.city, u.profile_image,
               (SELECT AVG(r.rating) FROM reviews r WHERE r.product_id = p.product_id) AS avg_rating
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE p.product_status = 'available' 
          AND p.approval_status = 'approved'
          AND f.verification_status = 'verified'
    """
    params = []

    if search_query:
        sql += " AND (p.product_name LIKE %s OR p.description LIKE %s OR f.farm_name LIKE %s)"
        like_str = f"%{search_query}%"
        params.extend([like_str, like_str, like_str])

    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)

    if sort_by == 'price_low':
        sql += " ORDER BY p.price ASC"
    elif sort_by == 'price_high':
        sql += " ORDER BY p.price DESC"
    else:
        sql += " ORDER BY p.product_id DESC"

    prods = query_db(sql, tuple(params)) or []
    categories_list = query_db("SELECT * FROM categories ORDER BY category_name ASC;") or []

    return render_template('products.html', products=prods, categories=categories_list)


@app.route('/product/<int:product_id>')
def product_details(product_id):
    """
    Detailed view for a single agricultural product.
    Customers can only view products if farmer is verified and product is approved.
    Displays product image, farm provenance, and farmer profile photo.
    """
    prod_query = """
        SELECT p.product_id, p.farmer_id, p.product_name, p.description, p.price, p.unit, 
               p.available_quantity, p.harvest_date, p.product_status, p.approval_status,
               p.image_filename, c.category_id, c.category_name,
               f.farm_name, f.farm_address, f.farming_type, f.verification_status,
               u.full_name AS farmer_name, u.city, u.state, u.profile_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE p.product_id = %s;
    """
    product = query_db(prod_query, (product_id,), one=True)
    if not product:
        flash('Agricultural product not found.', 'danger')
        return redirect(url_for('products'))

    # Check customer access rule:
    # If not verified farmer OR not approved product, only the owner farmer or admin can view
    current_user_id = session.get('user_id')
    current_role = session.get('role')
    is_owner = (current_role == 'farmer' and current_user_id == product['farmer_id'])
    is_admin = (current_role == 'admin')

    if not (is_owner or is_admin):
        if product['verification_status'] != 'verified' or product['approval_status'] != 'approved' or product['product_status'] != 'available':
            flash('This agricultural product is currently not available for purchase on the marketplace.', 'warning')
            return redirect(url_for('products'))

    # Fetch verified reviews for this product
    reviews_query = """
        SELECT r.review_id, r.order_id, r.rating, r.review_text, r.review_date,
               u.full_name AS customer_name, u.profile_image AS customer_profile_image
        FROM reviews r
        JOIN customers c ON r.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE r.product_id = %s
        ORDER BY r.review_id DESC;
    """
    reviews = query_db(reviews_query, (product_id,)) or []

    # Calculate average rating
    avg_rating = 0.0
    if reviews:
        avg_rating = sum(r['rating'] for r in reviews) / len(reviews)

    return render_template('product_details.html', product=product, reviews=reviews, avg_rating=avg_rating)


# ==========================================================================
# AUTHENTICATION: LOGIN, REGISTER, LOGOUT, PROFILE PHOTO
# ==========================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticates users and routes them to their role-specific dashboard."""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'farmer':
            return redirect(url_for('farmer_dashboard'))
        elif role == 'customer':
            return redirect(url_for('customer_dashboard'))
        elif role == 'delivery_partner':
            return redirect(url_for('delivery_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html')

        user = query_db("SELECT * FROM users WHERE email = %s;", (email,), one=True)

        if user and verify_user_password(user['password_hash'], password):
            # Establish session
            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['phone'] = user['phone']
            session['role'] = user['role']
            session['city'] = user['city']
            session['state'] = user['state']
            session['profile_image'] = user.get('profile_image')

            # Initialize empty cart for customer
            if user['role'] == 'customer' and 'cart' not in session:
                session['cart'] = {}

            flash(f"Welcome back, {user['full_name']}!", 'success')

            # Role-based dashboard redirect
            if user['role'] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user['role'] == 'customer':
                next_url = request.args.get('next')
                return redirect(next_url or url_for('customer_dashboard'))
            elif user['role'] == 'delivery_partner':
                return redirect(url_for('delivery_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registrations for Customers and Farmers."""
    if request.method == 'POST':
        role = request.form.get('role', 'customer').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Optional profile photo on registration
        profile_file = request.files.get('profile_image')
        profile_image_path = None
        if profile_file and profile_file.filename != '':
            target_folder = Config.UPLOAD_FOLDER_FARMERS if role == 'farmer' else Config.UPLOAD_FOLDER_CUSTOMERS
            saved_ok, res = save_uploaded_image(profile_file, target_folder, prefix=role[:4])
            if saved_ok:
                profile_image_path = res
            else:
                flash(res, 'warning')

        # Validation
        if not full_name or not email or not phone or not password or not city or not state:
            flash('All required fields must be completed.', 'warning')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
            return render_template('register.html')

        # Check duplicate email or phone
        existing_email = query_db("SELECT user_id FROM users WHERE email = %s;", (email,), one=True)
        if existing_email:
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        existing_phone = query_db("SELECT user_id FROM users WHERE phone = %s;", (phone,), one=True)
        if existing_phone:
            flash('An account with this phone number already exists.', 'danger')
            return render_template('register.html')

        # Secure password hashing
        pwd_hash = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please check MySQL server status.', 'danger')
            return render_template('register.html')

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            # Insert into users table
            insert_user_sql = """
                INSERT INTO users (full_name, email, phone, password_hash, role, city, state, profile_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_user_sql, (full_name, email, phone, pwd_hash, role, city, state, profile_image_path))
            user_id = cursor.lastrowid

            if role == 'customer':
                delivery_address = request.form.get('delivery_address', f"{city}, {state}").strip()
                pincode = request.form.get('pincode', '600001').strip()
                cursor.execute("""
                    INSERT INTO customers (customer_id, delivery_address, pincode)
                    VALUES (%s, %s, %s);
                """, (user_id, delivery_address, pincode))

            elif role == 'farmer':
                farm_name = request.form.get('farm_name', f"{full_name}'s Farm").strip()
                farm_address = request.form.get('farm_address', f"{city}, {state}").strip()
                farming_type = request.form.get('farming_type', 'conventional').strip()
                cursor.execute("""
                    INSERT INTO farmers (farmer_id, farm_name, farm_address, farming_type, verification_status)
                    VALUES (%s, %s, %s, %s, 'pending');
                """, (user_id, farm_name, farm_address, farming_type))

            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            if conn:
                conn.rollback()
            flash(f'Registration error: {str(e)}', 'danger')
            return render_template('register.html')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Clears user session and redirects to login."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/profile/upload-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    """
    Updates or replaces the profile photo for the currently logged-in user.
    Supports Farmer, Customer, Delivery Partner, and Admin roles.
    """
    user_id = session['user_id']
    role = session.get('role', 'customer')

    if 'profile_image' not in request.files:
        flash('No image file selected.', 'warning')
        return redirect(request.referrer or url_for('index'))

    file = request.files['profile_image']
    if not file or file.filename == '':
        flash('Please select an image file to upload.', 'warning')
        return redirect(request.referrer or url_for('index'))

    folder_map = {
        'farmer': Config.UPLOAD_FOLDER_FARMERS,
        'customer': Config.UPLOAD_FOLDER_CUSTOMERS,
        'delivery_partner': Config.UPLOAD_FOLDER_DELIVERY,
        'admin': Config.UPLOAD_FOLDER_ADMIN
    }
    target_folder = folder_map.get(role, Config.UPLOAD_FOLDER_CUSTOMERS)

    success, result = save_uploaded_image(file, target_folder, prefix=role[:4])
    if not success:
        flash(result, 'danger')
        return redirect(request.referrer or url_for('index'))

    # Remove old photo if exists
    old_user = query_db("SELECT profile_image FROM users WHERE user_id = %s;", (user_id,), one=True)
    if old_user and old_user.get('profile_image'):
        remove_uploaded_file(old_user['profile_image'])

    query_db("UPDATE users SET profile_image = %s WHERE user_id = %s;", (result, user_id), commit=True)
    session['profile_image'] = result
    flash('Profile photo updated successfully!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/profile/remove-photo', methods=['POST'])
@login_required
def remove_profile_photo():
    """Removes the custom profile photo and reverts to the role's default avatar."""
    user_id = session['user_id']
    old_user = query_db("SELECT profile_image FROM users WHERE user_id = %s;", (user_id,), one=True)
    if old_user and old_user.get('profile_image'):
        remove_uploaded_file(old_user['profile_image'])
        query_db("UPDATE users SET profile_image = NULL WHERE user_id = %s;", (user_id,), commit=True)
        session['profile_image'] = None
        flash('Profile photo removed. Reverted to default avatar.', 'info')
    else:
        flash('No custom profile photo to remove.', 'info')
    return redirect(request.referrer or url_for('index'))


# ==========================================================================
# FARMER PORTAL
# ==========================================================================

@app.route('/farmer/dashboard')
@role_required('farmer')
def farmer_dashboard():
    """Farmer Dashboard: displays farm stats, approval statuses, and recent crop orders."""
    farmer_id = session['user_id']
    farmer = query_db("""
        SELECT f.*, u.full_name, u.email, u.phone, u.city, u.state, u.profile_image
        FROM farmers f
        JOIN users u ON f.farmer_id = u.user_id
        WHERE f.farmer_id = %s;
    """, (farmer_id,), one=True)
    
    # Farmer stats
    stats_query = """
        SELECT 
            COUNT(p.product_id) AS total_products,
            SUM(CASE WHEN p.approval_status = 'approved' AND p.product_status = 'available' AND p.available_quantity > 0 THEN 1 ELSE 0 END) AS active_products,
            SUM(CASE WHEN p.approval_status = 'pending' THEN 1 ELSE 0 END) AS pending_products,
            SUM(CASE WHEN p.approval_status = 'rejected' THEN 1 ELSE 0 END) AS rejected_products,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COALESCE(SUM(oi.item_total), 0) AS total_revenue
        FROM products p
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        WHERE p.farmer_id = %s;
    """
    stats = query_db(stats_query, (farmer_id,), one=True) or {}

    # Recent orders for this farmer's products
    recent_orders_query = """
        SELECT o.order_id, o.order_date, o.order_status, oi.quantity, oi.unit_price, oi.item_total,
               p.product_name, p.unit, p.image_filename, u.full_name AS customer_name, u.city
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE p.farmer_id = %s
        ORDER BY o.order_id DESC
        LIMIT 5;
    """
    recent_orders = query_db(recent_orders_query, (farmer_id,)) or []

    # Recent products with approval status
    recent_products = query_db("""
        SELECT p.*, c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.farmer_id = %s
        ORDER BY p.product_id DESC
        LIMIT 5;
    """, (farmer_id,)) or []

    return render_template('farmer/dashboard.html', farmer=farmer, stats=stats, recent_orders=recent_orders, recent_products=recent_products)


@app.route('/farmer/products')
@role_required('farmer')
def farmer_products():
    """List of all agricultural crops listed by the logged-in farmer with approval status."""
    farmer_id = session['user_id']
    farmer = query_db("""
        SELECT f.*, u.full_name, u.profile_image
        FROM farmers f
        JOIN users u ON f.farmer_id = u.user_id
        WHERE f.farmer_id = %s;
    """, (farmer_id,), one=True)
    query = """
        SELECT p.*, c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.farmer_id = %s
        ORDER BY p.product_id DESC;
    """
    prods = query_db(query, (farmer_id,)) or []
    return render_template('farmer/products.html', products=prods, farmer=farmer)


@app.route('/farmer/add-product', methods=['GET', 'POST'])
@role_required('farmer')
def farmer_add_product():
    """
    Allows a farmer to add a new agricultural crop.
    RULE: Only VERIFIED farmers can add products. Unverified/rejected farmers are blocked.
    New products start with approval_status = 'pending'.
    Supports image upload with preview.
    """
    farmer_id = session['user_id']
    farmer = query_db("SELECT * FROM farmers WHERE farmer_id = %s;", (farmer_id,), one=True)

    # Enforce verification check
    if not farmer or farmer['verification_status'] != 'verified':
        flash('Your farmer account must be verified by the admin before you can add products.', 'warning')
        return redirect(url_for('farmer_dashboard'))

    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        unit = request.form.get('unit', 'kg')
        price = request.form.get('price')
        available_quantity = request.form.get('available_quantity')
        harvest_date = request.form.get('harvest_date')
        product_status = request.form.get('product_status', 'available')

        # Handle Product Image Upload
        image_filename = None
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename != '':
                saved_ok, res = save_uploaded_image(file, Config.UPLOAD_FOLDER_PRODUCTS, prefix='prod')
                if saved_ok:
                    image_filename = res
                else:
                    flash(res, 'danger')
                    categories = query_db("SELECT * FROM categories ORDER BY category_name;") or []
                    return render_template('farmer/add_product.html', categories=categories, farmer=farmer)

        if not product_name or not category_id or not price or not available_quantity or not harvest_date:
            flash('Please fill in all mandatory product fields.', 'warning')
            categories = query_db("SELECT * FROM categories ORDER BY category_name;") or []
            return render_template('farmer/add_product.html', categories=categories, farmer=farmer)

        # Initial approval_status is always 'pending'
        insert_sql = """
            INSERT INTO products (farmer_id, category_id, product_name, description, unit, price, available_quantity, harvest_date, product_status, approval_status, image_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        result = query_db(insert_sql, (farmer_id, category_id, product_name, description, unit, price, available_quantity, harvest_date, product_status, 'pending', image_filename), commit=True)
        if result:
            flash(f"Crop '{product_name}' listed successfully! It is currently Pending Approval by Admin.", 'success')
            return redirect(url_for('farmer_products'))
        else:
            flash('Error adding product. Please check input values.', 'danger')

    categories = query_db("SELECT * FROM categories ORDER BY category_name;") or []
    return render_template('farmer/add_product.html', categories=categories, farmer=farmer)


@app.route('/farmer/edit-product/<int:product_id>', methods=['GET', 'POST'])
@role_required('farmer')
def farmer_edit_product(product_id):
    """Allows a farmer to edit their own listed product, including replacing/removing the image."""
    farmer_id = session['user_id']
    product = query_db("SELECT * FROM products WHERE product_id = %s AND farmer_id = %s;", (product_id, farmer_id), one=True)
    if not product:
        flash('Product not found or unauthorized.', 'danger')
        return redirect(url_for('farmer_products'))

    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        unit = request.form.get('unit', 'kg')
        price = request.form.get('price')
        available_quantity = request.form.get('available_quantity')
        harvest_date = request.form.get('harvest_date')
        product_status = request.form.get('product_status', 'available')
        remove_image_flag = request.form.get('remove_image') == '1'

        image_filename = product.get('image_filename')

        # Check if new image uploaded
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename != '':
                saved_ok, res = save_uploaded_image(file, Config.UPLOAD_FOLDER_PRODUCTS, prefix='prod')
                if saved_ok:
                    # Remove previous file if exists
                    if image_filename:
                        remove_uploaded_file(image_filename)
                    image_filename = res
                else:
                    flash(res, 'danger')
                    categories = query_db("SELECT * FROM categories ORDER BY category_name;") or []
                    return render_template('farmer/edit_product.html', product=product, categories=categories)
        
        # Handle remove image request if no new image was uploaded
        if remove_image_flag and not ('product_image' in request.files and request.files['product_image'].filename != ''):
            if image_filename:
                remove_uploaded_file(image_filename)
            image_filename = None

        update_sql = """
            UPDATE products 
            SET product_name = %s, category_id = %s, description = %s, unit = %s, 
                price = %s, available_quantity = %s, harvest_date = %s, product_status = %s,
                image_filename = %s
            WHERE product_id = %s AND farmer_id = %s;
        """
        query_db(update_sql, (product_name, category_id, description, unit, price, available_quantity, harvest_date, product_status, image_filename, product_id, farmer_id), commit=True)
        flash(f"Product '{product_name}' updated successfully.", 'success')
        return redirect(url_for('farmer_products'))

    categories = query_db("SELECT * FROM categories ORDER BY category_name;") or []
    return render_template('farmer/edit_product.html', product=product, categories=categories)


@app.route('/farmer/deactivate-product/<int:product_id>')
@role_required('farmer')
def farmer_deactivate_product(product_id):
    """Deactivates a product so it is hidden from the marketplace."""
    farmer_id = session['user_id']
    query_db("UPDATE products SET product_status = 'inactive' WHERE product_id = %s AND farmer_id = %s;", (product_id, farmer_id), commit=True)
    flash('Product has been deactivated from marketplace.', 'info')
    return redirect(url_for('farmer_products'))


@app.route('/farmer/activate-product/<int:product_id>')
@role_required('farmer')
def farmer_activate_product(product_id):
    """Reactivates a product on the marketplace."""
    farmer_id = session['user_id']
    query_db("UPDATE products SET product_status = 'available' WHERE product_id = %s AND farmer_id = %s;", (product_id, farmer_id), commit=True)
    flash('Product is now active on the marketplace.', 'success')
    return redirect(url_for('farmer_products'))


@app.route('/farmer/orders')
@role_required('farmer')
def farmer_orders():
    """All customer orders containing produce from the logged-in farmer."""
    farmer_id = session['user_id']
    query = """
        SELECT o.order_id, o.order_date, o.order_status, o.payment_method, o.payment_status,
               o.delivery_address, o.pincode,
               oi.quantity, oi.unit_price, oi.item_total,
               p.product_name, p.unit, p.image_filename,
               u.full_name AS customer_name, u.profile_image AS customer_profile_image
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE p.farmer_id = %s
        ORDER BY o.order_id DESC;
    """
    orders_list = query_db(query, (farmer_id,)) or []
    return render_template('farmer/orders.html', orders=orders_list)


# ==========================================================================
# CUSTOMER PORTAL & SHOPPING CART
# ==========================================================================

@app.route('/customer/dashboard')
@role_required('customer')
def customer_dashboard():
    """Customer Dashboard: overview of recent orders, active shipments, and quick profile stats."""
    customer_id = session['user_id']
    customer = query_db("""
        SELECT c.*, u.full_name, u.email, u.phone, u.city, u.state, u.profile_image
        FROM customers c
        JOIN users u ON c.customer_id = u.user_id
        WHERE c.customer_id = %s;
    """, (customer_id,), one=True) or {}

    stats_query = """
        SELECT 
            COUNT(*) AS total_orders,
            SUM(CASE WHEN order_status IN ('placed', 'confirmed', 'packed', 'out_for_delivery') THEN 1 ELSE 0 END) AS active_orders,
            SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END) AS completed_orders,
            COALESCE(SUM(total_amount), 0) AS total_spent
        FROM orders
        WHERE customer_id = %s;
    """
    stats = query_db(stats_query, (customer_id,), one=True) or {}

    recent_orders_query = """
        SELECT o.*,
               (SELECT COUNT(*) FROM order_items WHERE order_id = o.order_id) AS items_count
        FROM orders o
        WHERE o.customer_id = %s
        ORDER BY o.order_id DESC
        LIMIT 5;
    """
    recent_orders = query_db(recent_orders_query, (customer_id,)) or []

    return render_template('customer/dashboard.html', customer=customer, stats=stats, recent_orders=recent_orders)


@app.route('/customer/cart')
@role_required('customer')
def cart():
    """Displays the customer's current shopping cart."""
    cart_data = session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0.00')

    if cart_data:
        prod_ids = tuple(int(k) for k in cart_data.keys())
        if len(prod_ids) == 1:
            format_strings = '(%s)'
        else:
            format_strings = str(tuple(prod_ids))

        sql = f"""
            SELECT p.product_id, p.product_name, p.price, p.unit, p.available_quantity,
                   p.image_filename, c.category_name, f.farm_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN farmers f ON p.farmer_id = f.farmer_id
            WHERE p.product_id IN {format_strings};
        """
        prods = query_db(sql, prod_ids if len(prod_ids) == 1 else None) or []
        for p in prods:
            qty = Decimal(str(cart_data.get(str(p['product_id']), 1)))
            item_total = p['price'] * qty
            subtotal += item_total
            cart_items.append({
                'product': p,
                'quantity': qty,
                'item_total': item_total
            })

    delivery_fee = Decimal(str(Config.DELIVERY_FEE)) if cart_items else Decimal('0.00')
    grand_total = subtotal + delivery_fee

    return render_template('customer/cart.html', cart_items=cart_items, subtotal=subtotal, delivery_fee=delivery_fee, grand_total=grand_total)


@app.route('/customer/cart/add/<int:product_id>', methods=['POST'])
@role_required('customer')
def add_to_cart(product_id):
    """
    Adds a specified quantity of a product to the customer's session cart.
    RULE: Validates that farmer is verified and product is approved.
    """
    qty = float(request.form.get('quantity', 1))
    if qty <= 0:
        qty = 1.0

    # Ensure product is approved & farmer verified
    check_sql = """
        SELECT p.product_id, p.available_quantity, p.product_name, p.approval_status, f.verification_status
        FROM products p
        JOIN farmers f ON p.farmer_id = f.farmer_id
        WHERE p.product_id = %s AND p.product_status = 'available';
    """
    prod = query_db(check_sql, (product_id,), one=True)
    if not prod or prod['approval_status'] != 'approved' or prod['verification_status'] != 'verified':
        flash('This product is not currently available for ordering.', 'warning')
        return redirect(request.referrer or url_for('products'))

    if prod['available_quantity'] < qty:
        flash(f"Only {prod['available_quantity']} units of '{prod['product_name']}' available in stock.", 'warning')
        return redirect(request.referrer or url_for('product_details', product_id=product_id))

    cart_dict = session.get('cart', {})
    current_qty = cart_dict.get(str(product_id), 0)
    cart_dict[str(product_id)] = current_qty + qty
    session['cart'] = cart_dict
    session.modified = True

    flash(f"Added {qty} units of '{prod['product_name']}' to your cart.", 'success')
    return redirect(request.referrer or url_for('cart'))


@app.route('/customer/cart/update', methods=['POST'])
@role_required('customer')
def update_cart():
    """Updates the quantities of items in the shopping cart."""
    cart_dict = {}
    for key, val in request.form.items():
        if key.startswith('quantity_'):
            prod_id = key.replace('quantity_', '')
            try:
                qty = float(val)
                if qty > 0:
                    cart_dict[prod_id] = qty
            except ValueError:
                continue

    session['cart'] = cart_dict
    session.modified = True
    flash('Shopping cart updated.', 'info')
    return redirect(url_for('cart'))


@app.route('/customer/cart/remove/<int:product_id>')
@role_required('customer')
def remove_from_cart(product_id):
    """Removes a specific product from the session cart."""
    cart_dict = session.get('cart', {})
    if str(product_id) in cart_dict:
        del cart_dict[str(product_id)]
        session['cart'] = cart_dict
        session.modified = True
        flash('Item removed from your cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/customer/checkout', methods=['GET'])
@role_required('customer')
def checkout():
    """Checkout Page: review order summary and confirm delivery address."""
    cart_data = session.get('cart', {})
    if not cart_data:
        flash('Your cart is empty. Please add items to proceed.', 'warning')
        return redirect(url_for('products'))

    customer_id = session['user_id']
    customer = query_db("""
        SELECT c.*, u.full_name, u.email, u.phone, u.city, u.state
        FROM customers c
        JOIN users u ON c.customer_id = u.user_id
        WHERE c.customer_id = %s;
    """, (customer_id,), one=True)

    # Calculate totals
    prod_ids = tuple(int(k) for k in cart_data.keys())
    format_strings = '(%s)' if len(prod_ids) == 1 else str(tuple(prod_ids))
    sql = f"SELECT product_id, product_name, price, unit, image_filename FROM products WHERE product_id IN {format_strings};"
    prods = query_db(sql, prod_ids if len(prod_ids) == 1 else None) or []

    subtotal = Decimal('0.00')
    checkout_items = []
    for p in prods:
        qty = Decimal(str(cart_data.get(str(p['product_id']), 1)))
        item_total = p['price'] * qty
        subtotal += item_total
        checkout_items.append({'product': p, 'quantity': qty, 'item_total': item_total})

    delivery_fee = Decimal(str(Config.DELIVERY_FEE))
    grand_total = subtotal + delivery_fee

    return render_template('customer/checkout.html', customer=customer, checkout_items=checkout_items, subtotal=subtotal, delivery_fee=delivery_fee, grand_total=grand_total)


@app.route('/customer/place-order', methods=['POST'])
@role_required('customer')
def place_order():
    """Creates the order, order items, delivery assignment, and updates stock quantities."""
    cart_data = session.get('cart', {})
    if not cart_data:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products'))

    customer_id = session['user_id']
    delivery_address = request.form.get('delivery_address', '').strip()
    pincode = request.form.get('pincode', '').strip()
    payment_method = request.form.get('payment_method', 'cod')

    if not delivery_address or not pincode:
        flash('Please provide a complete delivery address and pincode.', 'warning')
        return redirect(url_for('checkout'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'danger')
        return redirect(url_for('checkout'))

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1. Fetch & lock product details, check stock and approval
        prod_ids = tuple(int(k) for k in cart_data.keys())
        format_strings = '(%s)' if len(prod_ids) == 1 else str(tuple(prod_ids))
        cursor.execute(f"""
            SELECT p.product_id, p.product_name, p.price, p.available_quantity, p.approval_status, f.verification_status
            FROM products p
            JOIN farmers f ON p.farmer_id = f.farmer_id
            WHERE p.product_id IN {format_strings} FOR UPDATE;
        """, prod_ids if len(prod_ids) == 1 else ())
        products_db = cursor.fetchall()

        subtotal = Decimal('0.00')
        order_items_data = []

        for p in products_db:
            pid = str(p['product_id'])
            qty_needed = Decimal(str(cart_data.get(pid, 1)))

            # Verification and approval check
            if p['approval_status'] != 'approved' or p['verification_status'] != 'verified':
                conn.rollback()
                flash(f"Crop '{p['product_name']}' is no longer approved for sale.", 'danger')
                return redirect(url_for('cart'))

            if p['available_quantity'] < qty_needed:
                conn.rollback()
                flash(f"Insufficient stock for '{p['product_name']}'. Only {p['available_quantity']} available.", 'danger')
                return redirect(url_for('cart'))

            item_total = p['price'] * qty_needed
            subtotal += item_total
            order_items_data.append((p['product_id'], qty_needed, p['price'], item_total))

        delivery_fee = Decimal(str(Config.DELIVERY_FEE))
        total_amount = subtotal + delivery_fee

        # Determine payment status and demo transaction ID (Demo Payment System)
        if payment_method in ['upi', 'card']:
            payment_status = 'paid'
            if payment_method == 'upi':
                transaction_id = f"DEMO-UPI-{int(datetime.now().timestamp())}"
            else:
                transaction_id = f"DEMO-CARD-{int(datetime.now().timestamp())}"
        else:
            payment_method = 'cod'
            payment_status = 'pending'
            transaction_id = None

        # 2. Insert into orders table (with transaction_id fallback)
        try:
            insert_order_sql = """
                INSERT INTO orders (customer_id, order_date, delivery_address, pincode, subtotal, delivery_fee, total_amount, payment_method, payment_status, transaction_id, order_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'placed');
            """
            cursor.execute(insert_order_sql, (customer_id, now_str, delivery_address, pincode, subtotal, delivery_fee, total_amount, payment_method, payment_status, transaction_id))
        except Exception:
            insert_order_sql = """
                INSERT INTO orders (customer_id, order_date, delivery_address, pincode, subtotal, delivery_fee, total_amount, payment_method, payment_status, order_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'placed');
            """
            cursor.execute(insert_order_sql, (customer_id, now_str, delivery_address, pincode, subtotal, delivery_fee, total_amount, payment_method, payment_status))
        order_id = cursor.lastrowid

        # 3. Insert into order_items and decrement product stock
        for prod_id, qty, unit_price, item_tot in order_items_data:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, item_total)
                VALUES (%s, %s, %s, %s, %s);
            """, (order_id, prod_id, qty, unit_price, item_tot))

            cursor.execute("""
                UPDATE products
                SET available_quantity = available_quantity - %s,
                    product_status = CASE WHEN available_quantity - %s <= 0 THEN 'out_of_stock' ELSE product_status END
                WHERE product_id = %s;
            """, (qty, qty, prod_id))

        # 4. Assign an available delivery partner
        cursor.execute("SELECT delivery_partner_id FROM delivery_partners WHERE availability_status = 'available' LIMIT 1;")
        partner = cursor.fetchone()
        delivery_partner_id = partner['delivery_partner_id'] if partner else 21  # Fallback to seed delivery partner

        cursor.execute("""
            INSERT INTO deliveries (order_id, delivery_partner_id, pickup_status, delivery_status, assigned_at)
            VALUES (%s, %s, 'pending', 'assigned', %s);
        """, (order_id, delivery_partner_id, now_str))

        conn.commit()

        # Clear cart
        session['cart'] = {}
        session.modified = True

        if payment_method == 'upi':
            flash(f"Order #{order_id} placed successfully! Demo UPI payment verified ({transaction_id}).", 'success')
        elif payment_method == 'card':
            flash(f"Order #{order_id} placed successfully! Demo card payment approved ({transaction_id}).", 'success')
        else:
            flash(f"Order #{order_id} placed successfully via Cash on Delivery!", 'success')

        return redirect(url_for('customer_order_details', order_id=order_id))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error placing order: {str(e)}", 'danger')
        return redirect(url_for('checkout'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/customer/orders')
@role_required('customer')
def customer_orders():
    """Displays customer order history with status badges."""
    customer_id = session['user_id']
    query = """
        SELECT o.*, 
               (SELECT COUNT(*) FROM order_items WHERE order_id = o.order_id) AS items_count,
               d.delivery_status
        FROM orders o
        LEFT JOIN deliveries d ON o.order_id = d.order_id
        WHERE o.customer_id = %s
        ORDER BY o.order_id DESC;
    """
    orders_list = query_db(query, (customer_id,)) or []
    return render_template('customer/orders.html', orders=orders_list)


@app.route('/customer/order/<int:order_id>')
@role_required('customer')
def customer_order_details(order_id):
    """Detailed invoice and tracking view for a specific customer order."""
    customer_id = session['user_id']
    order = query_db("""
        SELECT o.*, d.delivery_status, d.assigned_at, d.delivered_at,
               u.full_name AS delivery_partner_name, u.phone AS delivery_partner_phone
        FROM orders o
        LEFT JOIN deliveries d ON o.order_id = d.order_id
        LEFT JOIN delivery_partners dp ON d.delivery_partner_id = dp.delivery_partner_id
        LEFT JOIN users u ON dp.delivery_partner_id = u.user_id
        WHERE o.order_id = %s AND o.customer_id = %s;
    """, (order_id, customer_id), one=True)

    if not order:
        flash('Order not found or unauthorized.', 'danger')
        return redirect(url_for('customer_orders'))

    items_query = """
        SELECT oi.*, p.product_name, p.unit, p.image_filename, f.farm_name, u.full_name AS farmer_name,
               (SELECT review_id FROM reviews WHERE order_id = oi.order_id AND product_id = oi.product_id AND customer_id = %s) AS existing_review_id
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE oi.order_id = %s;
    """
    items = query_db(items_query, (customer_id, order_id)) or []

    return render_template('customer/order_details.html', order=order, items=items)


@app.route('/customer/review/<int:order_id>/<int:product_id>', methods=['GET', 'POST'])
@role_required('customer')
def submit_review(order_id, product_id):
    """Allows customers to rate and review agricultural produce after delivery."""
    customer_id = session['user_id']
    
    # Check that order was delivered
    order = query_db("SELECT * FROM orders WHERE order_id = %s AND customer_id = %s AND order_status = 'delivered';", (order_id, customer_id), one=True)
    if not order:
        flash('Reviews can only be submitted for delivered orders.', 'warning')
        return redirect(url_for('customer_orders'))

    product = query_db("SELECT * FROM products WHERE product_id = %s;", (product_id,), one=True)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('customer_orders'))

    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        review_text = request.form.get('review_text', '').strip()
        review_date = date.today().strftime('%Y-%m-%d')

        # Check existing review
        existing = query_db("SELECT review_id FROM reviews WHERE order_id = %s AND customer_id = %s AND product_id = %s;", (order_id, customer_id, product_id), one=True)
        if existing:
            query_db("UPDATE reviews SET rating = %s, review_text = %s, review_date = %s WHERE review_id = %s;", (rating, review_text, review_date, existing['review_id']), commit=True)
            flash('Your review has been updated.', 'success')
        else:
            query_db("INSERT INTO reviews (order_id, customer_id, product_id, rating, review_text, review_date) VALUES (%s, %s, %s, %s, %s, %s);", (order_id, customer_id, product_id, rating, review_text, review_date), commit=True)
            flash('Thank you for rating this produce!', 'success')
        return redirect(url_for('customer_order_details', order_id=order_id))

    return render_template('customer/review.html', order_id=order_id, product=product)


@app.route('/customer/complaint', methods=['GET', 'POST'])
@role_required('customer')
def submit_complaint():
    """Allows customers to submit issues regarding deliveries, quality, or payments."""
    customer_id = session['user_id']
    selected_order_id = request.args.get('order_id', '')

    if request.method == 'POST':
        order_id_val = request.form.get('order_id') or None
        complaint_type = request.form.get('complaint_type', 'other')
        description = request.form.get('description', '').strip()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not description:
            flash('Please describe your issue.', 'warning')
        else:
            query = """
                INSERT INTO complaints (customer_id, order_id, complaint_type, description, complaint_status, created_at)
                VALUES (%s, %s, %s, %s, 'open', %s);
            """
            query_db(query, (customer_id, order_id_val, complaint_type, description, created_at), commit=True)
            flash('Your complaint has been submitted to the admin team.', 'success')
            return redirect(url_for('submit_complaint'))

    user_orders = query_db("SELECT order_id, total_amount, order_status FROM orders WHERE customer_id = %s ORDER BY order_id DESC;", (customer_id,)) or []
    complaints = query_db("SELECT * FROM complaints WHERE customer_id = %s ORDER BY complaint_id DESC;", (customer_id,)) or []

    return render_template('customer/complaint.html', user_orders=user_orders, complaints=complaints, selected_order_id=selected_order_id)


# ==========================================================================
# DELIVERY PARTNER PORTAL
# ==========================================================================

@app.route('/delivery/dashboard')
@role_required('delivery_partner')
def delivery_dashboard():
    """Delivery Partner Dashboard: view assigned shipments and update delivery status."""
    partner_id = session['user_id']
    partner = query_db("""
        SELECT dp.*, u.full_name, u.phone, u.city, u.state, u.profile_image
        FROM delivery_partners dp
        JOIN users u ON dp.delivery_partner_id = u.user_id
        WHERE dp.delivery_partner_id = %s;
    """, (partner_id,), one=True) or {}

    stats_query = """
        SELECT 
            SUM(CASE WHEN delivery_status = 'assigned' THEN 1 ELSE 0 END) AS assigned_count,
            SUM(CASE WHEN delivery_status IN ('picked_up', 'out_for_delivery') THEN 1 ELSE 0 END) AS transit_count,
            SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_count
        FROM deliveries
        WHERE delivery_partner_id = %s;
    """
    stats = query_db(stats_query, (partner_id,), one=True) or {}

    deliveries_query = """
        SELECT d.*, o.order_date, o.delivery_address, o.pincode, o.total_amount, o.payment_method, o.payment_status,
               u.full_name AS customer_name, u.phone AS customer_phone, u.profile_image AS customer_profile_image
        FROM deliveries d
        JOIN orders o ON d.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
        WHERE d.delivery_partner_id = %s
        ORDER BY d.delivery_id DESC;
    """
    deliveries_list = query_db(deliveries_query, (partner_id,)) or []

    return render_template('delivery/dashboard.html', partner=partner, stats=stats, deliveries=deliveries_list)


@app.route('/delivery/update-status/<int:delivery_id>', methods=['POST'])
@role_required('delivery_partner')
def delivery_update_status(delivery_id):
    """Updates shipment progress (assigned -> picked_up -> out_for_delivery -> delivered)."""
    partner_id = session['user_id']
    new_status = request.form.get('delivery_status')

    delivery = query_db("SELECT * FROM deliveries WHERE delivery_id = %s AND delivery_partner_id = %s;", (delivery_id, partner_id), one=True)
    if not delivery:
        flash('Delivery record not found or unauthorized.', 'danger')
        return redirect(url_for('delivery_dashboard'))

    order_id = delivery['order_id']
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('delivery_dashboard'))

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if new_status == 'picked_up':
            cursor.execute("UPDATE deliveries SET pickup_status = 'picked_up', delivery_status = 'picked_up' WHERE delivery_id = %s;", (delivery_id,))
            cursor.execute("UPDATE orders SET order_status = 'packed' WHERE order_id = %s;", (order_id,))

        elif new_status == 'out_for_delivery':
            cursor.execute("UPDATE deliveries SET pickup_status = 'picked_up', delivery_status = 'out_for_delivery' WHERE delivery_id = %s;", (delivery_id,))
            cursor.execute("UPDATE orders SET order_status = 'out_for_delivery' WHERE order_id = %s;", (order_id,))

        elif new_status == 'delivered':
            cursor.execute("UPDATE deliveries SET pickup_status = 'picked_up', delivery_status = 'delivered', delivered_at = %s WHERE delivery_id = %s;", (now_str, delivery_id))
            cursor.execute("UPDATE orders SET order_status = 'delivered', payment_status = 'paid' WHERE order_id = %s;", (order_id,))

        elif new_status == 'failed':
            cursor.execute("UPDATE deliveries SET delivery_status = 'failed' WHERE delivery_id = %s;", (delivery_id,))
            cursor.execute("UPDATE orders SET order_status = 'cancelled' WHERE order_id = %s;", (order_id,))

        conn.commit()
        flash(f"Delivery status updated to '{new_status}'.", 'success')
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error updating status: {str(e)}", 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('delivery_dashboard'))


# ==========================================================================
# ADMIN PORTAL
# ==========================================================================

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    """
    Admin Dashboard: overview stats for Farmers and Products,
    featuring two dedicated sections:
    A. Farmer Verification
    B. Product Approval
    """
    stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT COUNT(*) FROM farmers) AS total_farmers,
            (SELECT COUNT(*) FROM farmers WHERE verification_status = 'pending') AS pending_farmers,
            (SELECT COUNT(*) FROM farmers WHERE verification_status = 'verified') AS verified_farmers,
            (SELECT COUNT(*) FROM farmers WHERE verification_status = 'rejected') AS rejected_farmers,
            (SELECT COUNT(*) FROM customers) AS total_customers,
            (SELECT COUNT(*) FROM products) AS total_products,
            (SELECT COUNT(*) FROM products WHERE approval_status = 'pending') AS pending_products,
            (SELECT COUNT(*) FROM products WHERE approval_status = 'approved') AS approved_products,
            (SELECT COUNT(*) FROM products WHERE approval_status = 'rejected') AS rejected_products,
            (SELECT COUNT(*) FROM orders) AS total_orders,
            (SELECT COUNT(*) FROM complaints WHERE complaint_status IN ('open', 'in_progress')) AS pending_complaints;
    """
    stats = query_db(stats_query, one=True) or {}

    # Section A: Pending Farmer Verifications
    pending_farmers = query_db("""
        SELECT f.farmer_id, f.farm_name, f.farm_address, f.farming_type, f.verification_status,
               u.full_name, u.email, u.phone, u.city, u.state, u.profile_image
        FROM farmers f
        JOIN users u ON f.farmer_id = u.user_id
        WHERE f.verification_status = 'pending'
        ORDER BY f.farmer_id DESC
        LIMIT 6;
    """) or []

    # Section B: Pending Product Approvals
    pending_products = query_db("""
        SELECT p.product_id, p.product_name, p.price, p.unit, p.available_quantity, p.harvest_date, p.approval_status,
               p.image_filename, c.category_name, f.farm_name, u.full_name AS farmer_name, u.profile_image AS farmer_profile_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE p.approval_status = 'pending'
        ORDER BY p.product_id DESC
        LIMIT 6;
    """) or []

    recent_orders = query_db("""
        SELECT o.order_id, o.order_date, o.total_amount, o.order_status, u.full_name AS customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
        ORDER BY o.order_id DESC
        LIMIT 5;
    """) or []

    return render_template('admin/dashboard.html', stats=stats, pending_farmers=pending_farmers, pending_products=pending_products, recent_orders=recent_orders)


@app.route('/admin/users')
@role_required('admin')
def admin_users():
    """User Management: list all users with optional role filtering."""
    role_filter = request.args.get('role', '')
    if role_filter:
        users_list = query_db("SELECT * FROM users WHERE role = %s ORDER BY user_id ASC;", (role_filter,)) or []
    else:
        users_list = query_db("SELECT * FROM users ORDER BY user_id ASC;") or []

    return render_template('admin/users.html', users=users_list)


@app.route('/admin/farmers')
@role_required('admin')
def admin_farmers():
    """Farmer verification and management panel."""
    status_filter = request.args.get('status', '')
    if status_filter:
        farmers_list = query_db("""
            SELECT f.*, u.full_name, u.email, u.phone, u.city, u.state, u.profile_image
            FROM farmers f
            JOIN users u ON f.farmer_id = u.user_id
            WHERE f.verification_status = %s
            ORDER BY f.farmer_id ASC;
        """, (status_filter,)) or []
    else:
        farmers_list = query_db("""
            SELECT f.*, u.full_name, u.email, u.phone, u.city, u.state, u.profile_image
            FROM farmers f
            JOIN users u ON f.farmer_id = u.user_id
            ORDER BY f.farmer_id ASC;
        """) or []

    return render_template('admin/farmers.html', farmers=farmers_list)


@app.route('/admin/verify-farmer/<int:farmer_id>', methods=['POST'])
@role_required('admin')
def admin_verify_farmer(farmer_id):
    """Verifies a farmer account so they can add products and sell on marketplace."""
    query_db("UPDATE farmers SET verification_status = 'verified' WHERE farmer_id = %s;", (farmer_id,), commit=True)
    flash(f'Farmer #{farmer_id} has been verified successfully. They can now list produce.', 'success')
    return redirect(request.referrer or url_for('admin_farmers'))


@app.route('/admin/reject-farmer/<int:farmer_id>', methods=['POST'])
@role_required('admin')
def admin_reject_farmer(farmer_id):
    """Rejects a farmer account verification."""
    query_db("UPDATE farmers SET verification_status = 'rejected' WHERE farmer_id = %s;", (farmer_id,), commit=True)
    flash(f'Farmer #{farmer_id} verification has been rejected.', 'warning')
    return redirect(request.referrer or url_for('admin_farmers'))


@app.route('/admin/products')
@role_required('admin')
def admin_products():
    """
    Product approval and marketplace monitoring panel.
    Allows admin to inspect produce image, farmer photo, and approve/reject products.
    """
    approval_filter = request.args.get('approval', '')
    status_filter = request.args.get('status', '')

    sql = """
        SELECT p.*, c.category_name, f.farm_name, f.verification_status AS farmer_verification, 
               u.full_name AS farmer_name, u.profile_image AS farmer_profile_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN farmers f ON p.farmer_id = f.farmer_id
        JOIN users u ON f.farmer_id = u.user_id
        WHERE 1=1
    """
    params = []

    if approval_filter:
        sql += " AND p.approval_status = %s"
        params.append(approval_filter)

    if status_filter:
        sql += " AND p.product_status = %s"
        params.append(status_filter)

    sql += " ORDER BY p.product_id DESC;"

    products_list = query_db(sql, tuple(params)) or []
    return render_template('admin/products.html', products=products_list)


@app.route('/admin/approve-product/<int:product_id>', methods=['POST'])
@role_required('admin')
def admin_approve_product(product_id):
    """Approves a farmer's crop listing so customers can purchase it."""
    query_db("UPDATE products SET approval_status = 'approved' WHERE product_id = %s;", (product_id,), commit=True)
    flash(f'Product #{product_id} has been Approved for marketplace sale.', 'success')
    return redirect(request.referrer or url_for('admin_products'))


@app.route('/admin/reject-product/<int:product_id>', methods=['POST'])
@role_required('admin')
def admin_reject_product(product_id):
    """Rejects a farmer's crop listing."""
    query_db("UPDATE products SET approval_status = 'rejected' WHERE product_id = %s;", (product_id,), commit=True)
    flash(f'Product #{product_id} has been Rejected.', 'warning')
    return redirect(request.referrer or url_for('admin_products'))


@app.route('/admin/toggle-product/<int:product_id>', methods=['POST'])
@role_required('admin')
def admin_toggle_product(product_id):
    """Toggles product availability status between available and inactive."""
    prod = query_db("SELECT product_status FROM products WHERE product_id = %s;", (product_id,), one=True)
    if prod:
        new_status = 'inactive' if prod['product_status'] == 'available' else 'available'
        query_db("UPDATE products SET product_status = %s WHERE product_id = %s;", (new_status, product_id), commit=True)
        flash(f"Product status updated to '{new_status}'.", 'info')
    return redirect(request.referrer or url_for('admin_products'))


@app.route('/admin/orders')
@role_required('admin')
def admin_orders():
    """Platform-wide order management."""
    status_filter = request.args.get('status', '')
    sql = """
        SELECT o.*, u.full_name AS customer_name,
               (SELECT u2.full_name FROM deliveries d JOIN delivery_partners dp ON d.delivery_partner_id = dp.delivery_partner_id JOIN users u2 ON dp.delivery_partner_id = u2.user_id WHERE d.order_id = o.order_id) AS delivery_partner_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
    """
    params = []
    if status_filter:
        sql += " WHERE o.order_status = %s"
        params.append(status_filter)
    sql += " ORDER BY o.order_id DESC;"

    orders_list = query_db(sql, tuple(params)) or []
    return render_template('admin/orders.html', orders=orders_list)


@app.route('/admin/complaints')
@role_required('admin')
def admin_complaints():
    """Complaints resolution panel."""
    status_filter = request.args.get('status', '')
    sql = """
        SELECT cmp.*, u.full_name AS customer_name, u.email AS customer_email, u.phone AS customer_phone
        FROM complaints cmp
        JOIN customers c ON cmp.customer_id = c.customer_id
        JOIN users u ON c.customer_id = u.user_id
    """
    params = []
    if status_filter:
        sql += " WHERE cmp.complaint_status = %s"
        params.append(status_filter)
    sql += " ORDER BY cmp.complaint_id DESC;"

    complaints_list = query_db(sql, tuple(params)) or []
    return render_template('admin/complaints.html', complaints=complaints_list)


@app.route('/admin/update-complaint/<int:complaint_id>', methods=['POST'])
@role_required('admin')
def admin_update_complaint(complaint_id):
    """Updates complaint resolution status."""
    new_status = request.form.get('complaint_status', 'open')
    resolved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status in ['resolved', 'closed'] else None
    
    query = "UPDATE complaints SET complaint_status = %s, resolved_at = %s WHERE complaint_id = %s;"
    query_db(query, (new_status, resolved_at, complaint_id), commit=True)
    flash(f"Complaint #{complaint_id} updated to '{new_status}'.", 'success')
    return redirect(url_for('admin_complaints'))


# ==========================================================================
# CUSTOM ERROR HANDLERS
# ==========================================================================

@app.errorhandler(403)
def forbidden_error(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


# ==========================================================================
# MAIN EXECUTION ENTRYPOINT
# ==========================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  FarmDirect – Farmer-to-Consumer Agricultural Marketplace")
    print("  Local Dev Server: http://127.0.0.1:5000/")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
