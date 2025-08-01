import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Directorios
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
    
    # Límites de archivos
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_VIDEO_SIZE_MB', 500)) * 1024 * 1024  # MB a bytes
    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION_SECONDS', 600))  # segundos
    
    # YouTube API
    YOUTUBE_CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
    YOUTUBE_REFRESH_TOKEN = os.environ.get('YOUTUBE_REFRESH_TOKEN')
    YOUTUBE_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'youtube_credentials.json')
    YOUTUBE_TOKEN_FILE = os.path.join(BASE_DIR, 'youtube_token.pickle')
    
    # Instagram API
    INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_USER_ID = os.environ.get('INSTAGRAM_USER_ID')
    INSTAGRAM_APP_ID = os.environ.get('INSTAGRAM_APP_ID')
    INSTAGRAM_APP_SECRET = os.environ.get('INSTAGRAM_APP_SECRET')
    
    # Redis (para colas de tareas)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Proxy settings
    HTTP_PROXY = os.environ.get('HTTP_PROXY')
    HTTPS_PROXY = os.environ.get('HTTPS_PROXY')
    
    # Telegram (notificaciones opcionales)
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    
    # Configuraciones de plataformas
    PLATFORM_CONFIGS = {
        'youtube_shorts': {
            'max_duration': 180,  # 3 minutos en 2025
            'max_file_size': 256 * 1024 * 1024,  # 256MB
            'resolution': {'width': 1080, 'height': 1920},  # 9:16
            'bitrate': '8000k',
            'fps': 30,
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'h264',
            'title_max_length': 100,
            'description_max_length': 5000,
            'tags_max_count': 30
        },
        'instagram_reels': {
            'max_duration': 180,  # 3 minutos en 2025
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'resolution': {'width': 1080, 'height': 1920},  # 9:16
            'bitrate': '6000k',
            'fps': 30,
            'audio_bitrate': '128k',
            'format': 'mp4',
            'codec': 'h264',
            'caption_max_length': 2200,
            'hashtags_max_count': 30
        }
    }
    
    # Configuración de yt-dlp
    YT_DLP_OPTIONS = {
        'format': 'best[ext=mp4]',
        'writeinfojson': True,
        'writethumbnail': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
        'no_warnings': False,
        'extractflat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    # FFmpeg configuración
    FFMPEG_OPTIONS = {
        'video_codec': 'libx264',
        'audio_codec': 'aac',
        'preset': 'slow',  # Mejor calidad
        'crf': '18',  # Calidad alta (0-51, menor = mejor)
        'pix_fmt': 'yuv420p',  # Compatibilidad
        'movflags': '+faststart'  # Para streaming
    }
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'uploader.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuración de tareas
    TASK_TIMEOUT = 1800  # 30 minutos
    TASK_RETRY_COUNT = 3
    TASK_RETRY_DELAY = 60  # segundos
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() in ['true', '1', 'yes']
    RATE_LIMIT_REQUESTS = int(os.environ.get('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 3600))  # 1 hora
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutos

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    
    # Configuraciones más permisivas para desarrollo
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
    TASK_TIMEOUT = 3600  # 1 hora
    
    # Logging más detallado
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
    # Configuraciones más estrictas para producción
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    TASK_TIMEOUT = 1800  # 30 minutos
    
    # Rate limiting más estricto
    RATE_LIMIT_REQUESTS = 50
    RATE_LIMIT_WINDOW = 3600  # 1 hora
    
    # Logging menos verboso
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Configuraciones para tests
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    TASK_TIMEOUT = 60  # 1 minuto
    
    # Deshabilitar rate limiting para tests
    RATE_LIMIT_ENABLED = False

# Configuración por defecto basada en la variable de entorno
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración basada en la variable de entorno FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'default').lower()
    return config_mapping.get(env, DevelopmentConfig) 