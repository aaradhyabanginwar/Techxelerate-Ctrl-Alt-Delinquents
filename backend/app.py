from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # For handling cross-origin requests
from werkzeug.exceptions import HTTPException
from backend.models import db
from backend import create_app
from backend.auth import auth_bp
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # ---------------- CONFIGURATION ----------------
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "APP.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_fallback_secret_key')  # Change this for production
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # Token expires in 1 hour

    # Enable CORS (Cross-Origin Resource Sharing)
    CORS(app)

    # ---------------- INITIALIZE EXTENSIONS ----------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    from backend.routes import api_bp
    from backend.auth import auth_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # ---------------- ERROR HANDLING ----------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global error handler for unexpected exceptions"""
        if isinstance(e, HTTPException):
            return jsonify({"error": e.description}), e.code
        return jsonify({"error": "Internal Server Error"}), 500

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors (resource not found)"""
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors (bad request)"""
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors (unauthorized access)"""
        return jsonify({"error": "Unauthorized"}), 401

    # ---------------- SHELL CONTEXT ----------------
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}

    # ---------------- ROUTES ----------------
    @app.route('/')
    def home():
        return jsonify({"message": "API is working with JWT authentication!"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
