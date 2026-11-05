import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from backend.app.config.config import config_by_name
from backend.app.models.base import db
import backend.app.models  # Register all 20 models

jwt = JWTManager()
migrate = Migrate()

def create_app(config_name: str = "development") -> Flask:
    """Application factory for the e-commerce platform."""
    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        supports_credentials=True,
    )

    # Register blueprints
    from backend.app.routes.auth_routes import auth_bp
    from backend.app.routes.user_routes import user_bp
    from backend.app.routes.catalog_routes import catalog_bp
    from backend.app.routes.cart_routes import cart_bp
    from backend.app.routes.order_routes import order_bp
    from backend.app.routes.payment_routes import payment_bp
    from backend.app.routes.review_routes import review_bp
    from backend.app.routes.admin_routes import admin_bp
    from backend.app.routes.recommendation_routes import recommendation_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(recommendation_bp)

    # Root & Healthcheck endpoints
    @app.route("/", methods=["GET"])
    def root_status():
        return jsonify({
            "status": "online",
            "message": "ApexStore E-Commerce & AI Recommendation REST API",
            "frontend_url": "http://localhost:5173",
            "health_check": "/api/health",
            "version": "1.0.0",
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "environment": config_name,
            "version": "1.0.0",
        }), 200

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "message": "Bad request", "errors": [str(error)]}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "message": "The requested endpoint was not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "message": "Method not allowed on this endpoint"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "message": "An internal server error occurred"}), 500

    return app
