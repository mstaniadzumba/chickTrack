from flask import Blueprint, request, jsonify
from models.users import register_user, login_user

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/api/register", methods=['POST'])
def register():
    data = request.get_json()
    
    success = register_user(
        name=data['name'],
        phone=data['phone'],
        password=data['password']
    )
    
    if success:
        return jsonify({"message": "Registration successful"})
    else:
        return jsonify({"message": "Phone number already exists"}), 400

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