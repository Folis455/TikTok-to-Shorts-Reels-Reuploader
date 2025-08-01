import yt_dlp
import os
import json
import requests
from urllib.parse import urlparse
import re
from datetime import datetime
import tempfile
import shutil

class TikTokDownloader:
    def __init__(self):
        self.download_folder = 'downloads'
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Configuración optimizada para TikTok sin marca de agua
        self.ydl_opts = {
            'format': 'best[ext=mp4]',  # Mejor calidad en MP4
            'outtmpl': os.path.join(self.download_folder, '%(id)s_%(title)s.%(ext)s'),
            'writeinfojson': True,  # Guardar metadatos
            'writethumbnail': True,  # Descargar miniatura
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'extractflat': False,
            'writethumbnail': True,
            'writeinfojson': True,
            # Headers para evitar detección
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
    
    def extract_video_id(self, url):
        """Extrae el ID del video de la URL de TikTok"""
        patterns = [
            r'tiktok\.com/@[^/]+/video/(\d+)',
            r'tiktok\.com/t/([A-Za-z0-9]+)',
            r'vm\.tiktok\.com/([A-Za-z0-9]+)',
            r'tiktok\.com/@[^/]+/video/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download(self, url, task_id=None):
        """
        Descarga un video de TikTok sin marca de agua
        
        Args:
            url (str): URL del video de TikTok
            task_id (str): ID de la tarea para seguimiento
            
        Returns:
            dict: Información del video descargado
        """
        try:
            # Validar URL
            if not self.is_valid_tiktok_url(url):
                raise ValueError("URL de TikTok no válida")
            
            # Crear directorio temporal para esta descarga
            temp_dir = tempfile.mkdtemp(prefix=f'tiktok_{task_id}_')
            
            # Configurar ruta de salida temporal
            temp_opts = self.ydl_opts.copy()
            temp_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
            
            # Ejecutar descarga
            with yt_dlp.YoutubeDL(temp_opts) as ydl:
                # Extraer información primero
                info_dict = ydl.extract_info(url, download=False)
                
                # Descargar video
                ydl.download([url])
                
                # Procesar archivos descargados
                video_id = info_dict.get('id', 'unknown')
                title = info_dict.get('title', 'TikTok Video')
                description = info_dict.get('description', '')
                creator = info_dict.get('uploader', '')
                
                # Buscar archivos descargados
                video_file = None
                thumbnail_file = None
                info_file = None
                
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp4'):
                        video_file = os.path.join(temp_dir, file)
                    elif file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                        thumbnail_file = os.path.join(temp_dir, file)
                    elif file.endswith('.info.json'):
                        info_file = os.path.join(temp_dir, file)
                
                if not video_file:
                    raise Exception("No se pudo descargar el video")
                
                # Mover archivos a directorio permanente
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_video_path = os.path.join(
                    self.download_folder, 
                    f"{video_id}_{timestamp}.mp4"
                )
                final_thumbnail_path = None
                final_info_path = None
                
                shutil.move(video_file, final_video_path)
                
                if thumbnail_file:
                    final_thumbnail_path = os.path.join(
                        self.download_folder, 
                        f"{video_id}_{timestamp}_thumb.jpg"
                    )
                    shutil.move(thumbnail_file, final_thumbnail_path)
                
                if info_file:
                    final_info_path = os.path.join(
                        self.download_folder, 
                        f"{video_id}_{timestamp}_info.json"
                    )
                    shutil.move(info_file, final_info_path)
                
                # Limpiar directorio temporal
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                # Obtener información adicional del video
                video_info = self.get_video_info(final_video_path)
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'creator': creator,
                    'video_path': final_video_path,
                    'thumbnail_path': final_thumbnail_path,
                    'info_path': final_info_path,
                    'metadata': {
                        'title': title,
                        'description': description,
                        'creator': creator,
                        'duration': video_info.get('duration', 0),
                        'width': video_info.get('width', 0),
                        'height': video_info.get('height', 0),
                        'fps': video_info.get('fps', 30),
                        'file_size': video_info.get('file_size', 0),
                        'download_date': datetime.now().isoformat()
                    },
                    'success': True
                }
                
        except Exception as e:
            # Limpiar directorio temporal en caso de error
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            raise Exception(f"Error descargando video: {str(e)}")
    
    def is_valid_tiktok_url(self, url):
        """Valida si la URL es de TikTok"""
        tiktok_domains = ['tiktok.com', 'vm.tiktok.com', 'www.tiktok.com']
        try:
            parsed = urlparse(url)
            return any(domain in parsed.netloc for domain in tiktok_domains)
        except:
            return False
    
    def get_video_info(self, video_path):
        """Obtiene información técnica del video usando ffprobe"""
        try:
            import subprocess
            
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                video_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                
                if video_stream:
                    return {
                        'duration': float(data.get('format', {}).get('duration', 0)),
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'fps': eval(video_stream.get('r_frame_rate', '30/1')),
                        'file_size': int(data.get('format', {}).get('size', 0)),
                        'codec': video_stream.get('codec_name', 'unknown')
                    }
            
            return {}
            
        except Exception:
            # Si ffprobe no está disponible, obtener info básica
            try:
                stat = os.stat(video_path)
                return {
                    'file_size': stat.st_size,
                    'duration': 0,
                    'width': 0,
                    'height': 0,
                    'fps': 30
                }
            except:
                return {}
    
    def get_alternative_download_methods(self, url):
        """Métodos alternativos si yt-dlp falla"""
        try:
            # Método 1: Usar API no oficial de TikTok
            api_url = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/"
            
            # Extraer video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                return None
            
            # Hacer petición a la API
            response = requests.get(
                f"https://www.tiktok.com/oembed?url={url}",
                headers=self.ydl_opts['http_headers']
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'author_name': data.get('author_name', '')
                }
            
            return None
            
        except Exception:
            return None 