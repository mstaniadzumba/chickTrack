from flask import Blueprint, request, jsonify
from models.users import register_user, login_user
import os

auth_routes = Blueprint('auth_routes', __name__)

# register_user(os.environ.get("ADMIN"), os.environ.get("PHONE"), os.environ.get("APP_PASSWORD"))

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
        return jsonify({
            "message": "Login successful",
            "user": {"name": user['name'], "phone": user['phone']}
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
def create_admin_user():
    admin = os.environ.get("ADMIN")
    phone = os.environ.get("PHONE")
    password = os.environ.get("APP_PASSWORD")

    if admin and phone and password:
        register_user(admin, phone, password)