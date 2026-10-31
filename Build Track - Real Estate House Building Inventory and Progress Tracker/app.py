import os
import csv
import io
from datetime import datetime, date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, jsonify, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from db import query_db, get_db, init_db

app = Flask(__name__)
app.config.from_object(Config)

# -------------------------------------------------------------------
# Helper Decorators for Role-Based Access Control (RBAC)
# -------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access restricted to Administrators.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def builder_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'builder':
            flash('Access restricted to Builders / Site Engineers.', 'danger')
            return redirect(url_for('builder_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_common_data():
    low_stock_count = 0
    pending_updates_count = 0
    if session.get('role') == 'admin':
        try:
            ls_row = query_db("""
                SELECT COUNT(*) AS cnt FROM materials 
                WHERE available_quantity <= minimum_stock_level;
            """, one=True)
            low_stock_count = ls_row['cnt'] if ls_row else 0

            pu_const = query_db("SELECT COUNT(*) AS cnt FROM construction_updates WHERE status = 'PENDING';", one=True)
            pu_stock = query_db("SELECT COUNT(*) AS cnt FROM stock_updates WHERE status = 'PENDING';", one=True)
            pending_updates_count = (pu_const['cnt'] if pu_const else 0) + (pu_stock['cnt'] if pu_stock else 0)
        except Exception:
            pass
    return {
        'low_stock_badge_count': low_stock_count,
        'pending_updates_badge_count': pending_updates_count,
        'now_year': datetime.now().year
    }

# -------------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'builder':
            return redirect(url_for('builder_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session and session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html', email=email)

        admin = query_db("SELECT * FROM admins WHERE email = %s;", (email,), one=True)
        if admin and check_password_hash(admin['password_hash'], password):
            session.clear()
            session['user_id'] = admin['admin_id']
            session['user_name'] = admin['full_name']
            session['email'] = admin['email']
            session['role'] = 'admin'
            flash(f'Welcome back, {admin["full_name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Please verify email and password.', 'danger')

    return render_template('login.html')

@app.route('/builder/login', methods=['GET', 'POST'])
def builder_login():
    if 'user_id' in session and session.get('role') == 'builder':
        return redirect(url_for('builder_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('builder_login.html', email=email)

        builder = query_db("SELECT * FROM builders WHERE email = %s;", (email,), one=True)
        if builder:
            if builder['status'] != 'Active':
                flash('Your account is currently Inactive. Please contact the Administrator.', 'danger')
                return render_template('builder_login.html', email=email)

            if check_password_hash(builder['password_hash'], password):
                session.clear()
                session['user_id'] = builder['builder_id']
                session['user_name'] = builder['builder_name']
                session['email'] = builder['email']
                session['role'] = 'builder'
                flash(f'Welcome to Site Portal, {builder["builder_name"]}!', 'success')
                return redirect(url_for('builder_dashboard'))

        flash('Invalid builder credentials or inactive account.', 'danger')

    return render_template('builder_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/builder/logout')
def builder_logout():
    session.clear()
    flash('You have been logged out from the Site Portal.', 'info')
    return redirect(url_for('builder_login'))

# -------------------------------------------------------------------
# Admin Dashboard
# -------------------------------------------------------------------
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # House statistics
    house_stats = query_db("""
        SELECT 
            COUNT(*) AS total_houses,
            SUM(CASE WHEN status = 'Planned' THEN 1 ELSE 0 END) AS planned,
            SUM(CASE WHEN status = 'Under Construction' THEN 1 ELSE 0 END) AS under_construction,
            SUM(CASE WHEN status = 'On Hold' THEN 1 ELSE 0 END) AS on_hold,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
        FROM houses;
    """, one=True)

    # Inventory statistics
    inv_stats = query_db("""
        SELECT 
            COUNT(*) AS total_materials,
            SUM(available_quantity) AS total_stock,
            SUM(CASE WHEN available_quantity <= 0 THEN 1 ELSE 0 END) AS out_of_stock,
            SUM(CASE WHEN available_quantity > 0 AND available_quantity <= minimum_stock_level THEN 1 ELSE 0 END) AS low_stock,
            SUM(CASE WHEN available_quantity > minimum_stock_level THEN 1 ELSE 0 END) AS available
        FROM materials;
    """, one=True)

    # Builder statistics
    builder_stats = query_db("""
        SELECT 
            COUNT(*) AS total_builders,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_builders
        FROM builders;
    """, one=True)

    # Update counts (Construction + Stock updates)
    const_updates_stats = query_db("""
        SELECT 
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected
        FROM construction_updates;
    """, one=True)

    stock_updates_stats = query_db("""
        SELECT 
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected
        FROM stock_updates;
    """, one=True)

    pending_updates_total = (const_updates_stats['pending'] or 0) + (stock_updates_stats['pending'] or 0)
    approved_updates_total = (const_updates_stats['approved'] or 0) + (stock_updates_stats['approved'] or 0)
    rejected_updates_total = (const_updates_stats['rejected'] or 0) + (stock_updates_stats['rejected'] or 0)

    # Construction Overview: Houses list with assigned builder
    houses_overview = query_db("""
        SELECT 
            h.house_id, h.house_number, h.house_type, h.bhk, h.location,
            h.construction_stage, h.progress_pct, h.status,
            GROUP_CONCAT(b.builder_name SEPARATOR ', ') AS assigned_builders
        FROM houses h
        LEFT JOIN builder_house_assignments bha ON h.house_id = bha.house_id AND bha.status = 'Active'
        LEFT JOIN builders b ON bha.builder_id = b.builder_id
        GROUP BY h.house_id
        ORDER BY h.house_number ASC;
    """)

    # Low Stock & Out of Stock Alerts
    low_stock_items = query_db("""
        SELECT material_id, material_name, category, unit, available_quantity, minimum_stock_level, unit_price,
               CASE 
                   WHEN available_quantity <= 0 THEN 'OUT OF STOCK'
                   WHEN available_quantity <= minimum_stock_level THEN 'LOW STOCK'
                   ELSE 'AVAILABLE'
               END AS stock_status
        FROM materials
        WHERE available_quantity <= minimum_stock_level
        ORDER BY available_quantity ASC;
    """)

    # Recent Builder Updates
    recent_const_updates = query_db("""
        SELECT 
            cu.update_id, 'Construction Progress' AS update_type,
            h.house_number, b.builder_name,
            cu.stage, cu.progress_pct, cu.remarks,
            cu.update_date, cu.status, cu.created_at
        FROM construction_updates cu
        JOIN houses h ON cu.house_id = h.house_id
        JOIN builders b ON cu.builder_id = b.builder_id
        ORDER BY cu.created_at DESC
        LIMIT 6;
    """)

    recent_stock_updates = query_db("""
        SELECT 
            su.stock_update_id, 'Material Stock/Usage' AS update_type,
            h.house_number, b.builder_name,
            m.material_name, m.unit, su.material_used, su.remaining_stock,
            su.remarks, su.update_date, su.status, su.created_at
        FROM stock_updates su
        JOIN houses h ON su.house_id = h.house_id
        JOIN builders b ON su.builder_id = b.builder_id
        JOIN materials m ON su.material_id = m.material_id
        ORDER BY su.created_at DESC
        LIMIT 6;
    """)

    # Stage distribution for charts
    stage_dist = query_db("""
        SELECT construction_stage, COUNT(*) AS cnt
        FROM houses
        GROUP BY construction_stage;
    """)

    return render_template(
        'admin_dashboard.html',
        house_stats=house_stats,
        inv_stats=inv_stats,
        builder_stats=builder_stats,
        pending_updates_total=pending_updates_total,
        approved_updates_total=approved_updates_total,
        rejected_updates_total=rejected_updates_total,
        houses_overview=houses_overview,
        low_stock_items=low_stock_items,
        recent_const_updates=recent_const_updates,
        recent_stock_updates=recent_stock_updates,
        stage_dist=stage_dist
    )

# -------------------------------------------------------------------
# Builder Dashboard (Mobile-friendly Site Interface)
# -------------------------------------------------------------------
@app.route('/builder/dashboard')
@builder_required
def builder_dashboard():
    builder_id = session['user_id']

    # Assigned houses for this builder
    assigned_houses = query_db("""
        SELECT 
            h.house_id, h.house_number, h.house_type, h.bhk, h.area_sqft,
            h.location, h.construction_stage, h.progress_pct, h.status,
            h.start_date, h.expected_completion_date,
            (SELECT MAX(update_date) FROM construction_updates WHERE house_id = h.house_id) AS last_update_date
        FROM houses h
        JOIN builder_house_assignments bha ON h.house_id = bha.house_id
        WHERE bha.builder_id = %s AND bha.status = 'Active'
        ORDER BY h.house_number ASC;
    """, (builder_id,))

    # Counts for this builder
    my_stats = query_db("""
        SELECT 
            (SELECT COUNT(*) FROM builder_house_assignments WHERE builder_id = %s AND status = 'Active') AS assigned_count,
            (SELECT COUNT(*) FROM houses h JOIN builder_house_assignments bha ON h.house_id = bha.house_id 
             WHERE bha.builder_id = %s AND bha.status = 'Active' AND h.status = 'Under Construction') AS in_progress_count,
            (SELECT COUNT(*) FROM construction_updates WHERE builder_id = %s AND status = 'PENDING') +
            (SELECT COUNT(*) FROM stock_updates WHERE builder_id = %s AND status = 'PENDING') AS pending_updates_count,
            (SELECT COUNT(*) FROM construction_updates WHERE builder_id = %s AND status = 'APPROVED') +
            (SELECT COUNT(*) FROM stock_updates WHERE builder_id = %s AND status = 'APPROVED') AS approved_updates_count;
    """, (builder_id, builder_id, builder_id, builder_id, builder_id, builder_id), one=True)

    # Recent updates submitted by this builder
    recent_submissions = query_db("""
        (SELECT 
            'Construction' AS update_category,
            h.house_number,
            CONCAT('Stage: ', cu.stage, ' (', cu.progress_pct, '%)') AS details,
            cu.update_date, cu.status, cu.created_at
         FROM construction_updates cu
         JOIN houses h ON cu.house_id = h.house_id
         WHERE cu.builder_id = %s)
        UNION ALL
        (SELECT 
            'Stock/Usage' AS update_category,
            h.house_number,
            CONCAT(m.material_name, ' - Used: ', su.material_used, ' ', m.unit) AS details,
            su.update_date, su.status, su.created_at
         FROM stock_updates su
         JOIN houses h ON su.house_id = h.house_id
         JOIN materials m ON su.material_id = m.material_id
         WHERE su.builder_id = %s)
        ORDER BY created_at DESC
        LIMIT 6;
    """, (builder_id, builder_id))

    return render_template(
        'builder_dashboard.html',
        assigned_houses=assigned_houses,
        my_stats=my_stats,
        recent_submissions=recent_submissions
    )

# -------------------------------------------------------------------
# House Management (Admin)
# -------------------------------------------------------------------
@app.route('/houses')
@admin_required
def houses():
    search = request.args.get('search', '').strip()
    stage_filter = request.args.get('stage', '').strip()
    status_filter = request.args.get('status', '').strip()

    sql = """
        SELECT 
            h.house_id, h.house_number, h.house_type, h.bhk, h.area_sqft,
            h.location, h.construction_stage, h.progress_pct, h.status,
            h.start_date, h.expected_completion_date, h.notes,
            GROUP_CONCAT(b.builder_name SEPARATOR ', ') AS assigned_builders
        FROM houses h
        LEFT JOIN builder_house_assignments bha ON h.house_id = bha.house_id AND bha.status = 'Active'
        LEFT JOIN builders b ON bha.builder_id = b.builder_id
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (h.house_number LIKE %s OR h.location LIKE %s OR h.house_type LIKE %s)"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])

    if stage_filter:
        sql += " AND h.construction_stage = %s"
        params.append(stage_filter)

    if status_filter:
        sql += " AND h.status = %s"
        params.append(status_filter)

    sql += " GROUP BY h.house_id ORDER BY h.house_number ASC;"

    houses_list = query_db(sql, params)
    builders_list = query_db("SELECT builder_id, builder_name FROM builders WHERE status = 'Active' ORDER BY builder_name ASC;")

    stages = ['Foundation', 'Structure', 'Brickwork', 'Plumbing', 'Electrical', 'Flooring', 'Painting', 'Finishing', 'Completed']
    statuses = ['Planned', 'Under Construction', 'On Hold', 'Completed']

    return render_template(
        'houses.html',
        houses=houses_list,
        builders=builders_list,
        stages=stages,
        statuses=statuses,
        search=search,
        selected_stage=stage_filter,
        selected_status=status_filter
    )

@app.route('/houses/add', methods=['POST'])
@admin_required
def add_house():
    house_number = request.form.get('house_number', '').strip()
    house_type = request.form.get('house_type', '').strip()
    bhk = request.form.get('bhk', '').strip()
    area_sqft = request.form.get('area_sqft', '').strip()
    location = request.form.get('location', '').strip()
    stage = request.form.get('construction_stage', 'Foundation').strip()
    progress_pct = request.form.get('progress_pct', '0.00').strip()
    status = request.form.get('status', 'Planned').strip()
    start_date = request.form.get('start_date') or None
    expected_completion_date = request.form.get('expected_completion_date') or None
    assigned_builder_id = request.form.get('assigned_builder_id') or None
    notes = request.form.get('notes', '').strip()

    if not house_number or not house_type or not bhk or not area_sqft or not location:
        flash('House Number, Type, BHK, Area, and Location are required.', 'warning')
        return redirect(url_for('houses'))

    existing = query_db("SELECT house_id FROM houses WHERE house_number = %s;", (house_number,), one=True)
    if existing:
        flash(f'House with number "{house_number}" already exists.', 'danger')
        return redirect(url_for('houses'))

    try:
        area_sqft_val = float(area_sqft)
        progress_val = float(progress_pct)
        if area_sqft_val <= 0 or not (0 <= progress_val <= 100):
            flash('Invalid Area or Progress range.', 'warning')
            return redirect(url_for('houses'))
    except ValueError:
        flash('Invalid numeric value for Area or Progress.', 'warning')
        return redirect(url_for('houses'))

    house_id = query_db("""
        INSERT INTO houses (house_number, house_type, bhk, area_sqft, location, construction_stage, progress_pct, status, start_date, expected_completion_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (house_number, house_type, bhk, area_sqft_val, location, stage, progress_val, status, start_date, expected_completion_date, notes), commit=True)

    if assigned_builder_id:
        query_db("""
            INSERT INTO builder_house_assignments (builder_id, house_id, status, notes)
            VALUES (%s, %s, 'Active', 'Initial assignment during house creation');
        """, (assigned_builder_id, house_id), commit=True)

    flash(f'House {house_number} created successfully!', 'success')
    return redirect(url_for('houses'))

@app.route('/houses/edit/<int:house_id>', methods=['POST'])
@admin_required
def edit_house(house_id):
    house_number = request.form.get('house_number', '').strip()
    house_type = request.form.get('house_type', '').strip()
    bhk = request.form.get('bhk', '').strip()
    area_sqft = request.form.get('area_sqft', '').strip()
    location = request.form.get('location', '').strip()
    stage = request.form.get('construction_stage', '').strip()
    progress_pct = request.form.get('progress_pct', '').strip()
    status = request.form.get('status', '').strip()
    start_date = request.form.get('start_date') or None
    expected_completion_date = request.form.get('expected_completion_date') or None
    notes = request.form.get('notes', '').strip()

    dup = query_db("SELECT house_id FROM houses WHERE house_number = %s AND house_id != %s;", (house_number, house_id), one=True)
    if dup:
        flash(f'Another house already has number "{house_number}".', 'danger')
        return redirect(url_for('houses'))

    try:
        area_sqft_val = float(area_sqft)
        progress_val = float(progress_pct)
    except ValueError:
        flash('Invalid numeric inputs.', 'warning')
        return redirect(url_for('houses'))

    query_db("""
        UPDATE houses 
        SET house_number = %s, house_type = %s, bhk = %s, area_sqft = %s,
            location = %s, construction_stage = %s, progress_pct = %s,
            status = %s, start_date = %s, expected_completion_date = %s, notes = %s
        WHERE house_id = %s;
    """, (house_number, house_type, bhk, area_sqft_val, location, stage, progress_val, status, start_date, expected_completion_date, notes, house_id), commit=True)

    flash(f'House {house_number} updated successfully.', 'success')
    return redirect(url_for('houses'))

@app.route('/houses/delete/<int:house_id>', methods=['POST'])
@admin_required
def delete_house(house_id):
    house = query_db("SELECT house_number FROM houses WHERE house_id = %s;", (house_id,), one=True)
    if house:
        query_db("DELETE FROM houses WHERE house_id = %s;", (house_id,), commit=True)
        flash(f'House {house["house_number"]} and associated records deleted.', 'info')
    return redirect(url_for('houses'))

# -------------------------------------------------------------------
# House Details Page (Comprehensive View)
# -------------------------------------------------------------------
@app.route('/houses/<int:house_id>')
@login_required
def house_details(house_id):
    if session.get('role') == 'builder':
        builder_id = session['user_id']
        assigned = query_db("""
            SELECT assignment_id FROM builder_house_assignments 
            WHERE house_id = %s AND builder_id = %s AND status = 'Active';
        """, (house_id, builder_id), one=True)
        if not assigned:
            flash('You do not have access to this house.', 'danger')
            return redirect(url_for('builder_dashboard'))

    house = query_db("SELECT * FROM houses WHERE house_id = %s;", (house_id,), one=True)
    if not house:
        flash('House not found.', 'warning')
        return redirect(url_for('houses'))

    assigned_builders = query_db("""
        SELECT bha.assignment_id, bha.assigned_date, bha.notes, bha.status,
               b.builder_id, b.builder_name, b.email, b.phone
        FROM builder_house_assignments bha
        JOIN builders b ON bha.builder_id = b.builder_id
        WHERE bha.house_id = %s AND bha.status = 'Active'
        ORDER BY bha.assigned_date DESC;
    """, (house_id,))

    all_builders = query_db("SELECT builder_id, builder_name FROM builders WHERE status = 'Active' ORDER BY builder_name ASC;")

    material_summary = query_db("""
        SELECT 
            mr.requirement_id, mr.house_id, mr.material_id, mr.required_quantity, mr.notes AS req_notes,
            m.material_name, m.category, m.unit, m.available_quantity, m.unit_price,
            COALESCE((
                SELECT SUM(su.material_used)
                FROM stock_updates su
                WHERE su.house_id = mr.house_id 
                  AND su.material_id = mr.material_id 
                  AND su.status = 'APPROVED'
            ), 0) AS approved_used_quantity
        FROM material_requirements mr
        JOIN materials m ON mr.material_id = m.material_id
        WHERE mr.house_id = %s
        ORDER BY m.category, m.material_name ASC;
    """, (house_id,))

    for item in material_summary:
        item['remaining_quantity'] = max(0.0, float(item['required_quantity']) - float(item['approved_used_quantity']))
        if float(item['approved_used_quantity']) >= float(item['required_quantity']):
            item['req_status'] = 'COMPLETED'
        elif float(item['approved_used_quantity']) > 0:
            item['req_status'] = 'IN PROGRESS'
        else:
            item['req_status'] = 'NOT STARTED'

    const_updates = query_db("""
        SELECT cu.*, b.builder_name, a.full_name AS reviewer_name
        FROM construction_updates cu
        JOIN builders b ON cu.builder_id = b.builder_id
        LEFT JOIN admins a ON cu.reviewed_by = a.admin_id
        WHERE cu.house_id = %s
        ORDER BY cu.update_date DESC, cu.created_at DESC;
    """, (house_id,))

    stock_updates = query_db("""
        SELECT su.*, b.builder_name, m.material_name, m.unit, a.full_name AS reviewer_name
        FROM stock_updates su
        JOIN builders b ON su.builder_id = b.builder_id
        JOIN materials m ON su.material_id = m.material_id
        LEFT JOIN admins a ON su.reviewed_by = a.admin_id
        WHERE su.house_id = %s
        ORDER BY su.update_date DESC, su.created_at DESC;
    """, (house_id,))

    available_materials = query_db("SELECT material_id, material_name, category, unit FROM materials ORDER BY category, material_name ASC;")

    return render_template(
        'house_details.html',
        house=house,
        assigned_builders=assigned_builders,
        all_builders=all_builders,
        material_summary=material_summary,
        const_updates=const_updates,
        stock_updates=stock_updates,
        available_materials=available_materials
    )

@app.route('/houses/<int:house_id>/assign-builder', methods=['POST'])
@admin_required
def assign_builder_to_house(house_id):
    builder_id = request.form.get('builder_id')
    notes = request.form.get('notes', '').strip()

    if not builder_id:
        flash('Please select a builder to assign.', 'warning')
        return redirect(url_for('house_details', house_id=house_id))

    existing = query_db("""
        SELECT assignment_id FROM builder_house_assignments 
        WHERE house_id = %s AND builder_id = %s AND status = 'Active';
    """, (house_id, builder_id), one=True)
    if existing:
        flash('This builder is already actively assigned to this house.', 'info')
        return redirect(url_for('house_details', house_id=house_id))

    query_db("""
        INSERT INTO builder_house_assignments (builder_id, house_id, status, notes)
        VALUES (%s, %s, 'Active', %s);
    """, (builder_id, house_id, notes), commit=True)

    flash('Builder successfully assigned to house.', 'success')
    return redirect(url_for('house_details', house_id=house_id))

@app.route('/assignments/remove/<int:assignment_id>', methods=['POST'])
@admin_required
def remove_builder_assignment(assignment_id):
    assignment = query_db("SELECT house_id FROM builder_house_assignments WHERE assignment_id = %s;", (assignment_id,), one=True)
    if assignment:
        query_db("UPDATE builder_house_assignments SET status = 'Reassigned' WHERE assignment_id = %s;", (assignment_id,), commit=True)
        flash('Builder assignment removed.', 'info')
        return redirect(url_for('house_details', house_id=assignment['house_id']))
    return redirect(url_for('houses'))

# -------------------------------------------------------------------
# Master Material Inventory
# -------------------------------------------------------------------
@app.route('/materials')
@admin_required
def materials():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    sql = """
        SELECT 
            m.material_id, m.material_name, m.category, m.unit,
            m.available_quantity, m.minimum_stock_level, m.unit_price,
            m.storage_location, s.supplier_name,
            CASE 
                WHEN m.available_quantity <= 0 THEN 'OUT OF STOCK'
                WHEN m.available_quantity <= m.minimum_stock_level THEN 'LOW STOCK'
                ELSE 'AVAILABLE'
            END AS stock_status
        FROM materials m
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (m.material_name LIKE %s OR m.category LIKE %s OR m.storage_location LIKE %s)"
        pat = f"%{search}%"
        params.extend([pat, pat, pat])

    if category_filter:
        sql += " AND m.category = %s"
        params.append(category_filter)

    if status_filter:
        if status_filter == 'OUT OF STOCK':
            sql += " AND m.available_quantity <= 0"
        elif status_filter == 'LOW STOCK':
            sql += " AND m.available_quantity > 0 AND m.available_quantity <= m.minimum_stock_level"
        elif status_filter == 'AVAILABLE':
            sql += " AND m.available_quantity > m.minimum_stock_level"

    sql += " ORDER BY m.category ASC, m.material_name ASC;"

    materials_list = query_db(sql, params)
    categories = query_db("SELECT DISTINCT category FROM materials ORDER BY category ASC;")
    suppliers_list = query_db("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC;")

    return render_template(
        'materials.html',
        materials=materials_list,
        categories=categories,
        suppliers=suppliers_list,
        search=search,
        selected_category=category_filter,
        selected_status=status_filter
    )

@app.route('/materials/add', methods=['POST'])
@admin_required
def add_material():
    material_name = request.form.get('material_name', '').strip()
    category = request.form.get('category', '').strip()
    unit = request.form.get('unit', '').strip()
    available_qty = request.form.get('available_quantity', '0').strip()
    min_stock = request.form.get('minimum_stock_level', '0').strip()
    unit_price = request.form.get('unit_price', '0').strip()
    supplier_id = request.form.get('supplier_id') or None
    storage_location = request.form.get('storage_location', '').strip()

    if not material_name or not category or not unit:
        flash('Material name, category, and unit are required.', 'warning')
        return redirect(url_for('materials'))

    try:
        avail_val = float(available_qty)
        min_val = float(min_stock)
        price_val = float(unit_price)
        if avail_val < 0 or min_val < 0 or price_val < 0:
            flash('Stock quantities and unit price cannot be negative.', 'warning')
            return redirect(url_for('materials'))
    except ValueError:
        flash('Invalid numeric inputs for quantity or price.', 'warning')
        return redirect(url_for('materials'))

    query_db("""
        INSERT INTO materials (material_name, category, unit, available_quantity, minimum_stock_level, unit_price, supplier_id, storage_location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, (material_name, category, unit, avail_val, min_val, price_val, supplier_id, storage_location), commit=True)

    flash(f'Material "{material_name}" added successfully.', 'success')
    return redirect(url_for('materials'))

@app.route('/materials/edit/<int:material_id>', methods=['POST'])
@admin_required
def edit_material(material_id):
    material_name = request.form.get('material_name', '').strip()
    category = request.form.get('category', '').strip()
    unit = request.form.get('unit', '').strip()
    available_qty = request.form.get('available_quantity', '0').strip()
    min_stock = request.form.get('minimum_stock_level', '0').strip()
    unit_price = request.form.get('unit_price', '0').strip()
    supplier_id = request.form.get('supplier_id') or None
    storage_location = request.form.get('storage_location', '').strip()

    try:
        avail_val = float(available_qty)
        min_val = float(min_stock)
        price_val = float(unit_price)
        if avail_val < 0 or min_val < 0 or price_val < 0:
            flash('Stock quantities and unit price cannot be negative.', 'warning')
            return redirect(url_for('materials'))
    except ValueError:
        flash('Invalid numeric inputs.', 'warning')
        return redirect(url_for('materials'))

    query_db("""
        UPDATE materials 
        SET material_name = %s, category = %s, unit = %s, available_quantity = %s,
            minimum_stock_level = %s, unit_price = %s, supplier_id = %s, storage_location = %s
        WHERE material_id = %s;
    """, (material_name, category, unit, avail_val, min_val, price_val, supplier_id, storage_location, material_id), commit=True)

    flash(f'Material "{material_name}" updated successfully.', 'success')
    return redirect(url_for('materials'))

@app.route('/materials/delete/<int:material_id>', methods=['POST'])
@admin_required
def delete_material(material_id):
    tx_count = query_db("SELECT COUNT(*) as cnt FROM inventory_transactions WHERE material_id = %s;", (material_id,), one=True)
    if tx_count and tx_count['cnt'] > 0:
        flash('Cannot delete this material because historical transactions exist for it.', 'danger')
        return redirect(url_for('materials'))

    query_db("DELETE FROM materials WHERE material_id = %s;", (material_id,), commit=True)
    flash('Material deleted successfully.', 'info')
    return redirect(url_for('materials'))

@app.route('/api/materials/<int:material_id>')
@login_required
def api_material_info(material_id):
    mat = query_db("""
        SELECT material_id, material_name, category, unit, available_quantity, minimum_stock_level, unit_price
        FROM materials WHERE material_id = %s;
    """, (material_id,), one=True)
    if mat:
        return jsonify({
            'success': True,
            'material': {
                'id': mat['material_id'],
                'name': mat['material_name'],
                'category': mat['category'],
                'unit': mat['unit'],
                'available_quantity': float(mat['available_quantity']),
                'minimum_stock_level': float(mat['minimum_stock_level']),
                'unit_price': float(mat['unit_price'])
            }
        })
    return jsonify({'success': False, 'message': 'Material not found'}), 404

# -------------------------------------------------------------------
# Material Inward (Receiving Stock from Suppliers)
# -------------------------------------------------------------------
@app.route('/inward', methods=['GET', 'POST'])
@admin_required
def inward():
    if request.method == 'POST':
        material_id = request.form.get('material_id')
        supplier_id = request.form.get('supplier_id') or None
        house_id = request.form.get('house_id') or None
        quantity_str = request.form.get('quantity', '0').strip()
        unit_price_str = request.form.get('unit_price', '0').strip()
        invoice_number = request.form.get('invoice_number', '').strip()
        received_date = request.form.get('received_date') or str(date.today())
        notes = request.form.get('notes', '').strip()

        if not material_id:
            flash('Please select a material.', 'warning')
            return redirect(url_for('inward'))

        try:
            quantity = float(quantity_str)
            unit_price = float(unit_price_str)
            if quantity <= 0:
                flash('Received quantity must be greater than zero.', 'warning')
                return redirect(url_for('inward'))
            if unit_price < 0:
                flash('Unit price cannot be negative.', 'warning')
                return redirect(url_for('inward'))
        except ValueError:
            flash('Invalid quantity or price value.', 'warning')
            return redirect(url_for('inward'))

        total_cost = quantity * unit_price

        mat = query_db("SELECT material_name, unit, available_quantity FROM materials WHERE material_id = %s;", (material_id,), one=True)
        if not mat:
            flash('Selected material not found.', 'danger')
            return redirect(url_for('inward'))

        new_stock = float(mat['available_quantity']) + quantity

        # Update material stock
        query_db("UPDATE materials SET available_quantity = %s WHERE material_id = %s;", (new_stock, material_id), commit=True)

        # Record IN transaction
        query_db("""
            INSERT INTO inventory_transactions
            (transaction_type, material_id, house_id, supplier_id, quantity, unit_price, total_cost, transaction_date, invoice_number, purpose, notes, status)
            VALUES ('IN', %s, %s, %s, %s, %s, %s, %s, %s, 'Supplier Delivery', %s, 'COMPLETED');
        """, (material_id, house_id, supplier_id, quantity, unit_price, total_cost, received_date, invoice_number, notes), commit=True)

        flash(f'Successfully received {quantity} {mat["unit"]} of {mat["material_name"]}. Updated available stock: {new_stock} {mat["unit"]}.', 'success')
        return redirect(url_for('inward'))

    materials_list = query_db("SELECT material_id, material_name, category, unit, unit_price, available_quantity FROM materials ORDER BY category, material_name ASC;")
    suppliers_list = query_db("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC;")
    houses_list = query_db("SELECT house_id, house_number, location FROM houses ORDER BY house_number ASC;")

    recent_inwards = query_db("""
        SELECT 
            it.transaction_id, it.transaction_date, it.quantity, it.unit_price, it.total_cost, it.invoice_number, it.notes,
            m.material_name, m.unit, s.supplier_name, h.house_number
        FROM inventory_transactions it
        JOIN materials m ON it.material_id = m.material_id
        LEFT JOIN suppliers s ON it.supplier_id = s.supplier_id
        LEFT JOIN houses h ON it.house_id = h.house_id
        WHERE it.transaction_type = 'IN'
        ORDER BY it.transaction_date DESC, it.created_at DESC
        LIMIT 10;
    """)

    return render_template(
        'inward.html',
        materials=materials_list,
        suppliers=suppliers_list,
        houses=houses_list,
        recent_inwards=recent_inwards,
        today_date=str(date.today())
    )

# -------------------------------------------------------------------
# Material Outward (Direct Admin Issuance / Dispatch to Site)
# -------------------------------------------------------------------
@app.route('/outward', methods=['GET', 'POST'])
@admin_required
def outward():
    if request.method == 'POST':
        material_id = request.form.get('material_id')
        house_id = request.form.get('house_id')
        builder_id = request.form.get('builder_id') or None
        quantity_str = request.form.get('quantity', '0').strip()
        issue_date = request.form.get('issue_date') or str(date.today())
        purpose = request.form.get('purpose', 'Direct site dispatch').strip()
        notes = request.form.get('notes', '').strip()

        if not material_id or not house_id:
            flash('Material and House selection are required.', 'warning')
            return redirect(url_for('outward'))

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                flash('Quantity issued must be greater than zero.', 'warning')
                return redirect(url_for('outward'))
        except ValueError:
            flash('Invalid quantity input.', 'warning')
            return redirect(url_for('outward'))

        mat = query_db("SELECT material_name, unit, unit_price, available_quantity FROM materials WHERE material_id = %s;", (material_id,), one=True)
        if not mat:
            flash('Material not found.', 'danger')
            return redirect(url_for('outward'))

        current_stock = float(mat['available_quantity'])
        if quantity > current_stock:
            flash(f'Cannot issue {quantity} {mat["unit"]}. Available stock is only {current_stock} {mat["unit"]}.', 'danger')
            return redirect(url_for('outward'))

        new_stock = current_stock - quantity
        total_cost = quantity * float(mat['unit_price'])

        # Deduct from official inventory
        query_db("UPDATE materials SET available_quantity = %s WHERE material_id = %s;", (new_stock, material_id), commit=True)

        # Record OUT transaction
        query_db("""
            INSERT INTO inventory_transactions
            (transaction_type, material_id, house_id, builder_id, quantity, unit_price, total_cost, transaction_date, purpose, notes, status)
            VALUES ('OUT', %s, %s, %s, %s, %s, %s, %s, %s, %s, 'COMPLETED');
        """, (material_id, house_id, builder_id, quantity, mat['unit_price'], total_cost, issue_date, purpose, notes), commit=True)

        flash(f'Issued {quantity} {mat["unit"]} of {mat["material_name"]} to site. Remaining stock: {new_stock} {mat["unit"]}.', 'success')
        return redirect(url_for('outward'))

    materials_list = query_db("SELECT material_id, material_name, category, unit, unit_price, available_quantity FROM materials WHERE available_quantity > 0 ORDER BY category, material_name ASC;")
    houses_list = query_db("SELECT house_id, house_number, location FROM houses ORDER BY house_number ASC;")
    builders_list = query_db("SELECT builder_id, builder_name FROM builders WHERE status = 'Active' ORDER BY builder_name ASC;")

    recent_outwards = query_db("""
        SELECT 
            it.transaction_id, it.transaction_date, it.quantity, it.unit_price, it.total_cost, it.purpose, it.notes,
            m.material_name, m.unit, h.house_number, b.builder_name
        FROM inventory_transactions it
        JOIN materials m ON it.material_id = m.material_id
        LEFT JOIN houses h ON it.house_id = h.house_id
        LEFT JOIN builders b ON it.builder_id = b.builder_id
        WHERE it.transaction_type = 'OUT'
        ORDER BY it.transaction_date DESC, it.created_at DESC
        LIMIT 10;
    """)

    return render_template(
        'outward.html',
        materials=materials_list,
        houses=houses_list,
        builders=builders_list,
        recent_outwards=recent_outwards,
        today_date=str(date.today())
    )

# -------------------------------------------------------------------
# House Material Requirements (Admin)
# -------------------------------------------------------------------
@app.route('/requirements')
@admin_required
def requirements():
    house_id = request.args.get('house_id')
    houses_list = query_db("SELECT house_id, house_number, house_type, bhk, location FROM houses ORDER BY house_number ASC;")

    selected_house = None
    requirements_list = []
    if house_id:
        selected_house = query_db("SELECT * FROM houses WHERE house_id = %s;", (house_id,), one=True)
        if selected_house:
            requirements_list = query_db("""
                SELECT 
                    mr.requirement_id, mr.house_id, mr.material_id, mr.required_quantity, mr.notes,
                    m.material_name, m.category, m.unit, m.available_quantity,
                    COALESCE((
                        SELECT SUM(su.material_used)
                        FROM stock_updates su
                        WHERE su.house_id = mr.house_id 
                          AND su.material_id = mr.material_id 
                          AND su.status = 'APPROVED'
                    ), 0) AS approved_used_quantity
                FROM material_requirements mr
                JOIN materials m ON mr.material_id = m.material_id
                WHERE mr.house_id = %s
                ORDER BY m.category, m.material_name ASC;
            """, (house_id,))

            for item in requirements_list:
                item['remaining_quantity'] = max(0.0, float(item['required_quantity']) - float(item['approved_used_quantity']))
                if float(item['approved_used_quantity']) >= float(item['required_quantity']):
                    item['status'] = 'COMPLETED'
                elif float(item['approved_used_quantity']) > 0:
                    item['status'] = 'IN PROGRESS'
                else:
                    item['status'] = 'PENDING'

    materials_list = query_db("SELECT material_id, material_name, category, unit FROM materials ORDER BY category, material_name ASC;")

    return render_template(
        'requirements.html',
        houses=houses_list,
        selected_house=selected_house,
        requirements=requirements_list,
        materials=materials_list
    )

@app.route('/requirements/add', methods=['POST'])
@admin_required
def add_requirement():
    house_id = request.form.get('house_id')
    material_id = request.form.get('material_id')
    required_qty_str = request.form.get('required_quantity', '0').strip()
    notes = request.form.get('notes', '').strip()

    if not house_id or not material_id:
        flash('House and Material are required.', 'warning')
        return redirect(url_for('requirements', house_id=house_id))

    try:
        required_qty = float(required_qty_str)
        if required_qty <= 0:
            flash('Required quantity must be greater than zero.', 'warning')
            return redirect(url_for('requirements', house_id=house_id))
    except ValueError:
        flash('Invalid required quantity value.', 'warning')
        return redirect(url_for('requirements', house_id=house_id))

    query_db("""
        INSERT INTO material_requirements (house_id, material_id, required_quantity, notes)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE required_quantity = %s, notes = %s;
    """, (house_id, material_id, required_qty, notes, required_qty, notes), commit=True)

    flash('Material requirement saved successfully.', 'success')
    return redirect(url_for('requirements', house_id=house_id))

@app.route('/requirements/delete/<int:requirement_id>', methods=['POST'])
@admin_required
def delete_requirement(requirement_id):
    req = query_db("SELECT house_id FROM material_requirements WHERE requirement_id = %s;", (requirement_id,), one=True)
    if req:
        query_db("DELETE FROM material_requirements WHERE requirement_id = %s;", (requirement_id,), commit=True)
        flash('Material requirement deleted.', 'info')
        return redirect(url_for('requirements', house_id=req['house_id']))
    return redirect(url_for('requirements'))

# -------------------------------------------------------------------
# Builder Site Actions (Progress & Stock Updates)
# -------------------------------------------------------------------
@app.route('/builder/houses/<int:house_id>/update-progress', methods=['GET', 'POST'])
@builder_required
def builder_construction_update(house_id):
    builder_id = session['user_id']

    assignment = query_db("""
        SELECT assignment_id FROM builder_house_assignments 
        WHERE house_id = %s AND builder_id = %s AND status = 'Active';
    """, (house_id, builder_id), one=True)
    if not assignment:
        flash('This house is not assigned to you.', 'danger')
        return redirect(url_for('builder_dashboard'))

    house = query_db("SELECT * FROM houses WHERE house_id = %s;", (house_id,), one=True)

    if request.method == 'POST':
        stage = request.form.get('stage', '').strip()
        progress_str = request.form.get('progress_pct', '0').strip()
        work_completed = request.form.get('work_completed', '').strip()
        work_pending = request.form.get('work_pending', '').strip()
        remarks = request.form.get('remarks', '').strip()
        update_date = request.form.get('update_date') or str(date.today())

        if not stage or not progress_str:
            flash('Stage and progress percentage are required.', 'warning')
            return render_template('builder_construction_update.html', house=house, today_date=str(date.today()))

        try:
            progress_pct = float(progress_str)
            if not (0 <= progress_pct <= 100):
                flash('Progress percentage must be between 0 and 100.', 'warning')
                return render_template('builder_construction_update.html', house=house, today_date=str(date.today()))
        except ValueError:
            flash('Invalid progress value.', 'warning')
            return render_template('builder_construction_update.html', house=house, today_date=str(date.today()))

        query_db("""
            INSERT INTO construction_updates
            (house_id, builder_id, stage, progress_pct, work_completed, work_pending, remarks, update_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING');
        """, (house_id, builder_id, stage, progress_pct, work_completed, work_pending, remarks, update_date), commit=True)

        flash('Construction progress update submitted successfully! Status: PENDING Admin review.', 'success')
        return redirect(url_for('builder_my_updates'))

    stages = ['Foundation', 'Structure', 'Brickwork', 'Plumbing', 'Electrical', 'Flooring', 'Painting', 'Finishing', 'Completed']
    return render_template(
        'builder_construction_update.html',
        house=house,
        stages=stages,
        today_date=str(date.today())
    )

@app.route('/builder/houses/<int:house_id>/stock-update', methods=['GET', 'POST'])
@builder_required
def builder_stock_update(house_id):
    builder_id = session['user_id']

    assignment = query_db("""
        SELECT assignment_id FROM builder_house_assignments 
        WHERE house_id = %s AND builder_id = %s AND status = 'Active';
    """, (house_id, builder_id), one=True)
    if not assignment:
        flash('This house is not assigned to you.', 'danger')
        return redirect(url_for('builder_dashboard'))

    house = query_db("SELECT * FROM houses WHERE house_id = %s;", (house_id,), one=True)

    if request.method == 'POST':
        material_id = request.form.get('material_id')
        opening_stock_str = request.form.get('opening_stock', '0').strip()
        material_received_str = request.form.get('material_received', '0').strip()
        material_used_str = request.form.get('material_used', '0').strip()
        remarks = request.form.get('remarks', '').strip()
        update_date = request.form.get('update_date') or str(date.today())

        if not material_id:
            flash('Please select a material.', 'warning')
            return redirect(url_for('builder_stock_update', house_id=house_id))

        try:
            opening_stock = float(opening_stock_str)
            material_received = float(material_received_str)
            material_used = float(material_used_str)

            if opening_stock < 0 or material_received < 0 or material_used < 0:
                flash('Stock values cannot be negative.', 'warning')
                return redirect(url_for('builder_stock_update', house_id=house_id))

            # Calculation: Remaining Stock = Opening Stock + Material Received - Material Used
            remaining_stock = opening_stock + material_received - material_used

            if remaining_stock < 0:
                flash('Material Used cannot exceed total available site stock (Opening Stock + Received). Remaining stock cannot be negative.', 'danger')
                return redirect(url_for('builder_stock_update', house_id=house_id))

        except ValueError:
            flash('Invalid numeric inputs for stock.', 'warning')
            return redirect(url_for('builder_stock_update', house_id=house_id))

        mat = query_db("SELECT material_name, unit, available_quantity FROM materials WHERE material_id = %s;", (material_id,), one=True)
        if not mat:
            flash('Selected material not found.', 'danger')
            return redirect(url_for('builder_stock_update', house_id=house_id))

        query_db("""
            INSERT INTO stock_updates
            (house_id, builder_id, material_id, opening_stock, material_received, material_used, remaining_stock, update_date, remarks, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING');
        """, (house_id, builder_id, material_id, opening_stock, material_received, material_used, remaining_stock, update_date, remarks), commit=True)

        flash(f'Stock update for {mat["material_name"]} submitted successfully! Status: PENDING Admin review and approval.', 'success')
        return redirect(url_for('builder_my_updates'))

    materials_list = query_db("""
        SELECT m.material_id, m.material_name, m.category, m.unit, m.available_quantity
        FROM materials m
        ORDER BY m.category, m.material_name ASC;
    """)

    return render_template(
        'builder_stock_update.html',
        house=house,
        materials=materials_list,
        today_date=str(date.today())
    )

@app.route('/builder/my-updates')
@builder_required
def builder_my_updates():
    builder_id = session['user_id']

    const_updates = query_db("""
        SELECT cu.*, h.house_number, a.full_name AS reviewer_name
        FROM construction_updates cu
        JOIN houses h ON cu.house_id = h.house_id
        LEFT JOIN admins a ON cu.reviewed_by = a.admin_id
        WHERE cu.builder_id = %s
        ORDER BY cu.created_at DESC;
    """, (builder_id,))

    stock_updates = query_db("""
        SELECT su.*, h.house_number, m.material_name, m.unit, a.full_name AS reviewer_name
        FROM stock_updates su
        JOIN houses h ON su.house_id = h.house_id
        JOIN materials m ON su.material_id = m.material_id
        LEFT JOIN admins a ON su.reviewed_by = a.admin_id
        WHERE su.builder_id = %s
        ORDER BY su.created_at DESC;
    """, (builder_id,))

    return render_template(
        'builder_my_updates.html',
        const_updates=const_updates,
        stock_updates=stock_updates
    )

# -------------------------------------------------------------------
# Admin Approval System (Review Builder Submissions)
# -------------------------------------------------------------------
@app.route('/builder-updates')
@admin_required
def builder_updates():
    pending_const = query_db("""
        SELECT cu.*, h.house_number, h.location, b.builder_name, b.email AS builder_email
        FROM construction_updates cu
        JOIN houses h ON cu.house_id = h.house_id
        JOIN builders b ON cu.builder_id = b.builder_id
        WHERE cu.status = 'PENDING'
        ORDER BY cu.update_date ASC, cu.created_at ASC;
    """)

    pending_stock = query_db("""
        SELECT su.*, h.house_number, h.location, b.builder_name,
               m.material_name, m.unit, m.available_quantity, m.unit_price
        FROM stock_updates su
        JOIN houses h ON su.house_id = h.house_id
        JOIN builders b ON su.builder_id = b.builder_id
        JOIN materials m ON su.material_id = m.material_id
        WHERE su.status = 'PENDING'
        ORDER BY su.update_date ASC, su.created_at ASC;
    """)

    reviewed_const = query_db("""
        SELECT cu.*, h.house_number, b.builder_name, a.full_name AS reviewer_name
        FROM construction_updates cu
        JOIN houses h ON cu.house_id = h.house_id
        JOIN builders b ON cu.builder_id = b.builder_id
        LEFT JOIN admins a ON cu.reviewed_by = a.admin_id
        WHERE cu.status != 'PENDING'
        ORDER BY cu.review_date DESC
        LIMIT 20;
    """)

    reviewed_stock = query_db("""
        SELECT su.*, h.house_number, b.builder_name, m.material_name, m.unit, a.full_name AS reviewer_name
        FROM stock_updates su
        JOIN houses h ON su.house_id = h.house_id
        JOIN builders b ON su.builder_id = b.builder_id
        JOIN materials m ON su.material_id = m.material_id
        LEFT JOIN admins a ON su.reviewed_by = a.admin_id
        WHERE su.status != 'PENDING'
        ORDER BY su.review_date DESC
        LIMIT 20;
    """)

    return render_template(
        'builder_updates.html',
        pending_const=pending_const,
        pending_stock=pending_stock,
        reviewed_const=reviewed_const,
        reviewed_stock=reviewed_stock
    )

@app.route('/builder-updates/approve-construction/<int:update_id>', methods=['POST'])
@admin_required
def approve_construction_update(update_id):
    admin_id = session['user_id']
    review_notes = request.form.get('review_notes', 'Approved after site verification').strip()

    update = query_db("SELECT * FROM construction_updates WHERE update_id = %s;", (update_id,), one=True)
    if not update:
        flash('Construction update not found.', 'warning')
        return redirect(url_for('builder_updates'))

    if update['status'] != 'PENDING':
        flash('This update has already been reviewed.', 'info')
        return redirect(url_for('builder_updates'))

    query_db("""
        UPDATE construction_updates 
        SET status = 'APPROVED', reviewed_by = %s, review_date = NOW(), review_notes = %s
        WHERE update_id = %s;
    """, (admin_id, review_notes, update_id), commit=True)

    new_stage = update['stage']
    new_progress = float(update['progress_pct'])
    house_status = 'Completed' if (new_progress >= 100 and new_stage == 'Completed') else 'Under Construction'

    query_db("""
        UPDATE houses 
        SET construction_stage = %s, progress_pct = %s, status = %s
        WHERE house_id = %s;
    """, (new_stage, new_progress, house_status, update['house_id']), commit=True)

    flash('Construction progress update APPROVED! Official house stage and progress updated.', 'success')
    return redirect(url_for('builder_updates'))

@app.route('/builder-updates/reject-construction/<int:update_id>', methods=['POST'])
@admin_required
def reject_construction_update(update_id):
    admin_id = session['user_id']
    review_notes = request.form.get('review_notes', 'Rejected by Administrator').strip()

    update = query_db("SELECT * FROM construction_updates WHERE update_id = %s;", (update_id,), one=True)
    if not update or update['status'] != 'PENDING':
        flash('Invalid update or already processed.', 'warning')
        return redirect(url_for('builder_updates'))

    query_db("""
        UPDATE construction_updates 
        SET status = 'REJECTED', reviewed_by = %s, review_date = NOW(), review_notes = %s
        WHERE update_id = %s;
    """, (admin_id, review_notes, update_id), commit=True)

    flash('Construction update has been REJECTED.', 'info')
    return redirect(url_for('builder_updates'))

@app.route('/builder-updates/approve-stock/<int:stock_update_id>', methods=['POST'])
@admin_required
def approve_stock_update(stock_update_id):
    admin_id = session['user_id']
    review_notes = request.form.get('review_notes', 'Approved and verified').strip()

    update = query_db("""
        SELECT su.*, m.material_name, m.unit, m.unit_price, m.available_quantity
        FROM stock_updates su
        JOIN materials m ON su.material_id = m.material_id
        WHERE su.stock_update_id = %s;
    """, (stock_update_id,), one=True)

    if not update:
        flash('Stock update record not found.', 'warning')
        return redirect(url_for('builder_updates'))

    if update['status'] != 'PENDING':
        flash('This stock update has already been processed.', 'info')
        return redirect(url_for('builder_updates'))

    used_qty = float(update['material_used'])
    available_qty = float(update['available_quantity'])

    # Business Rule: Do not allow negative inventory!
    if used_qty > available_qty:
        flash(f'Cannot approve: Quantity used ({used_qty} {update["unit"]}) exceeds available master warehouse stock ({available_qty} {update["unit"]}). Please inward stock first.', 'danger')
        return redirect(url_for('builder_updates'))

    # Mark update as APPROVED
    query_db("""
        UPDATE stock_updates 
        SET status = 'APPROVED', reviewed_by = %s, review_date = NOW(), review_notes = %s
        WHERE stock_update_id = %s;
    """, (admin_id, review_notes, stock_update_id), commit=True)

    # Deduct used quantity from official master inventory
    if used_qty > 0:
        new_avail_stock = available_qty - used_qty
        query_db("UPDATE materials SET available_quantity = %s WHERE material_id = %s;", (new_avail_stock, update['material_id']), commit=True)

        # Record official OUT transaction
        total_cost = used_qty * float(update['unit_price'])
        purpose_text = f"Site Material Usage - {update['remarks'] or 'Construction Work'}"
        query_db("""
            INSERT INTO inventory_transactions
            (transaction_type, material_id, house_id, builder_id, quantity, unit_price, total_cost, transaction_date, purpose, notes, status)
            VALUES ('OUT', %s, %s, %s, %s, %s, %s, %s, %s, %s, 'COMPLETED');
        """, (update['material_id'], update['house_id'], update['builder_id'], used_qty, update['unit_price'], total_cost, update['update_date'], purpose_text, review_notes), commit=True)

    flash(f'Stock update for {update["material_name"]} APPROVED! Official inventory deducted and transaction logged.', 'success')
    return redirect(url_for('builder_updates'))

@app.route('/builder-updates/reject-stock/<int:stock_update_id>', methods=['POST'])
@admin_required
def reject_stock_update(stock_update_id):
    admin_id = session['user_id']
    review_notes = request.form.get('review_notes', 'Rejected by Administrator').strip()

    update = query_db("SELECT * FROM stock_updates WHERE stock_update_id = %s;", (stock_update_id,), one=True)
    if not update or update['status'] != 'PENDING':
        flash('Invalid update or already processed.', 'warning')
        return redirect(url_for('builder_updates'))

    query_db("""
        UPDATE stock_updates 
        SET status = 'REJECTED', reviewed_by = %s, review_date = NOW(), review_notes = %s
        WHERE stock_update_id = %s;
    """, (admin_id, review_notes, stock_update_id), commit=True)

    flash('Stock update has been REJECTED. No inventory was deducted.', 'info')
    return redirect(url_for('builder_updates'))

# -------------------------------------------------------------------
# Builder Accounts Management (Admin)
# -------------------------------------------------------------------
@app.route('/builders')
@admin_required
def builders():
    builders_list = query_db("""
        SELECT 
            b.builder_id, b.builder_name, b.email, b.phone, b.status, b.created_at,
            COUNT(DISTINCT bha.house_id) AS assigned_houses_count,
            GROUP_CONCAT(DISTINCT h.house_number SEPARATOR ', ') AS assigned_house_numbers
        FROM builders b
        LEFT JOIN builder_house_assignments bha ON b.builder_id = bha.builder_id AND bha.status = 'Active'
        LEFT JOIN houses h ON bha.house_id = h.house_id
        GROUP BY b.builder_id
        ORDER BY b.builder_name ASC;
    """)
    houses_list = query_db("SELECT house_id, house_number FROM houses ORDER BY house_number ASC;")
    return render_template('builders.html', builders=builders_list, houses=houses_list)

@app.route('/builders/add', methods=['POST'])
@admin_required
def add_builder():
    name = request.form.get('builder_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    status = request.form.get('status', 'Active').strip()

    if not name or not email or not phone or not password:
        flash('All fields are required.', 'warning')
        return redirect(url_for('builders'))

    dup = query_db("SELECT builder_id FROM builders WHERE email = %s;", (email,), one=True)
    if dup:
        flash(f'A builder with email "{email}" already exists.', 'danger')
        return redirect(url_for('builders'))

    pwd_hash = generate_password_hash(password)
    query_db("""
        INSERT INTO builders (builder_name, email, phone, password_hash, status)
        VALUES (%s, %s, %s, %s, %s);
    """, (name, email, phone, pwd_hash, status), commit=True)

    flash(f'Builder account for {name} created successfully.', 'success')
    return redirect(url_for('builders'))

@app.route('/builders/edit/<int:builder_id>', methods=['POST'])
@admin_required
def edit_builder(builder_id):
    name = request.form.get('builder_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    status = request.form.get('status', 'Active').strip()
    new_password = request.form.get('new_password', '').strip()

    dup = query_db("SELECT builder_id FROM builders WHERE email = %s AND builder_id != %s;", (email, builder_id), one=True)
    if dup:
        flash(f'Another builder is already using email "{email}".', 'danger')
        return redirect(url_for('builders'))

    if new_password:
        pwd_hash = generate_password_hash(new_password)
        query_db("""
            UPDATE builders 
            SET builder_name = %s, email = %s, phone = %s, status = %s, password_hash = %s
            WHERE builder_id = %s;
        """, (name, email, phone, status, pwd_hash, builder_id), commit=True)
    else:
        query_db("""
            UPDATE builders 
            SET builder_name = %s, email = %s, phone = %s, status = %s
            WHERE builder_id = %s;
        """, (name, email, phone, status, builder_id), commit=True)

    flash(f'Builder {name} updated successfully.', 'success')
    return redirect(url_for('builders'))

@app.route('/builders/toggle-status/<int:builder_id>', methods=['POST'])
@admin_required
def toggle_builder_status(builder_id):
    b = query_db("SELECT builder_name, status FROM builders WHERE builder_id = %s;", (builder_id,), one=True)
    if b:
        new_status = 'Inactive' if b['status'] == 'Active' else 'Active'
        query_db("UPDATE builders SET status = %s WHERE builder_id = %s;", (new_status, builder_id), commit=True)
        flash(f'Builder {b["builder_name"]} status changed to {new_status}.', 'info')
    return redirect(url_for('builders'))

# -------------------------------------------------------------------
# Supplier Management (Admin)
# -------------------------------------------------------------------
@app.route('/suppliers')
@admin_required
def suppliers():
    search = request.args.get('search', '').strip()
    sql = """
        SELECT s.*, COUNT(m.material_id) AS catalog_materials_count
        FROM suppliers s
        LEFT JOIN materials m ON s.supplier_id = m.supplier_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (s.supplier_name LIKE %s OR s.contact_person LIKE %s OR s.materials_supplied LIKE %s)"
        p = f"%{search}%"
        params.extend([p, p, p])

    sql += " GROUP BY s.supplier_id ORDER BY s.supplier_name ASC;"
    suppliers_list = query_db(sql, params)
    return render_template('suppliers.html', suppliers=suppliers_list, search=search)

@app.route('/suppliers/add', methods=['POST'])
@admin_required
def add_supplier():
    name = request.form.get('supplier_name', '').strip()
    contact = request.form.get('contact_person', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    materials_supplied = request.form.get('materials_supplied', '').strip()

    if not name or not contact or not phone:
        flash('Supplier name, contact person, and phone are required.', 'warning')
        return redirect(url_for('suppliers'))

    query_db("""
        INSERT INTO suppliers (supplier_name, contact_person, phone, email, address, materials_supplied)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (name, contact, phone, email, address, materials_supplied), commit=True)

    flash(f'Supplier "{name}" added successfully.', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/edit/<int:supplier_id>', methods=['POST'])
@admin_required
def edit_supplier(supplier_id):
    name = request.form.get('supplier_name', '').strip()
    contact = request.form.get('contact_person', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    materials_supplied = request.form.get('materials_supplied', '').strip()

    query_db("""
        UPDATE suppliers 
        SET supplier_name = %s, contact_person = %s, phone = %s, email = %s, address = %s, materials_supplied = %s
        WHERE supplier_id = %s;
    """, (name, contact, phone, email, address, materials_supplied, supplier_id), commit=True)

    flash(f'Supplier "{name}" updated successfully.', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:supplier_id>')
@admin_required
def supplier_details(supplier_id):
    supplier = query_db("SELECT * FROM suppliers WHERE supplier_id = %s;", (supplier_id,), one=True)
    if not supplier:
        flash('Supplier not found.', 'warning')
        return redirect(url_for('suppliers'))

    purchases = query_db("""
        SELECT 
            it.transaction_id, it.transaction_date, it.quantity, it.unit_price, it.total_cost, it.invoice_number, it.notes,
            m.material_name, m.unit, h.house_number
        FROM inventory_transactions it
        JOIN materials m ON it.material_id = m.material_id
        LEFT JOIN houses h ON it.house_id = h.house_id
        WHERE it.supplier_id = %s AND it.transaction_type = 'IN'
        ORDER BY it.transaction_date DESC;
    """, (supplier_id,))

    catalog_materials = query_db("SELECT * FROM materials WHERE supplier_id = %s ORDER BY material_name ASC;", (supplier_id,))

    return render_template('supplier_details.html', supplier=supplier, purchases=purchases, catalog_materials=catalog_materials)

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@admin_required
def delete_supplier(supplier_id):
    query_db("DELETE FROM suppliers WHERE supplier_id = %s;", (supplier_id,), commit=True)
    flash('Supplier deleted.', 'info')
    return redirect(url_for('suppliers'))

# -------------------------------------------------------------------
# Inventory Transaction History
# -------------------------------------------------------------------
@app.route('/transactions')
@admin_required
def transactions():
    mat_id = request.args.get('material_id', '').strip()
    house_id = request.args.get('house_id', '').strip()
    builder_id = request.args.get('builder_id', '').strip()
    supplier_id = request.args.get('supplier_id', '').strip()
    tx_type = request.args.get('type', '').strip()
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()

    sql = """
        SELECT 
            it.transaction_id, it.transaction_type, it.quantity, it.unit_price, it.total_cost,
            it.transaction_date, it.invoice_number, it.purpose, it.notes, it.status, it.created_at,
            m.material_name, m.unit, m.category,
            h.house_number,
            b.builder_name,
            s.supplier_name
        FROM inventory_transactions it
        JOIN materials m ON it.material_id = m.material_id
        LEFT JOIN houses h ON it.house_id = h.house_id
        LEFT JOIN builders b ON it.builder_id = b.builder_id
        LEFT JOIN suppliers s ON it.supplier_id = s.supplier_id
        WHERE 1=1
    """
    params = []

    if mat_id:
        sql += " AND it.material_id = %s"
        params.append(mat_id)
    if house_id:
        sql += " AND it.house_id = %s"
        params.append(house_id)
    if builder_id:
        sql += " AND it.builder_id = %s"
        params.append(builder_id)
    if supplier_id:
        sql += " AND it.supplier_id = %s"
        params.append(supplier_id)
    if tx_type in ('IN', 'OUT'):
        sql += " AND it.transaction_type = %s"
        params.append(tx_type)
    if from_date:
        sql += " AND it.transaction_date >= %s"
        params.append(from_date)
    if to_date:
        sql += " AND it.transaction_date <= %s"
        params.append(to_date)

    sql += " ORDER BY it.transaction_date DESC, it.transaction_id DESC;"

    transactions_list = query_db(sql, params)
    materials_list = query_db("SELECT material_id, material_name FROM materials ORDER BY material_name ASC;")
    houses_list = query_db("SELECT house_id, house_number FROM houses ORDER BY house_number ASC;")
    builders_list = query_db("SELECT builder_id, builder_name FROM builders ORDER BY builder_name ASC;")
    suppliers_list = query_db("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC;")

    total_in_qty = sum(float(t['quantity']) for t in transactions_list if t['transaction_type'] == 'IN')
    total_out_qty = sum(float(t['quantity']) for t in transactions_list if t['transaction_type'] == 'OUT')
    total_cost_sum = sum(float(t['total_cost']) for t in transactions_list)

    return render_template(
        'transactions.html',
        transactions=transactions_list,
        materials=materials_list,
        houses=houses_list,
        builders=builders_list,
        suppliers=suppliers_list,
        total_in_qty=total_in_qty,
        total_out_qty=total_out_qty,
        total_cost_sum=total_cost_sum,
        filter_material_id=mat_id,
        filter_house_id=house_id,
        filter_builder_id=builder_id,
        filter_supplier_id=supplier_id,
        filter_type=tx_type,
        from_date=from_date,
        to_date=to_date
    )

# -------------------------------------------------------------------
# Reports Module & CSV Exports
# -------------------------------------------------------------------
@app.route('/reports')
@admin_required
def reports():
    active_tab = request.args.get('tab', 'inventory')

    inventory_data = query_db("""
        SELECT 
            m.material_id, m.material_name, m.category, m.unit,
            m.available_quantity, m.minimum_stock_level, m.unit_price,
            (m.available_quantity * m.unit_price) AS total_value,
            s.supplier_name, m.storage_location,
            CASE 
                WHEN m.available_quantity <= 0 THEN 'OUT OF STOCK'
                WHEN m.available_quantity <= m.minimum_stock_level THEN 'LOW STOCK'
                ELSE 'AVAILABLE'
            END AS stock_status
        FROM materials m
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        ORDER BY m.category, m.material_name ASC;
    """)

    house_material_data = query_db("""
        SELECT 
            h.house_number, h.house_type, h.location, h.construction_stage, h.progress_pct,
            m.material_name, m.category, m.unit,
            mr.required_quantity,
            COALESCE((
                SELECT SUM(su.material_used)
                FROM stock_updates su
                WHERE su.house_id = mr.house_id 
                  AND su.material_id = mr.material_id 
                  AND su.status = 'APPROVED'
            ), 0) AS approved_used_quantity
        FROM material_requirements mr
        JOIN houses h ON mr.house_id = h.house_id
        JOIN materials m ON mr.material_id = m.material_id
        ORDER BY h.house_number ASC, m.material_name ASC;
    """)
    for item in house_material_data:
        item['remaining_quantity'] = max(0.0, float(item['required_quantity']) - float(item['approved_used_quantity']))
        if float(item['approved_used_quantity']) >= float(item['required_quantity']):
            item['status'] = 'COMPLETED'
        elif float(item['approved_used_quantity']) > 0:
            item['status'] = 'IN PROGRESS'
        else:
            item['status'] = 'PENDING'

    builder_updates_data = query_db("""
        (SELECT 
            'Construction Progress' AS update_type,
            b.builder_name, h.house_number,
            CONCAT('Stage: ', cu.stage, ' (', cu.progress_pct, '%) - ', COALESCE(cu.remarks, '')) AS details,
            cu.update_date, cu.status, cu.created_at
         FROM construction_updates cu
         JOIN builders b ON cu.builder_id = b.builder_id
         JOIN houses h ON cu.house_id = h.house_id)
        UNION ALL
        (SELECT 
            'Stock / Usage' AS update_type,
            b.builder_name, h.house_number,
            CONCAT(m.material_name, ' (Used: ', su.material_used, ' ', m.unit, ', Remaining: ', su.remaining_stock, ') - ', COALESCE(su.remarks, '')) AS details,
            su.update_date, su.status, su.created_at
         FROM stock_updates su
         JOIN builders b ON su.builder_id = b.builder_id
         JOIN houses h ON su.house_id = h.house_id
         JOIN materials m ON su.material_id = m.material_id)
        ORDER BY update_date DESC, created_at DESC;
    """)

    transactions_data = query_db("""
        SELECT 
            it.transaction_id, it.transaction_date, it.transaction_type,
            m.material_name, m.unit, it.quantity, it.unit_price, it.total_cost,
            h.house_number, s.supplier_name, b.builder_name, it.purpose, it.status
        FROM inventory_transactions it
        JOIN materials m ON it.material_id = m.material_id
        LEFT JOIN houses h ON it.house_id = h.house_id
        LEFT JOIN suppliers s ON it.supplier_id = s.supplier_id
        LEFT JOIN builders b ON it.builder_id = b.builder_id
        ORDER BY it.transaction_date DESC, it.transaction_id DESC;
    """)

    return render_template(
        'reports.html',
        active_tab=active_tab,
        inventory_data=inventory_data,
        house_material_data=house_material_data,
        builder_updates_data=builder_updates_data,
        transactions_data=transactions_data,
        report_date=date.today().strftime('%d-%m-%Y')
    )

@app.route('/reports/export-csv/<report_type>')
@admin_required
def export_csv(report_type):
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'inventory':
        writer.writerow(['Material ID', 'Material Name', 'Category', 'Unit', 'Available Quantity', 'Min Stock Level', 'Unit Price', 'Stock Value', 'Status', 'Supplier', 'Storage Location'])
        rows = query_db("""
            SELECT m.material_id, m.material_name, m.category, m.unit, m.available_quantity, m.minimum_stock_level, m.unit_price,
                   (m.available_quantity * m.unit_price) AS total_value,
                   CASE 
                       WHEN m.available_quantity <= 0 THEN 'OUT OF STOCK'
                       WHEN m.available_quantity <= m.minimum_stock_level THEN 'LOW STOCK'
                       ELSE 'AVAILABLE'
                   END AS stock_status,
                   s.supplier_name, m.storage_location
            FROM materials m
            LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
            ORDER BY m.category, m.material_name ASC;
        """)
        for r in rows:
            writer.writerow([r['material_id'], r['material_name'], r['category'], r['unit'], r['available_quantity'], r['minimum_stock_level'], r['unit_price'], r['total_value'], r['stock_status'], r['supplier_name'] or '', r['storage_location'] or ''])
        filename = f"Inventory_Report_{date.today().strftime('%Y%m%d')}.csv"

    elif report_type == 'house-materials':
        writer.writerow(['House Number', 'House Type', 'Location', 'Stage', 'Progress %', 'Material Name', 'Category', 'Unit', 'Required Quantity', 'Approved Used', 'Remaining', 'Requirement Status'])
        rows = query_db("""
            SELECT h.house_number, h.house_type, h.location, h.construction_stage, h.progress_pct,
                   m.material_name, m.category, m.unit, mr.required_quantity,
                   COALESCE((
                       SELECT SUM(su.material_used)
                       FROM stock_updates su
                       WHERE su.house_id = mr.house_id 
                         AND su.material_id = mr.material_id 
                         AND su.status = 'APPROVED'
                   ), 0) AS approved_used_quantity
            FROM material_requirements mr
            JOIN houses h ON mr.house_id = h.house_id
            JOIN materials m ON mr.material_id = m.material_id
            ORDER BY h.house_number ASC, m.material_name ASC;
        """)
        for r in rows:
            rem = max(0.0, float(r['required_quantity']) - float(r['approved_used_quantity']))
            status = 'COMPLETED' if float(r['approved_used_quantity']) >= float(r['required_quantity']) else ('IN PROGRESS' if float(r['approved_used_quantity']) > 0 else 'PENDING')
            writer.writerow([r['house_number'], r['house_type'], r['location'], r['construction_stage'], f"{r['progress_pct']}%", r['material_name'], r['category'], r['unit'], r['required_quantity'], r['approved_used_quantity'], rem, status])
        filename = f"House_Material_Report_{date.today().strftime('%Y%m%d')}.csv"

    elif report_type == 'builder-updates':
        writer.writerow(['Update Type', 'Builder Name', 'House Number', 'Details', 'Update Date', 'Status'])
        rows = query_db("""
            (SELECT 'Construction Progress' AS update_type, b.builder_name, h.house_number,
                    CONCAT('Stage: ', cu.stage, ' (', cu.progress_pct, '%) - ', COALESCE(cu.remarks, '')) AS details,
                    cu.update_date, cu.status
             FROM construction_updates cu
             JOIN builders b ON cu.builder_id = b.builder_id
             JOIN houses h ON cu.house_id = h.house_id)
            UNION ALL
            (SELECT 'Stock / Usage' AS update_type, b.builder_name, h.house_number,
                    CONCAT(m.material_name, ' (Used: ', su.material_used, ' ', m.unit, ', Remaining: ', su.remaining_stock, ') - ', COALESCE(su.remarks, '')) AS details,
                    su.update_date, su.status
             FROM stock_updates su
             JOIN builders b ON su.builder_id = b.builder_id
             JOIN houses h ON su.house_id = h.house_id
             JOIN materials m ON su.material_id = m.material_id)
            ORDER BY update_date DESC;
        """)
        for r in rows:
            writer.writerow([r['update_type'], r['builder_name'], r['house_number'], r['details'], r['update_date'], r['status']])
        filename = f"Builder_Updates_Report_{date.today().strftime('%Y%m%d')}.csv"

    elif report_type == 'transactions':
        writer.writerow(['Transaction ID', 'Date', 'Type', 'Material Name', 'Unit', 'Quantity', 'Unit Price', 'Total Cost', 'House Number', 'Supplier', 'Builder', 'Purpose', 'Status'])
        rows = query_db("""
            SELECT it.transaction_id, it.transaction_date, it.transaction_type,
                   m.material_name, m.unit, it.quantity, it.unit_price, it.total_cost,
                   h.house_number, s.supplier_name, b.builder_name, it.purpose, it.status
            FROM inventory_transactions it
            JOIN materials m ON it.material_id = m.material_id
            LEFT JOIN houses h ON it.house_id = h.house_id
            LEFT JOIN suppliers s ON it.supplier_id = s.supplier_id
            LEFT JOIN builders b ON it.builder_id = b.builder_id
            ORDER BY it.transaction_date DESC, it.transaction_id DESC;
        """)
        for r in rows:
            writer.writerow([r['transaction_id'], r['transaction_date'], r['transaction_type'], r['material_name'], r['unit'], r['quantity'], r['unit_price'], r['total_cost'], r['house_number'] or '', r['supplier_name'] or '', r['builder_name'] or '', r['purpose'] or '', r['status']])
        filename = f"Transactions_Ledger_{date.today().strftime('%Y%m%d')}.csv"
    else:
        return "Invalid report type", 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/reports/download-pdf')
@admin_required
def download_pdf_report():
    from generate_pdf_report import build_pdf
    from flask import send_file
    basedir = os.path.abspath(os.path.dirname(__file__))
    pdf_path = os.path.join(basedir, 'BuildTrack_Full_Executive_Report.pdf')
    build_pdf(pdf_path)
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"BuildTrack_Executive_Report_{date.today().strftime('%Y%m%d')}.pdf"
    )

# -------------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    server_port = app.config.get('PORT', 5001)
    print("================================================================")
    print(" BuildTrack Real Estate Inventory & Construction Management")
    print(f" Running at: http://127.0.0.1:{server_port}")
    print(" Admin Login: admin@buildtrack.com / Admin@123")
    print(" Builder Login: kumar@buildtrack.com / Builder@123")
    print("================================================================")
    app.run(host='127.0.0.1', port=server_port, debug=True)
