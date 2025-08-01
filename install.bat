@echo off
:: TikTok to Shorts/Reels Uploader 2025 - Script de instalación para Windows
:: Requiere Windows 10 o superior

setlocal enabledelayedexpansion
color 0A

:: Banner
echo ╔══════════════════════════════════════════════════════╗
echo ║                                                      ║
echo ║     🚀 TikTok to Shorts/Reels Uploader 2025         ║
echo ║                                                      ║
echo ║            Script de Instalación Windows            ║
echo ║                                                      ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Verificar si estamos en el directorio correcto
if not exist "requirements.txt" (
    echo [ERROR] Este script debe ejecutarse desde el directorio raíz del proyecto.
    echo [ERROR] Asegúrate de que el archivo requirements.txt esté presente.
    pause
    exit /b 1
)

if not exist "app.py" (
    echo [ERROR] Archivo app.py no encontrado.
    echo [ERROR] Asegúrate de estar en el directorio correcto del proyecto.
    pause
    exit /b 1
)

echo [INFO] Iniciando instalación...
echo.

:: Verificar Python
echo [INFO] Verificando instalación de Python...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo [INFO] Descarga Python desde: https://www.python.org/downloads/
    echo [INFO] Asegúrate de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
    echo [SUCCESS] Python encontrado: !PYTHON_VERSION!
)

:: Verificar versión mínima de Python (3.8)
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Se requiere Python 3.8 o superior.
    echo [ERROR] Tu versión actual: !PYTHON_VERSION!
    pause
    exit /b 1
) else (
    echo [SUCCESS] Versión de Python compatible
)

:: Verificar pip
echo [INFO] Verificando pip...
pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] pip no está instalado o no está en el PATH.
    echo [INFO] Instalando pip...
    python -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo instalar pip.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] pip encontrado
)

:: Verificar FFmpeg
echo [INFO] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] FFmpeg no encontrado en el PATH.
    echo [INFO] Opciones para instalar FFmpeg:
    echo [INFO] 1. Chocolatey: choco install ffmpeg
    echo [INFO] 2. Descargar desde: https://ffmpeg.org/download.html
    echo [INFO] 3. Winget: winget install ffmpeg
    echo.
    choice /c YN /m "¿Continuar sin FFmpeg? (Algunas funciones no estarán disponibles)"
    if !errorlevel! equ 2 (
        echo [INFO] Instalación cancelada. Instala FFmpeg y vuelve a ejecutar este script.
        pause
        exit /b 1
    )
    echo [WARNING] Continuando sin FFmpeg...
) else (
    for /f "tokens=3" %%a in ('ffmpeg -version 2^>^&1 ^| findstr "ffmpeg version"') do set FFMPEG_VERSION=%%a
    echo [SUCCESS] FFmpeg encontrado: !FFMPEG_VERSION!
)

:: Crear entorno virtual
echo [INFO] Configurando entorno virtual...
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [SUCCESS] Entorno virtual creado
) else (
    echo [SUCCESS] Entorno virtual ya existe
)

:: Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Actualizar pip en el entorno virtual
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo [WARNING] No se pudo actualizar pip, continuando...
)

:: Instalar dependencias
echo [INFO] Instalando dependencias de Python...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Error al instalar dependencias.
    echo [ERROR] Revisa tu conexión a internet y vuelve a intentar.
    pause
    exit /b 1
)
echo [SUCCESS] Dependencias instaladas correctamente

:: Crear directorios necesarios
echo [INFO] Creando directorios de la aplicación...
if not exist "uploads" mkdir uploads
if not exist "downloads" mkdir downloads
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "templates" mkdir templates
echo [SUCCESS] Directorios creados

:: Configurar archivo .env
echo [INFO] Configurando archivos de configuración...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [SUCCESS] Archivo .env creado desde .env.example
        echo [WARNING] ¡IMPORTANTE! Edita el archivo .env con tus credenciales antes de usar la aplicación.
    ) else (
        echo [WARNING] Archivo .env.example no encontrado.
        echo [INFO] Creando archivo .env básico...
        echo # TikTok to Shorts/Reels Uploader 2025 - Configuración > .env
        echo # Edita este archivo con tus credenciales reales >> .env
        echo. >> .env
        echo # YouTube API Configuration >> .env
        echo YOUTUBE_CLIENT_ID=your_youtube_client_id >> .env
        echo YOUTUBE_CLIENT_SECRET=your_youtube_client_secret >> .env
        echo YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token >> .env
        echo. >> .env
        echo # Instagram API Configuration >> .env
        echo INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token >> .env
        echo INSTAGRAM_USER_ID=your_instagram_user_id >> .env
        echo. >> .env
        echo # General Configuration >> .env
        echo DEBUG=True >> .env
        echo SECRET_KEY=change-this-secret-key >> .env
        echo [SUCCESS] Archivo .env básico creado
    )
) else (
    echo [SUCCESS] Archivo .env ya existe
)

:: Verificar instalación
echo [INFO] Verificando instalación...
python -c "import app; print('[SUCCESS] Aplicación importada correctamente')" 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Error al verificar la aplicación.
    echo [ERROR] Revisa los errores anteriores.
    pause
    exit /b 1
)

python -c "import yt_dlp, flask, requests, PIL; print('[SUCCESS] Dependencias verificadas')" 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Error al verificar dependencias críticas.
    pause
    exit /b 1
)

:: Mostrar instrucciones finales
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║                   ✅ INSTALACIÓN COMPLETA             ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo 1. Configura tus credenciales de API en el archivo .env:
echo    notepad .env
echo.
echo 2. Para usar la aplicación en el futuro:
echo    a. Activa el entorno virtual: venv\Scripts\activate.bat
echo    b. Ejecuta la aplicación: python run.py
echo    c. Abre tu navegador en: http://localhost:5000
echo.
echo 📖 DOCUMENTACIÓN:
echo    - README.md para guía completa
echo    - config.py para configuración avanzada
echo.
echo 🆘 SOPORTE:
echo    - GitHub Issues: https://github.com/tu-usuario/tiktok-uploader/issues
echo    - Email: soporte@tiktok-uploader.com
echo.
echo ¡Gracias por usar TikTok to Shorts/Reels Uploader 2025! 🚀
echo.

:: Preguntar si quiere ejecutar la aplicación ahora
choice /c YN /m "¿Deseas ejecutar la aplicación ahora?"
if !errorlevel! equ 1 (
    echo.
    echo [INFO] Iniciando aplicación...
    echo [INFO] Presiona Ctrl+C para detener el servidor
    echo.
    python run.py
)

echo.
echo [INFO] Instalación completada. ¡Disfruta usando la aplicación!
pause 