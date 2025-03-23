from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.models import db, User
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

# ---------------------- User Signup ----------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Registers a new user and stores a hashed password."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "patient")  # Default role: "patient"

    # Validate input
    if not username or not password or role not in ["admin", "doctor", "patient"]:
        return jsonify({"error": "Invalid input"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    # Create new user
    new_user = User(username=username, role=role)
    new_user.set_password(password)

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# ---------------------- User Login ----------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates a user and returns a JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Validate input
    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    # Check user exists
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate JWT token (includes user role)
    access_token = create_access_token(identity={"username": user.username, "role": user.role}, expires_delta=timedelta(hours=1))

    return jsonify({"access_token": access_token, "role": user.role}), 200
