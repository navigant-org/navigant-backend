from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import jwt, datetime
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode(
        {
            "user_id": user.user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        },
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user": {
            "id": user.user_id,
            "name": user.name,
            "email": user.email
        }
    }), 200
    
@auth_bp.route('/register-admin', methods=['POST'])
def register_admin():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data or 'name' not in data or 'phone' not in data:
        return jsonify({"error": "Please fill all required fields"}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409

    new_user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        password_hash=generate_password_hash(data['password'])
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Admin user registered successfully",
        "user": {
            "id": new_user.user_id,
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone
        }
    }), 201