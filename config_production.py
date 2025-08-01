import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database settings (if needed)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    UPLOAD_FOLDER = 'uploads'
    DOWNLOAD_FOLDER = 'downloads'
    
    # API Keys (set these in Render environment variables)
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')
    
    # Redis settings (if using Redis)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # Logging
    LOG_LEVEL = 'INFO' 