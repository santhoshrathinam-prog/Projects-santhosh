from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    """
    Decorator to ensure user is logged in before accessing a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Decorator to restrict route access to specific user roles.
    Example: @role_required('admin') or @role_required('farmer', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.path))
            
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash(f'Access denied. This page is restricted to {", ".join(allowed_roles)}.', 'danger')
                
                # Redirect to appropriate dashboard based on actual role
                if user_role == 'farmer':
                    return redirect(url_for('farmer_dashboard'))
                elif user_role == 'customer':
                    return redirect(url_for('customer_dashboard'))
                elif user_role == 'delivery_partner':
                    return redirect(url_for('delivery_dashboard'))
                elif user_role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
