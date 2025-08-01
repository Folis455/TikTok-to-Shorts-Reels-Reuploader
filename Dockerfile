# TikTok to Shorts/Reels Uploader 2025 - Dockerfile
FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="TikTok Uploader Team <soporte@tiktok-uploader.com>"
LABEL description="TikTok to Shorts/Reels Uploader 2025"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV APP_HOME=/app

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la aplicación
WORKDIR $APP_HOME

# Copiar archivos de requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads downloads temp logs static/css static/js templates

# Establecer permisos
RUN chown -R appuser:appuser $APP_HOME
USER appuser

# Exponer puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Comando por defecto
CMD ["python", "run.py"] 