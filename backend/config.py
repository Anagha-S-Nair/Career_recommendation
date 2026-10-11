"""
Database and Application Configuration Module.
Configures SQLAlchemy to connect to MySQL 8.x Server using mysql-connector-python / PyMySQL.
Designed for MySQL Server and MySQL Workbench management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')


def build_mysql_uri():
    """Builds standard MySQL SQLAlchemy connection URI from environment variables."""
    # Direct DATABASE_URL override if provided in .env
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith('mysql'):
        return db_url

    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'abc123')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'career_recommendation_db')
    driver = os.getenv('DB_DRIVER', 'mysqlconnector')

    if password:
        return f"mysql+{driver}://{user}:{password}@{host}:{port}/{db_name}"
    else:
        return f"mysql+{driver}://{user}@{host}:{port}/{db_name}"


class Config:
    """Base application configuration for MySQL Server."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-in-production-dev-key')

    # MySQL Database Connection URI
    SQLALCHEMY_DATABASE_URI = build_mysql_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }

    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Template and Static paths
    TEMPLATE_FOLDER = str(BASE_DIR / 'frontend' / 'templates')
    STATIC_FOLDER = str(BASE_DIR / 'frontend' / 'static')

    # Production ML Model Configuration Paths
    MODEL_DIR = str(BASE_DIR / 'backend' / 'ml' / 'models')
    CAREER_DATA_PATH = str(BASE_DIR / 'backend' / 'ml' / 'data' / 'career_knowledge_requirements.csv')


class DevelopmentConfig(Config):
    """Development configuration for MySQL."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration for automated unit test isolation."""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
