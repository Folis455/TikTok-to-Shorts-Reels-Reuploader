# services/instagram_uploader.py

import os
import requests
import json
from datetime import datetime
import logging

class InstagramUploader:
    def __init__(self):
        """
        Inicializa el servicio de Instagram API with Instagram Login (2025)
        """
        # Nueva Instagram API with Instagram Login
        self.client_id = os.getenv('INSTAGRAM_CLIENT_ID')
        self.client_secret = os.getenv('INSTAGRAM_CLIENT_SECRET')
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.user_id = os.getenv('INSTAGRAM_USER_ID')
        
        # URLs para Instagram API with Instagram Login
        self.base_url = 'https://graph.instagram.com'
        self.graph_url = 'https://graph.facebook.com'
        
        # Configuración específica para Reels
        self.reels_config = {
            'max_duration': 180,  # 3 minutos en 2025
            'supported_formats': ['mp4', 'mov'],
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'recommended_aspect_ratio': '9:16'
        }
        
        self.initialized = self._check_credentials()
        
    def _check_credentials(self):
        """Verifica si las credenciales están configuradas"""
        if not all([self.client_id, self.client_secret, self.access_token, self.user_id]):
            print("⚠️  Credenciales de Instagram no configuradas")
            return False
        return True
        
    def upload(self, video_path, description, thumbnail_path=None, custom_title=None):
        """
        Sube un video a Instagram como Reel usando Instagram API with Instagram Login
        
        Args:
            video_path (str): Ruta al archivo de video
            description (str): Descripción del video
            thumbnail_path (str): Ruta a la miniatura (opcional)
            custom_title (str): Título personalizado (opcional)
            
        Returns:
            dict: Información del video subido
        """
        if not self.initialized:
            raise Exception("Credenciales de Instagram no configuradas")
        
        try:
            print(f"[DEBUG] Iniciando subida a Instagram Reels...")
            print(f"[DEBUG] Video: {video_path}")
            print(f"[DEBUG] Description: {description[:100]}...")
            
            # Validar archivo
            if not os.path.exists(video_path):
                raise Exception(f"Archivo de video no encontrado: {video_path}")
            
            # Verificar tamaño del archivo
            file_size = os.path.getsize(video_path)
            if file_size > self.reels_config['max_file_size']:
                raise Exception(f"Archivo muy grande: {file_size} bytes. Máximo: {self.reels_config['max_file_size']} bytes")
            
            # Paso 1: Subir video y crear container
            container_result = self._create_media_container(video_path, description, custom_title)
            container_id = container_result['id']
            
            print(f"[DEBUG] Container creado: {container_id}")
            
            # Paso 2: Verificar estado del container
            status = self._check_container_status(container_id)
            print(f"[DEBUG] Estado del container: {status}")
            
            # Paso 3: Publicar el container
            if status == 'FINISHED':
                publish_result = self._publish_container(container_id)
                
                # Construir resultado
                result = {
                    'success': True,
                    'media_id': publish_result['id'],
                    'container_id': container_id,
                    'permalink': f"https://www.instagram.com/reel/{publish_result['id']}/",
                    'title': custom_title or self._generate_title(description),
                    'description': description,
                    'upload_date': datetime.now().isoformat(),
                    'platform': 'instagram_reels',
                    'api_version': 'Instagram API with Instagram Login'
                }
                
                print(f"[DEBUG] Instagram Reel subido exitosamente: {result}")
                return result
            else:
                raise Exception(f"Container no está listo para publicar. Estado: {status}")
                
        except Exception as e:
            print(f"[ERROR] Error en subida a Instagram: {str(e)}")
            raise e
    
    def _create_media_container(self, video_path, description, custom_title=None):
        """Crea un container de media para Instagram Reels"""
        
        # Para videos, necesitamos subir a un hosting temporal o usar URL pública
        # Por simplicidad, asumimos que el video ya está en una URL pública
        # En implementación real, subirías a S3, Cloudinary, etc.
        
        video_url = self._get_public_video_url(video_path)
        
        # Preparar título y descripción para Reels
        title = custom_title or self._generate_title(description)
        formatted_description = self._format_description_for_reels(description, title)
        
        url = f"{self.base_url}/{self.user_id}/media"
        
        params = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': formatted_description,
            'share_to_feed': 'true',  # Compartir también en el feed
            'access_token': self.access_token
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(f"Error creando container: {response.status_code} - {error_data}")
    
    def _check_container_status(self, container_id, max_retries=30, delay=2):
        """Verifica el estado del container hasta que esté listo"""
        import time
        
        for attempt in range(max_retries):
            url = f"{self.base_url}/{container_id}"
            params = {
                'fields': 'status_code',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status_code')
                
                if status == 'FINISHED':
                    return status
                elif status == 'ERROR':
                    raise Exception("Error procesando el video en Instagram")
                elif status in ['IN_PROGRESS', 'PUBLISHED']:
                    print(f"[DEBUG] Container en progreso... ({attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    time.sleep(delay)
            else:
                print(f"[DEBUG] Error verificando estado: {response.status_code}")
                time.sleep(delay)
        
        raise Exception("Timeout esperando que el container esté listo")
    
    def _publish_container(self, container_id):
        """Publica el container como Instagram Reel"""
        url = f"{self.base_url}/{self.user_id}/media_publish"
        
        params = {
            'creation_id': container_id,
            'access_token': self.access_token
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(f"Error publicando: {response.status_code} - {error_data}")
    
    def _get_public_video_url(self, video_path):
        """
        Convierte el video local a una URL pública
        En implementación real, subirías a S3, Cloudinary, etc.
        """
        # IMPLEMENTACIÓN TEMPORAL - En producción, subir a cloud storage
        # Por ahora, simulamos una URL pública
        filename = os.path.basename(video_path)
        
        # TODO: Implementar subida real a cloud storage
        # Opciones: AWS S3, Cloudinary, Azure Blob, etc.
        
        # Temporal: usar servidor local (solo para desarrollo)
        return f"http://your-domain.com/temp-videos/{filename}"
    
    def _generate_title(self, description):
        """Genera un título atractivo basado en la descripción"""
        # Tomar las primeras palabras de la descripción
        words = description.split()[:8]
        title = ' '.join(words)
        
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def _format_description_for_reels(self, original_description, title):
        """Retorna la descripción original sin hashtags automáticos"""
        return self._clean_description(original_description)
    
    def _clean_description(self, description):
        """Limpia y optimiza la descripción"""
        import re
        
        # Eliminar hashtags duplicados
        hashtags = re.findall(r'#\w+', description)
        text_without_hashtags = re.sub(r'#\w+', '', description).strip()
        
        # Mantener solo hashtags únicos y relevantes
        unique_hashtags = list(dict.fromkeys(hashtags))[:10]  # Máximo 10 hashtags originales
        
        # Reconstruir
        cleaned = text_without_hashtags
        if unique_hashtags:
            cleaned += f"\n\n{' '.join(unique_hashtags)}"
        
        return cleaned.strip()
    
    def upload_with_manual_mode(self, video_path, description, custom_title=None):
        """
        Modo manual: optimiza el video y proporciona instrucciones para subida manual
        Útil como respaldo cuando la API no está disponible
        """
        try:
            # Generar descripción optimizada
            title = custom_title or self._generate_title(description)
            formatted_description = self._format_description_for_reels(description, title)
            
            # Información del video
            video_info = {
                'original_path': video_path,
                'optimized_title': title,
                'optimized_description': formatted_description,
                'recommended_hashtags': ["#Reels", "#InstagramReels", "#Viral", "#Content"],
                'manual_instructions': [
                    "1. Abre Instagram en tu móvil",
                    "2. Toca el botón + para crear contenido",
                    "3. Selecciona 'Reel'",
                    "4. Sube el video optimizado",
                    "5. Copia y pega la descripción optimizada",
                    "6. Publica el Reel"
                ]
            }
            
            return {
                'success': True,
                'mode': 'manual',
                'video_info': video_info,
                'message': 'Video optimizado para subida manual a Instagram Reels'
            }
            
        except Exception as e:
            raise Exception(f"Error en modo manual: {str(e)}") 