# 🚀 TikTok to Shorts/Reels Uploader 2025

Una herramienta completa para resubir automáticamente tus TikToks a YouTube Shorts e Instagram Reels, manteniendo la calidad original, sin marca de agua y con soporte para las nuevas duraciones extendidas de 2025.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Características principales

- 🎥 **Descarga sin marca de agua**: Videos limpios usando yt-dlp optimizado
- 📱 **Soporte multiplataforma**: YouTube Shorts e Instagram Reels
- 🎬 **Calidad preservada**: Sin pérdida de calidad, formato MP4 optimizado
- ⏰ **Duraciones extendidas 2025**: Hasta 3 minutos en ambas plataformas
- 🏷️ **Hashtags optimizados**: Descripción automática adaptada por plataforma
- 🖼️ **Miniatura conservada**: Mantiene la miniatura original del video
- 🔄 **Procesamiento automático**: Subida a múltiples plataformas simultáneamente
- 💻 **Interfaz moderna**: Web UI responsive y fácil de usar
- 📊 **Seguimiento en tiempo real**: Progreso detallado del procesamiento

## 🎯 Casos de uso

- **Creadores de contenido** que quieren maximizar su alcance
- **Marcas** que necesitan distribuir contenido en múltiples plataformas
- **Agencias de marketing** que gestionan múltiples cuentas
- **Influencers** que quieren automatizar su workflow de contenido

## 📋 Prerrequisitos

### Software necesario:
- Python 3.8 o superior
- FFmpeg (para procesamiento de video)
- Redis (para colas de tareas, opcional)

### APIs y credenciales:
- **YouTube Data API v3**: Para subir a YouTube Shorts
- **Facebook Graph API**: Para subir a Instagram Reels

## 🚀 Instalación rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/tiktok-uploader.git
cd tiktok-uploader
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar FFmpeg

#### Windows:
```bash
# Con chocolatey
choco install ffmpeg

# O descargar desde https://ffmpeg.org/download.html
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
# Con Homebrew
brew install ffmpeg
```

### 5. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

### 6. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## ⚙️ Configuración

### Configuración de YouTube API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la YouTube Data API v3
4. Crea credenciales (OAuth 2.0)
5. Descarga el archivo `credentials.json`
6. Agrega las credenciales a tu archivo `.env`:

```env
YOUTUBE_CLIENT_ID=tu_client_id_aqui
YOUTUBE_CLIENT_SECRET=tu_client_secret_aqui
YOUTUBE_REFRESH_TOKEN=tu_refresh_token_aqui
```

### Configuración de Instagram API

1. Ve a [Facebook for Developers](https://developers.facebook.com/)
2. Crea una aplicación
3. Configura Instagram Basic Display
4. Obtén el Access Token y User ID
5. Agrega las credenciales a tu archivo `.env`:

```env
INSTAGRAM_ACCESS_TOKEN=tu_access_token_aqui
INSTAGRAM_USER_ID=tu_user_id_aqui
```

### Variables de entorno completas

```env
# YouTube API Configuration
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token

# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_USER_ID=your_instagram_user_id

# General Configuration
DEBUG=True
SECRET_KEY=your_secret_key_here
MAX_VIDEO_SIZE_MB=500
MAX_VIDEO_DURATION_SECONDS=600

# Proxy Configuration (opcional)
HTTP_PROXY=
HTTPS_PROXY=

# Redis Configuration (para colas)
REDIS_URL=redis://localhost:6379/0

# Telegram Bot (opcional, para notificaciones)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## 📖 Uso

### Interfaz Web

1. Abre `http://localhost:5000` en tu navegador
2. Pega la URL de tu TikTok
3. Selecciona las plataformas destino (YouTube Shorts, Instagram Reels)
4. Opcionalmente, personaliza la descripción
5. Haz clic en "Procesar y Subir"
6. Observa el progreso en tiempo real
7. ¡Recibe los enlaces de tus videos subidos!

### API REST

La aplicación también proporciona una API REST para integración:

#### Procesar video completo
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@usuario/video/1234567890",
    "platforms": ["youtube", "instagram"],
    "description": "Mi descripción personalizada"
  }'
```

#### Solo descargar
```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@usuario/video/1234567890"
  }'
```

#### Verificar estado de tarea
```bash
curl http://localhost:5000/api/task/{task_id}
```

### Respuestas de la API

#### Respuesta exitosa:
```json
{
  "task_id": "uuid-de-la-tarea",
  "status": "started",
  "message": "Procesamiento iniciado"
}
```

#### Estado de tarea:
```json
{
  "status": "completed",
  "progress": 100,
  "message": "Procesamiento completado exitosamente",
  "video_info": {
    "title": "Título del video",
    "creator": "@usuario",
    "duration": 45.2,
    "width": 1080,
    "height": 1920
  },
  "uploads": {
    "youtube": {
      "success": true,
      "video_id": "abc123",
      "video_url": "https://www.youtube.com/watch?v=abc123",
      "shorts_url": "https://www.youtube.com/shorts/abc123"
    },
    "instagram": {
      "success": true,
      "reel_id": "def456",
      "reel_url": "https://www.instagram.com/reel/def456/"
    }
  }
}
```

## 🔧 Configuración avanzada

### Configuración de calidad de video

La aplicación utiliza configuraciones optimizadas para cada plataforma:

```python
platform_configs = {
    'youtube_shorts': {
        'max_duration': 180,  # 3 minutos en 2025
        'resolution': {'width': 1080, 'height': 1920},  # 9:16
        'bitrate': '8000k',  # Alta calidad
        'fps': 30,
        'audio_bitrate': '128k'
    },
    'instagram_reels': {
        'max_duration': 180,  # 3 minutos en 2025
        'resolution': {'width': 1080, 'height': 1920},  # 9:16
        'bitrate': '6000k',
        'fps': 30,
        'audio_bitrate': '128k'
    }
}
```

### Personalización de hashtags

Puedes personalizar los hashtags por defecto editando `services/metadata_processor.py`:

```python
self.default_hashtags = {
    'youtube': ['#Shorts', '#YouTubeShorts', '#Viral', '#Trending'],
    'instagram': ['#reels', '#instagram', '#viral', '#fyp', '#parati']
}
```

### Uso con Docker

```dockerfile
# Dockerfile incluido
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

```bash
# Construir imagen
docker build -t tiktok-uploader .

# Ejecutar contenedor
docker run -p 5000:5000 -v $(pwd)/.env:/app/.env tiktok-uploader
```

## 🛡️ Consideraciones de seguridad

- **Nunca commits credenciales**: Usa variables de entorno
- **Limita el acceso**: Considera autenticación para uso en producción
- **Monitorea el uso**: Las APIs tienen límites de rate
- **Mantén actualizado**: Actualiza dependencias regularmente

## 📊 Monitoreo y logs

La aplicación incluye logging detallado:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('uploader.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Actualizaciones y migraciones

### Actualizar dependencias:
```bash
pip install -r requirements.txt --upgrade
```

### Migración desde versiones anteriores:
- Revisa el `CHANGELOG.md` para cambios importantes
- Actualiza las configuraciones de API si es necesario
- Prueba en entorno de desarrollo antes de producción

## 🐛 Solución de problemas

### Problemas comunes:

#### Error de FFmpeg no encontrado
```bash
# Instalar FFmpeg
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS
```

#### Error de credenciales de YouTube
- Verifica que las credenciales OAuth estén correctas
- Asegúrate de que el refresh token sea válido
- Revisa que la YouTube Data API esté habilitada

#### Error de subida a Instagram
- Confirma que el access token sea válido
- Verifica que la aplicación tenga permisos de Instagram
- Revisa el tamaño y formato del video

#### Video demasiado largo
- Los videos se recortan automáticamente a 3 minutos
- Verifica la configuración de duración máxima

### Logs de debug

Para habilitar logs detallados:

```bash
export DEBUG=True
python app.py
```

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de contribución:

- Sigue PEP 8 para el código Python
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación
- Prueba en múltiples plataformas

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Reconocimientos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Para descarga de videos
- [FFmpeg](https://ffmpeg.org/) - Para procesamiento de video
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Google APIs](https://developers.google.com/) - YouTube integration
- [Facebook for Developers](https://developers.facebook.com/) - Instagram integration

## 📞 Soporte

- 📧 Email: soporte@tiktok-uploader.com
- 💬 Discord: [Únete a nuestro servidor](https://discord.gg/tiktok-uploader)
- 📖 Wiki: [Documentación completa](https://github.com/tu-usuario/tiktok-uploader/wiki)
- 🐛 Reportar bugs: [Issues](https://github.com/tu-usuario/tiktok-uploader/issues)

## 🚀 Roadmap

### Próximas versiones:

- [ ] Soporte para TikTok Stories
- [ ] Integración con Twitter/X
- [ ] Programación de subidas
- [ ] Dashboard de analytics
- [ ] API webhooks
- [ ] Procesamiento por lotes
- [ ] Integración con Zapier
- [ ] App móvil

---

**¿Te gusta el proyecto?** ⭐ ¡Danos una estrella en GitHub y compártelo con otros creadores!

**Creado con ❤️ para la comunidad de creadores de contenido en 2025** 