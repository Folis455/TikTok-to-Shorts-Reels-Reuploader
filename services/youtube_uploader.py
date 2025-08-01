import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import pickle
from datetime import datetime

class YouTubeUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.credentials = None
        self.service = None
        
        # Configuración para YouTube Shorts (2025)
        self.shorts_config = {
            'max_duration': 180,  # 3 minutos para Shorts en 2025
            'vertical_ratio': True,  # Videos verticales preferidos
            'tags': ['#Shorts', '#YouTubeShorts', '#TikTok'],
            'category_id': '22',  # People & Blogs
            'privacy_status': 'public'
        }
        
        self.initialize_service()
    
    def initialize_service(self):
        """Inicializa el servicio de YouTube API"""
        try:
            # Buscar credenciales guardadas
            creds_file = 'youtube_credentials.json'
            token_file = 'youtube_token.pickle'
            
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Si no hay credenciales válidas, obtenerlas
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if os.path.exists(creds_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            creds_file, self.SCOPES)
                        self.credentials = flow.run_local_server(port=8080)
                    else:
                        # Usar variables de entorno si están disponibles
                        client_id = os.getenv('YOUTUBE_CLIENT_ID')
                        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
                        refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
                        
                        if all([client_id, client_secret, refresh_token]):
                            self.credentials = Credentials(
                                token=None,
                                refresh_token=refresh_token,
                                client_id=client_id,
                                client_secret=client_secret,
                                token_uri='https://oauth2.googleapis.com/token'
                            )
                            self.credentials.refresh(Request())
                        else:
                            raise Exception("No se encontraron credenciales de YouTube. Configure las variables de entorno o el archivo credentials.json")
                
                # Guardar credenciales para uso futuro
                with open(token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Construir el servicio
            self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self.credentials)
            
        except Exception as e:
            print(f"Error inicializando YouTube API: {str(e)}")
            self.service = None
    
    def upload(self, video_path, description, thumbnail_path=None, custom_title=None):
        """
        Sube un video a YouTube como Short
        
        Args:
            video_path (str): Ruta al archivo de video
            description (str): Descripción del video
            thumbnail_path (str): Ruta a la miniatura (opcional)
            custom_title (str): Título personalizado (opcional)
            
        Returns:
            dict: Información del video subido
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado")
        
        try:
            # Validar archivo
            if not os.path.exists(video_path):
                raise Exception(f"Archivo de video no encontrado: {video_path}")
            
            # Preparar título
            if custom_title:
                title = custom_title
            else:
                # Generar título basado en descripción
                title = self.generate_title_from_description(description)
            
            # Asegurar que es un Short
            title = f"#Shorts {title}" if not title.startswith('#Shorts') else title
            
            # Usar descripción tal como está (sin hashtags automáticos)
            formatted_description = description
            
            # Configurar metadatos del video
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube tiene límite de 100 caracteres
                    'description': formatted_description,
                    'tags': self.generate_tags(description),
                    'categoryId': self.shorts_config['category_id'],
                    'defaultLanguage': 'es',
                    'defaultAudioLanguage': 'es'
                },
                'status': {
                    'privacyStatus': self.shorts_config['privacy_status'],
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Configurar upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # Iniciar upload
            insert_request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Ejecutar upload con reintentos
            response = self.resumable_upload(insert_request)
            
            if response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                shorts_url = f"https://www.youtube.com/shorts/{video_id}"
                
                # Subir miniatura si se proporciona
                thumbnail_uploaded = False
                if thumbnail_path and os.path.exists(thumbnail_path):
                    thumbnail_uploaded = self.upload_thumbnail(video_id, thumbnail_path)
                
                return {
                    'success': True,
                    'video_id': video_id,
                    'video_url': video_url,
                    'shorts_url': shorts_url,
                    'title': title,
                    'description': formatted_description,
                    'thumbnail_uploaded': thumbnail_uploaded,
                    'upload_date': datetime.now().isoformat(),
                    'platform': 'youtube_shorts'
                }
            else:
                raise Exception("No se recibió respuesta del servidor de YouTube")
                
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            raise Exception(f"Error de YouTube API: {error_details}")
        except Exception as e:
            raise Exception(f"Error subiendo a YouTube: {str(e)}")
    
    def resumable_upload(self, insert_request):
        """Maneja la subida resumible con reintentos"""
        response = None
        error = None
        retry = 0
        max_retries = 3
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        return response
                    else:
                        raise Exception(f"Error inesperado: {response}")
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Errores del servidor, reintentar
                    retry += 1
                    if retry > max_retries:
                        raise Exception(f"Error después de {max_retries} intentos: {e}")
                    
                    import time
                    time.sleep(2 ** retry)  # Backoff exponencial
                else:
                    raise e
        
        return response
    
    def upload_thumbnail(self, video_id, thumbnail_path):
        """Sube una miniatura personalizada"""
        try:
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            return True
        except Exception as e:
            print(f"Error subiendo miniatura: {str(e)}")
            return False
    
    def generate_title_from_description(self, description):
        """Genera un título basado en la descripción"""
        if not description:
            return "Mi Video Short"
        
        # Tomar las primeras palabras de la descripción
        words = description.split()[:8]
        title = " ".join(words)
        
        # Limpiar caracteres especiales
        import re
        title = re.sub(r'[^\w\s\-áéíóúñ]', '', title)
        
        return title[:80]  # Limitar longitud
    
    def format_description_for_shorts(self, original_description):
        """Retorna la descripción original sin modificaciones"""
        return original_description if original_description else ""
    
    def generate_tags(self, description):
        """Genera tags relevantes basados en la descripción"""
        base_tags = [
            'shorts', 'youtube shorts', 'viral', 'trending',
            'tiktok', 'reels', 'entertainment', 'fun'
        ]
        
        # Extraer palabras clave de la descripción
        if description:
            import re
            words = re.findall(r'\b\w+\b', description.lower())
            # Filtrar palabras comunes
            common_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los', 'una', 'al', 'todo', 'esta', 'sus', 'mi', 'me', 'si', 'ya', 'o', 'pero', 'más', 'tiene', 'muy', 'todo', 'hasta', 'cuando', 'donde', 'hace', 'puede', 'entre', 'sin', 'sobre', 'ser', 'está', 'tan', 'solo', 'ese', 'ese', 'cada', 'algo', 'ese', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            relevant_words = [word for word in words if len(word) > 3 and word not in common_words]
            base_tags.extend(relevant_words[:10])
        
        return base_tags[:30]  # YouTube permite máximo 30 tags
    
    def check_video_status(self, video_id):
        """Verifica el estado de procesamiento del video"""
        try:
            response = self.service.videos().list(
                part="status,processingDetails",
                id=video_id
            ).execute()
            
            if response['items']:
                return response['items'][0]
            return None
            
        except Exception as e:
            print(f"Error verificando estado del video: {str(e)}")
            return None 