from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
from models.users import (
    register_user, login_user, get_all_users, delete_user, count_admins,
)
import sqlite3
import config
import os

auth_routes = Blueprint('auth_routes', __name__)


# ---------------------------------------------------------------------------
# Access-control decorators (used across all routes)
# ---------------------------------------------------------------------------

def login_required(f):
    """Block access unless someone is logged in.

    Page requests get redirected to the login screen; API requests get a clean
    401 so the browser code can react.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"message": "Please log in"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Only allow the admin through. Others get a friendly 'not allowed'."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get('user')
        if not user:
            if request.path.startswith('/api/'):
                return jsonify({"message": "Please log in"}), 401
            return redirect(url_for('login'))
        if not user.get('is_admin'):
            if request.path.startswith('/api/'):
                return jsonify({"message": "Only the admin can do this"}), 403
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------

@auth_routes.route("/api/register", methods=['POST'])
def register():
    return jsonify({"message": "Registration disabled"}), 403


@auth_routes.route("/api/login", methods=['POST'])
def login():
    data = request.get_json()

    user = login_user(
        phone=data['phone'],
        password=data['password']
    )

    if user:
        session.permanent = True
        session['user'] = {
            "name": user['name'],
            "phone": user['phone'],
            "is_admin": bool(user.get('is_admin')),
        }
        return jsonify({
            "message": "Login successful",
            "user": session['user']
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@auth_routes.route("/api/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


# ---------------------------------------------------------------------------
# Admin: manage users (mom & sister logins)
# ---------------------------------------------------------------------------

@auth_routes.route("/api/users", methods=['GET'])
@admin_required
def list_users():
    return jsonify(get_all_users())


@auth_routes.route("/api/add-user", methods=['POST'])
@admin_required
def add_user():
    data = request.get_json()
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    password = data.get('password') or ''
    is_admin = 1 if data.get('is_admin') else 0

    if not name or not phone or not password:
        return jsonify({"message": "Name, phone and password are all required"}), 400

    created = register_user(name, phone, password, is_admin=is_admin)
    if not created:
        return jsonify({"message": "That phone number is already used"}), 400

    return jsonify({"message": "User added"})


@auth_routes.route("/api/delete-user/<int:user_id>", methods=['DELETE'])
@admin_required
def remove_user(user_id):
    # Look up the user being deleted.
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, is_admin FROM users WHERE id = ?", (user_id,))
    target = cursor.fetchone()
    conn.close()

    if not target:
        return jsonify({"message": "User not found"}), 404

    # Don't let the admin delete their own account.
    if target['phone'] == session['user']['phone']:
        return jsonify({"message": "You cannot delete your own account"}), 400

    # Never remove the last admin.
    if target['is_admin'] and count_admins() <= 1:
        return jsonify({"message": "Cannot delete the only admin"}), 400

    delete_user(user_id)
    return jsonify({"message": "User removed"})


def create_admin_user():
    """Seed (or promote) the admin account from environment variables on startup."""
    admin = os.environ.get("ADMIN")
    phone = os.environ.get("PHONE")
    password = os.environ.get("APP_PASSWORD")

    if not (admin and phone and password):
        return

    created = register_user(admin, phone, password, is_admin=1)
    if not created:
        # User already exists — make sure they're flagged as admin.
        conn = sqlite3.connect(config.DB_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE phone = ?", (phone,))
        conn.commit()
        conn.close()
