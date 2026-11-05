import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-key-change-me-in-production-long-secure-key-1234567890")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-insecure-jwt-key-change-me-in-production-long-secure-key-1234567890")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    # Razorpay configurations
    RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
    
    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
        if origin.strip()
    ]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    # Default to SQLite for zero-setup local dev if DATABASE_URL not set
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///ecommerce.db"
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecommerce_db"
    )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
