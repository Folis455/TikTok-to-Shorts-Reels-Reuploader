import os
import subprocess
import json
import shutil
from datetime import datetime
import tempfile
from PIL import Image

# Importaciones opcionales para manejo de errores en producción
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV (cv2) not available. Some video processing features will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Some video processing features will be limited.")

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='video_processor_')
        
        # Configuraciones de calidad para cada plataforma (2025)
        self.platform_configs = {
            'youtube_shorts': {
                'max_duration': 180,  # 3 minutos en 2025
                'resolution': {'width': 1080, 'height': 1920},  # 9:16
                'bitrate': '8000k',  # Alta calidad
                'fps': 30,
                'audio_bitrate': '128k',
                'format': 'mp4',
                'codec': 'h264'
            },
            'instagram_reels': {
                'max_duration': 180,  # 3 minutos en 2025
                'resolution': {'width': 1080, 'height': 1920},  # 9:16
                'bitrate': '6000k',
                'fps': 30,
                'audio_bitrate': '128k',
                'format': 'mp4',
                'codec': 'h264'
            }
        }
    
    def process(self, video_path, metadata, target_platforms=['youtube_shorts', 'instagram_reels']):
        """
        Procesa el video manteniendo la máxima calidad para las plataformas objetivo
        
        Args:
            video_path (str): Ruta al video original
            metadata (dict): Metadatos del video
            target_platforms (list): Plataformas objetivo
            
        Returns:
            dict: Información del video procesado
        """
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video no encontrado: {video_path}")
            
            # Analizar video original
            video_info = self.analyze_video(video_path)
            
            # Determinar si necesita procesamiento
            needs_processing = self.needs_processing(video_info, target_platforms)
            
            if not needs_processing:
                # El video ya está optimizado
                return {
                    'path': video_path,
                    'processed': False,
                    'original_info': video_info,
                    'thumbnail': self.extract_thumbnail(video_path),
                    'platforms_ready': target_platforms
                }
            
            # Procesar video para cada plataforma
            processed_videos = {}
            
            for platform in target_platforms:
                processed_path = self.process_for_platform(video_path, platform, video_info)
                processed_videos[platform] = processed_path
            
            # Usar la versión de mejor calidad como principal
            main_video = processed_videos.get('youtube_shorts', processed_videos[list(processed_videos.keys())[0]])
            
            # Extraer miniatura de alta calidad
            thumbnail_path = self.extract_high_quality_thumbnail(main_video)
            
            return {
                'path': main_video,
                'processed': True,
                'original_info': video_info,
                'processed_videos': processed_videos,
                'thumbnail': thumbnail_path,
                'platforms_ready': target_platforms,
                'processing_report': self.create_processing_report(video_path, main_video, video_info)
            }
            
        except Exception as e:
            raise Exception(f"Error procesando video: {str(e)}")
    
    def analyze_video(self, video_path):
        """Analiza las propiedades técnicas del video"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Usar OpenCV como fallback
                return self.analyze_with_opencv(video_path)
            
            data = json.loads(result.stdout)
            
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            format_info = data.get('format', {})
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'width': int(video_stream.get('width', 0)) if video_stream else 0,
                'height': int(video_stream.get('height', 0)) if video_stream else 0,
                'fps': self.parse_fps(video_stream.get('r_frame_rate', '30/1')) if video_stream else 30,
                'bitrate': int(format_info.get('bit_rate', 0)),
                'codec': video_stream.get('codec_name', 'unknown') if video_stream else 'unknown',
                'has_audio': audio_stream is not None,
                'audio_codec': audio_stream.get('codec_name', 'none') if audio_stream else 'none',
                'file_size': int(format_info.get('size', 0)),
                'aspect_ratio': self.calculate_aspect_ratio(
                    video_stream.get('width', 0) if video_stream else 0,
                    video_stream.get('height', 0) if video_stream else 0
                )
            }
            
        except Exception as e:
            print(f"Error analizando video con ffprobe: {str(e)}")
            return self.analyze_with_opencv(video_path)
    
    def analyze_with_opencv(self, video_path):
        """Analizar video usando OpenCV como fallback"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception("No se pudo abrir el video con OpenCV")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            file_size = os.path.getsize(video_path)
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'bitrate': 0,  # No disponible con OpenCV
                'codec': 'unknown',
                'has_audio': True,  # Asumimos que tiene audio
                'audio_codec': 'unknown',
                'file_size': file_size,
                'aspect_ratio': self.calculate_aspect_ratio(width, height)
            }
            
        except Exception as e:
            print(f"Error analizando video con OpenCV: {str(e)}")
            return self.get_default_video_info()
    
    def needs_processing(self, video_info, target_platforms):
        """Determina si el video necesita ser procesado"""
        # Verificar duración máxima
        max_duration = max(self.platform_configs[platform]['max_duration'] for platform in target_platforms)
        if video_info['duration'] > max_duration:
            return True
        
        # Verificar resolución (preferimos 1080x1920 para vertical)
        ideal_width = 1080
        ideal_height = 1920
        
        if video_info['width'] != ideal_width or video_info['height'] != ideal_height:
            # Verificar si al menos tiene proporción 9:16
            aspect_ratio = video_info['width'] / video_info['height'] if video_info['height'] > 0 else 0
            if abs(aspect_ratio - (9/16)) > 0.1:  # Tolerancia del 10%
                return True
        
        # Verificar si el archivo es demasiado grande
        max_file_size = 100 * 1024 * 1024  # 100MB
        if video_info['file_size'] > max_file_size:
            return True
        
        return False
    
    def process_for_platform(self, video_path, platform, video_info):
        """Procesa el video específicamente para una plataforma"""
        config = self.platform_configs.get(platform)
        if not config:
            raise Exception(f"Configuración no encontrada para plataforma: {platform}")
        
        output_path = os.path.join(
            self.temp_dir,
            f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        
        # Construir comando FFmpeg
        cmd = ['ffmpeg', '-i', video_path]
        
        # Configurar video
        cmd.extend(['-c:v', 'libx264'])
        cmd.extend(['-b:v', config['bitrate']])
        cmd.extend(['-r', str(config['fps'])])
        
        # Configurar resolución (mantener proporción si es necesario)
        target_width = config['resolution']['width']
        target_height = config['resolution']['height']
        
        # Filtro para redimensionar manteniendo calidad
        scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black"
        cmd.extend(['-vf', scale_filter])
        
        # Configurar audio
        if video_info.get('has_audio', True):
            cmd.extend(['-c:a', 'aac'])
            cmd.extend(['-b:a', config['audio_bitrate']])
        else:
            cmd.extend(['-an'])  # Sin audio
        
        # Limitar duración si es necesario
        if video_info['duration'] > config['max_duration']:
            cmd.extend(['-t', str(config['max_duration'])])
        
        # Configuraciones adicionales para calidad
        cmd.extend(['-preset', 'slow'])  # Mejor calidad
        cmd.extend(['-crf', '18'])  # Calidad alta (0-51, menor = mejor)
        cmd.extend(['-pix_fmt', 'yuv420p'])  # Compatibilidad
        
        # Archivo de salida
        cmd.extend(['-y', output_path])  # -y para sobrescribir
        
        # Ejecutar comando
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"Error en FFmpeg: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise Exception("El archivo procesado no se generó")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout procesando video")
        except Exception as e:
            raise Exception(f"Error ejecutando FFmpeg: {str(e)}")
    
    def extract_thumbnail(self, video_path, timestamp=1.0):
        """Extrae miniatura del video en un timestamp específico"""
        try:
            thumbnail_path = os.path.join(
                self.temp_dir,
                f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            )
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', str(timestamp),
                '-vframes', '1',
                '-q:v', '2',  # Alta calidad
                '-y', thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(thumbnail_path):
                return thumbnail_path
            else:
                # Fallback con OpenCV
                return self.extract_thumbnail_opencv(video_path, timestamp)
                
        except Exception as e:
            print(f"Error extrayendo miniatura: {str(e)}")
            return None
    
    def extract_thumbnail_opencv(self, video_path, timestamp=1.0):
        """Extrae miniatura usando OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(fps * timestamp)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if ret:
                thumbnail_path = os.path.join(
                    self.temp_dir,
                    f"thumb_cv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )
                cv2.imwrite(thumbnail_path, frame)
                cap.release()
                return thumbnail_path
            
            cap.release()
            return None
            
        except Exception as e:
            print(f"Error extrayendo miniatura con OpenCV: {str(e)}")
            return None
    
    def extract_high_quality_thumbnail(self, video_path):
        """Extrae miniatura de alta calidad desde el centro del video"""
        try:
            # Obtener duración del video
            video_info = self.analyze_video(video_path)
            duration = video_info.get('duration', 10)
            
            # Extraer desde el centro del video
            center_timestamp = duration / 2
            
            return self.extract_thumbnail(video_path, center_timestamp)
            
        except Exception as e:
            print(f"Error extrayendo miniatura de alta calidad: {str(e)}")
            return self.extract_thumbnail(video_path, 1.0)
    
    def calculate_aspect_ratio(self, width, height):
        """Calcula la proporción de aspecto"""
        if height == 0:
            return 0
        return width / height
    
    def parse_fps(self, fps_string):
        """Parsea string de FPS (ej: '30/1') a número"""
        try:
            if '/' in fps_string:
                numerator, denominator = fps_string.split('/')
                return float(numerator) / float(denominator)
            return float(fps_string)
        except:
            return 30.0  # Default
    
    def get_default_video_info(self):
        """Retorna información de video por defecto en caso de error"""
        return {
            'duration': 0,
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'bitrate': 0,
            'codec': 'unknown',
            'has_audio': True,
            'audio_codec': 'unknown',
            'file_size': 0,
            'aspect_ratio': 9/16
        }
    
    def create_processing_report(self, original_path, processed_path, original_info):
        """Crea un reporte del procesamiento realizado"""
        try:
            processed_info = self.analyze_video(processed_path)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'original_file': original_path,
                'processed_file': processed_path,
                'original_info': original_info,
                'processed_info': processed_info,
                'improvements': {
                    'resolution_optimized': (
                        processed_info['width'] == 1080 and 
                        processed_info['height'] == 1920
                    ),
                    'duration_compliant': processed_info['duration'] <= 180,
                    'file_size_reduction': (
                        original_info['file_size'] > processed_info['file_size']
                    ),
                    'quality_maintained': processed_info['fps'] >= 30
                }
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f"Error creando reporte: {str(e)}"
            }
    
    def cleanup(self):
        """Limpia archivos temporales"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error limpiando archivos temporales: {str(e)}")
    
    def __del__(self):
        """Limpieza automática al destruir el objeto"""
        self.cleanup() 