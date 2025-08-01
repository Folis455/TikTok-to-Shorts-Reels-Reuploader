#!/usr/bin/env python3
"""
TikTok to Shorts/Reels Uploader 2025
Script principal para ejecutar la aplicación
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio actual al path de Python
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Configura el entorno necesario para la aplicación"""
    
    # Crear directorios necesarios
    directories = ['uploads', 'downloads', 'temp', 'logs', 'static', 'templates']
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Directorio creado/verificado: {dir_path}")
    
    # Verificar variables de entorno críticas
    required_env_vars = []
    optional_env_vars = [
        'YOUTUBE_CLIENT_ID',
        'YOUTUBE_CLIENT_SECRET', 
        'INSTAGRAM_ACCESS_TOKEN',
        'INSTAGRAM_USER_ID'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        logger.error("Por favor configura las variables de entorno antes de continuar")
    
    # Verificar variables opcionales
    missing_optional = []
    for var in optional_env_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        logger.warning(f"Variables de entorno opcionales no configuradas: {', '.join(missing_optional)}")
        logger.warning("Algunas funcionalidades pueden no estar disponibles")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    
    try:
        import flask
        import yt_dlp
        import requests
        import PIL
        logger.info("✓ Dependencias de Python verificadas")
    except ImportError as e:
        logger.error(f"✗ Dependencia faltante: {e}")
        logger.error("Ejecuta: pip install -r requirements.txt")
        return False
    
    # Verificar FFmpeg
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("✓ FFmpeg encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("✗ FFmpeg no encontrado")
        logger.error("Instala FFmpeg desde https://ffmpeg.org/")
        return False
    
    return True

def print_banner():
    """Imprime el banner de la aplicación"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║     🚀 TikTok to Shorts/Reels Uploader 2025         ║
    ║                                                      ║
    ║     Resube tus TikToks a YouTube Shorts e           ║
    ║     Instagram Reels manteniendo la calidad          ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Función principal"""
    
    # Mostrar banner
    print_banner()
    
    # Configurar entorno
    logger.info("Configurando entorno...")
    setup_environment()
    
    # Verificar dependencias
    logger.info("Verificando dependencias...")
    if not check_dependencies():
        logger.error("❌ Faltan dependencias críticas. Abortando.")
        sys.exit(1)
    
    # Importar y configurar la aplicación
    try:
        from app import app
        from config import get_config
        
        config = get_config()
        app.config.from_object(config)
        
        # Configurar logging de la aplicación
        if not app.debug:
            import logging
            from logging.handlers import RotatingFileHandler
            
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/uploader.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('TikTok Uploader startup')
        
        # Información de configuración
        logger.info("✓ Aplicación configurada correctamente")
        logger.info(f"✓ Modo debug: {app.debug}")
        logger.info(f"✓ Puerto: {os.getenv('PORT', 5000)}")
        
        # Verificar configuración de APIs
        youtube_configured = all([
            config.YOUTUBE_CLIENT_ID,
            config.YOUTUBE_CLIENT_SECRET
        ])
        
        instagram_configured = all([
            config.INSTAGRAM_ACCESS_TOKEN,
            config.INSTAGRAM_USER_ID
        ])
        
        if youtube_configured:
            logger.info("✓ YouTube API configurada")
        else:
            logger.warning("⚠ YouTube API no configurada")
        
        if instagram_configured:
            logger.info("✓ Instagram API configurada")
        else:
            logger.warning("⚠ Instagram API no configurada")
        
        if not youtube_configured and not instagram_configured:
            logger.warning("⚠ No hay APIs configuradas. Solo funcionará la descarga.")
        
        # Ejecutar aplicación
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        
        logger.info(f"🚀 Iniciando servidor en http://{host}:{port}")
        logger.info("📱 Presiona Ctrl+C para detener el servidor")
        
        app.run(
            host=host,
            port=port,
            debug=app.debug,
            threaded=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Error importando la aplicación: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error ejecutando la aplicación: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 