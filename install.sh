#!/bin/bash

# TikTok to Shorts/Reels Uploader 2025 - Script de instalación
# Compatible con Linux y macOS

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
show_banner() {
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                                                      ║"
    echo "║     🚀 TikTok to Shorts/Reels Uploader 2025         ║"
    echo "║                                                      ║"
    echo "║            Script de Instalación Automática         ║"
    echo "║                                                      ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
}

# Detectar sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            DISTRO="debian"
        elif command -v yum &> /dev/null; then
            DISTRO="redhat"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        OS="unknown"
        DISTRO="unknown"
    fi
    
    print_status "Sistema detectado: $OS ($DISTRO)"
}

# Verificar si un comando existe
command_exists() {
    command -v "$1" &> /dev/null
}

# Instalar Python y pip
install_python() {
    print_status "Verificando instalación de Python..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python3 ya está instalado: $PYTHON_VERSION"
        
        # Verificar versión mínima (3.8)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
            print_success "Versión de Python es compatible (>=3.8)"
        else
            print_error "Versión de Python demasiado antigua. Se requiere Python 3.8 o superior."
            exit 1
        fi
    else
        print_status "Instalando Python3..."
        
        case $DISTRO in
            "debian")
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            "redhat")
                sudo yum install -y python3 python3-pip
                ;;
            "macos")
                if command_exists brew; then
                    brew install python3
                else
                    print_error "Homebrew no encontrado. Instala Python3 manualmente desde python.org"
                    exit 1
                fi
                ;;
            *)
                print_error "Distribución no soportada. Instala Python3 manualmente."
                exit 1
                ;;
        esac
        
        print_success "Python3 instalado correctamente"
    fi
    
    # Verificar pip
    if command_exists pip3; then
        print_success "pip3 ya está instalado"
    else
        print_status "Instalando pip3..."
        python3 -m ensurepip --upgrade
    fi
}

# Instalar FFmpeg
install_ffmpeg() {
    print_status "Verificando instalación de FFmpeg..."
    
    if command_exists ffmpeg; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
        print_success "FFmpeg ya está instalado: $FFMPEG_VERSION"
    else
        print_status "Instalando FFmpeg..."
        
        case $DISTRO in
            "debian")
                sudo apt-get update
                sudo apt-get install -y ffmpeg
                ;;
            "redhat")
                sudo yum install -y epel-release
                sudo yum install -y ffmpeg
                ;;
            "macos")
                if command_exists brew; then
                    brew install ffmpeg
                else
                    print_error "Homebrew no encontrado. Instala FFmpeg manualmente."
                    exit 1
                fi
                ;;
            *)
                print_error "Distribución no soportada. Instala FFmpeg manualmente."
                exit 1
                ;;
        esac
        
        print_success "FFmpeg instalado correctamente"
    fi
}

# Instalar Redis (opcional)
install_redis() {
    print_status "Verificando instalación de Redis..."
    
    if command_exists redis-server; then
        print_success "Redis ya está instalado"
    else
        read -p "¿Deseas instalar Redis para colas de tareas? (y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Instalando Redis..."
            
            case $DISTRO in
                "debian")
                    sudo apt-get update
                    sudo apt-get install -y redis-server
                    sudo systemctl enable redis-server
                    sudo systemctl start redis-server
                    ;;
                "redhat")
                    sudo yum install -y redis
                    sudo systemctl enable redis
                    sudo systemctl start redis
                    ;;
                "macos")
                    if command_exists brew; then
                        brew install redis
                        brew services start redis
                    else
                        print_warning "Homebrew no encontrado. Instala Redis manualmente si es necesario."
                    fi
                    ;;
                *)
                    print_warning "Distribución no soportada para instalación automática de Redis."
                    ;;
            esac
            
            print_success "Redis instalado y configurado"
        else
            print_warning "Redis no instalado. Las colas de tareas no estarán disponibles."
        fi
    fi
}

# Crear entorno virtual y instalar dependencias
setup_python_environment() {
    print_status "Configurando entorno virtual de Python..."
    
    # Crear entorno virtual
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Entorno virtual creado"
    else
        print_success "Entorno virtual ya existe"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    print_status "Actualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependencias
    print_status "Instalando dependencias de Python..."
    pip install -r requirements.txt
    
    print_success "Dependencias instaladas correctamente"
}

# Configurar archivos de configuración
setup_configuration() {
    print_status "Configurando archivos de configuración..."
    
    # Crear archivo .env si no existe
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Archivo .env creado desde .env.example"
            print_warning "¡IMPORTANTE! Edita el archivo .env con tus credenciales antes de usar la aplicación."
        else
            print_warning "Archivo .env.example no encontrado. Deberás crear .env manualmente."
        fi
    else
        print_success "Archivo .env ya existe"
    fi
    
    # Crear directorios necesarios
    mkdir -p uploads downloads temp logs static/css static/js templates
    print_success "Directorios de la aplicación creados"
}

# Verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Verificar que se puede importar la aplicación
    if python3 -c "import app; print('✓ Aplicación importada correctamente')" 2>/dev/null; then
        print_success "Verificación de la aplicación exitosa"
    else
        print_error "Error al verificar la aplicación"
        return 1
    fi
    
    # Verificar dependencias críticas
    if python3 -c "import yt_dlp, flask, requests, PIL; print('✓ Dependencias verificadas')" 2>/dev/null; then
        print_success "Verificación de dependencias exitosa"
    else
        print_error "Error al verificar dependencias"
        return 1
    fi
    
    # Verificar FFmpeg
    if command_exists ffmpeg; then
        print_success "FFmpeg verificado"
    else
        print_error "FFmpeg no encontrado"
        return 1
    fi
    
    return 0
}

# Mostrar instrucciones finales
show_final_instructions() {
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                   ✅ INSTALACIÓN COMPLETA             ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 PRÓXIMOS PASOS:"
    echo ""
    echo "1. Configura tus credenciales de API en el archivo .env:"
    echo "   nano .env"
    echo ""
    echo "2. Activa el entorno virtual:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Ejecuta la aplicación:"
    echo "   python3 run.py"
    echo "   # o usando el script simplificado:"
    echo "   python3 app.py"
    echo ""
    echo "4. Abre tu navegador en:"
    echo "   http://localhost:5000"
    echo ""
    echo "📖 DOCUMENTACIÓN:"
    echo "   - README.md para guía completa"
    echo "   - config.py para configuración avanzada"
    echo ""
    echo "🆘 SOPORTE:"
    echo "   - GitHub Issues: https://github.com/tu-usuario/tiktok-uploader/issues"
    echo "   - Email: soporte@tiktok-uploader.com"
    echo ""
    echo "¡Gracias por usar TikTok to Shorts/Reels Uploader 2025! 🚀"
}

# Función principal
main() {
    show_banner
    
    # Verificar si estamos en el directorio correcto
    if [ ! -f "requirements.txt" ] || [ ! -f "app.py" ]; then
        print_error "Este script debe ejecutarse desde el directorio raíz del proyecto."
        print_error "Asegúrate de que los archivos requirements.txt y app.py estén presentes."
        exit 1
    fi
    
    print_status "Iniciando instalación..."
    
    # Detectar sistema operativo
    detect_os
    
    if [ "$OS" == "unknown" ]; then
        print_error "Sistema operativo no soportado. Este script funciona en Linux y macOS."
        exit 1
    fi
    
    # Instalar componentes
    install_python
    install_ffmpeg
    install_redis
    setup_python_environment
    setup_configuration
    
    # Verificar instalación
    if verify_installation; then
        show_final_instructions
    else
        print_error "La verificación de la instalación falló."
        print_error "Revisa los errores anteriores y corrige los problemas."
        exit 1
    fi
}

# Verificar si se ejecuta como script principal
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi 