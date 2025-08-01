# 📱 Instagram API 2025 - Guía de Configuración

## 🚀 Instagram API with Instagram Login (Nueva API 2025)

**⚠️ IMPORTANTE:** Instagram Basic Display API fue **deprecada en diciembre 2024**. Esta guía usa la **nueva Instagram API with Instagram Login** (2025).

---

## 📋 **Paso 1: Crear App en Meta for Developers**

### 1.1 Acceso a Meta Developers
1. Ve a [https://developers.facebook.com](https://developers.facebook.com)
2. Inicia sesión con tu cuenta de Facebook/Meta
3. Click **"My Apps"** → **"Create App"**

### 1.2 Configurar la Aplicación
1. **Usecase**: Selecciona **"Other"**
2. **App Type**: Selecciona **"Business"** 
3. **App Name**: `TikTok to Instagram Reels Uploader`
4. **Contact Email**: Tu email
5. **Business Manager Account**: Crear o seleccionar uno
6. Click **"Create App"**

---

## 📋 **Paso 2: Agregar Productos a la App**

### 2.1 Productos Necesarios (Apps Nuevas 2025)
Agrega estos 2 productos:
- ✅ **Instagram** 
- ✅ **Facebook Login for Business**

### 2.2 Si ves Apps Antiguas (3 productos)
Si tu developer account es anterior:
- ✅ **Facebook Login**
- ✅ **Instagram Basic Display** (para transición)
- ✅ **Instagram Graph API**

---

## 📋 **Paso 3: Configurar Instagram API**

### 3.1 Setup Instagram Product
1. En el dashboard, click **"Instagram"** → **"Setup"**
2. **Instagram App Type**: Selecciona **"Business"**
3. Completa la configuración básica

### 3.2 Configurar OAuth Redirect URIs
Agrega estas URLs en **Valid OAuth Redirect URIs**:
```
http://localhost:5000/auth/instagram/callback
http://localhost:8080/
https://tu-dominio.com/auth/instagram/callback
```

---

## 📋 **Paso 4: Configurar App Settings**

### 4.1 Settings → Basic
1. **App Domain**: Agrega `localhost` y tu dominio
2. **Privacy Policy URL**: Requerido para revisión
3. **Terms of Service URL**: Recomendado
4. **App Icon**: Subir logo de la app

### 4.2 Copiar Credenciales
En **Settings → Basic**, copia:
- ✅ **App ID** 
- ✅ **App Secret** (click "Show")

---

## 📋 **Paso 5: Crear Instagram Test User**

### 5.1 Agregar Instagram Tester
1. Ve a **Roles** → **Instagram Testers**
2. Click **"Add Instagram Testers"**
3. Ingresa tu **username de Instagram**
4. Send invitation

### 5.2 Aceptar Invitación
1. Ve a [instagram.com](https://instagram.com)
2. **Profile** → **Edit Profile** → **Apps and Websites**
3. **Tester Invites** → Acepta la invitación de tu app

---

## 📋 **Paso 6: Obtener Access Token**

### 6.1 Generar User Token
1. En tu app dashboard → **Instagram** → **Basic Display**
2. Scroll hasta **User Token Generator**
3. Click **"Generate Token"**
4. Autoriza con tu Instagram account
5. **Copia el Access Token generado**

### 6.2 Obtener User ID
```bash
curl -X GET \
"https://graph.instagram.com/me?fields=id,username&access_token=TU_ACCESS_TOKEN"
```

---

## 📋 **Paso 7: Configurar en la Aplicación**

### 7.1 Variables de Entorno (.env)
```env
# Instagram API with Instagram Login (2025)
INSTAGRAM_CLIENT_ID=tu_app_id
INSTAGRAM_CLIENT_SECRET=tu_app_secret  
INSTAGRAM_ACCESS_TOKEN=tu_access_token
INSTAGRAM_USER_ID=tu_user_id

# Configuración opcional
INSTAGRAM_REDIRECT_URI=http://localhost:5000/auth/instagram/callback
```

### 7.2 Verificar Configuración
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('✅ Client ID:', os.getenv('INSTAGRAM_CLIENT_ID')[:10] + '...' if os.getenv('INSTAGRAM_CLIENT_ID') else '❌ No configurado')
print('✅ Access Token:', os.getenv('INSTAGRAM_ACCESS_TOKEN')[:20] + '...' if os.getenv('INSTAGRAM_ACCESS_TOKEN') else '❌ No configurado')
print('✅ User ID:', os.getenv('INSTAGRAM_USER_ID') if os.getenv('INSTAGRAM_USER_ID') else '❌ No configurado')
"
```

---

## 🔧 **Paso 8: Testing**

### 8.1 Test API Connection
```bash
curl -X GET \
"https://graph.instagram.com/me?fields=id,username,account_type&access_token=TU_ACCESS_TOKEN"
```

**Respuesta esperada:**
```json
{
  "id": "17841405793187218",
  "username": "tu_username", 
  "account_type": "BUSINESS"
}
```

### 8.2 Test Reels Upload (Simulation)
```bash
curl -X POST \
"https://graph.instagram.com/TU_USER_ID/media" \
-F "media_type=REELS" \
-F "video_url=https://ejemplo.com/video.mp4" \
-F "caption=Test Reel from API" \
-F "access_token=TU_ACCESS_TOKEN"
```

---

## ⚠️ **Limitaciones Actuales**

### 8.1 Cuentas Soportadas
- ✅ **Business Accounts** (Recomendado)
- ✅ **Creator Accounts** 
- ❌ **Personal Accounts** (Limitado)

### 8.2 Tipos de Media
- ✅ **Reels** (hasta 3 minutos en 2025)
- ✅ **Posts** (fotos y videos)
- ❌ **Stories** (no soportado en API)

### 8.3 Requisitos de Video
- **Formato**: MP4, MOV
- **Duración**: Máximo 180 segundos (3 min)
- **Tamaño**: Máximo 100MB
- **Resolución**: Mínimo 540x960, Máximo 1080x1920
- **Aspect Ratio**: 9:16 (recomendado para Reels)

---

## 🔍 **Troubleshooting**

### Error: "Invalid Access Token"
```bash
# Verificar token
curl -X GET "https://graph.instagram.com/me?access_token=TU_TOKEN"

# Si falla, regenerar token en Meta Developers
```

### Error: "Insufficient Permissions"
- ✅ Verificar que la app tiene permisos de **instagram_content_publish**
- ✅ Verificar que tu cuenta es **Business/Creator**
- ✅ Verificar que aceptaste la invitación de tester

### Error: "Media Upload Failed"
- ✅ Video debe estar en URL pública (no localhost)
- ✅ Verificar formato y tamaño del video
- ✅ Verificar que la URL es accesible

---

## 🌐 **Hosting de Videos (Requerido)**

Para que Instagram pueda acceder al video, necesitas hosting público:

### Opciones Recomendadas:
1. **AWS S3** + CloudFront
2. **Cloudinary** (especializado en medios)
3. **Azure Blob Storage**
4. **Google Cloud Storage**

### Ejemplo con Cloudinary:
```python
import cloudinary
import cloudinary.uploader

# Subir video a Cloudinary
result = cloudinary.uploader.upload(
    video_path,
    resource_type="video",
    folder="instagram-reels"
)

video_url = result['secure_url']  # URL pública para Instagram
```

---

## 📚 **Recursos Adicionales**

- 📖 [Instagram API Documentation](https://developers.facebook.com/docs/instagram-api)
- 🔧 [Graph API Explorer](https://developers.facebook.com/tools/explorer)
- 💬 [Meta Developer Community](https://developers.facebook.com/community)
- 📊 [Instagram API Changelog](https://developers.facebook.com/docs/instagram-api/changelog)

---

## ✅ **Verificación Final**

Antes de usar en producción, verifica:
- [ ] App ID y App Secret configurados
- [ ] Access Token válido y no expirado
- [ ] Instagram account es Business/Creator
- [ ] Video hosting público configurado
- [ ] Permisos correctos otorgados
- [ ] Test de subida exitoso

---

**🎉 ¡Configuración completada!** Tu aplicación ya puede subir Reels automáticamente a Instagram usando la nueva API 2025. 