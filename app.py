from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import threading
import time

from services.tiktok_downloader import TikTokDownloader
from services.youtube_uploader import YouTubeUploader
from services.instagram_uploader import InstagramUploader
from services.metadata_processor import MetadataProcessor
from services.video_processor import VideoProcessor

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Inicializar servicios
tiktok_downloader = TikTokDownloader()
youtube_uploader = YouTubeUploader()
instagram_uploader = InstagramUploader()
metadata_processor = MetadataProcessor()
video_processor = VideoProcessor()

# Almacén en memoria para el estado de las tareas
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_tiktok():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Generar ID único para la tarea
        task_id = str(uuid.uuid4())
        
        # Inicializar estado de la tarea
        tasks[task_id] = {
            'status': 'downloading',
            'progress': 0,
            'message': 'Descargando video de TikTok...',
            'created_at': datetime.now().isoformat()
        }
        
        # Ejecutar descarga en hilo separado
        def download_task():
            try:
                result = tiktok_downloader.download(url, task_id)
                tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Video descargado exitosamente',
                    'result': result
                })
            except Exception as e:
                tasks[task_id].update({
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                })
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Descarga iniciada'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_to_platforms():
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        platforms = data.get('platforms', [])
        custom_description = data.get('description', '')
        
        if not video_path or not platforms:
            return jsonify({'error': 'Video path and platforms are required'}), 400
        
        task_id = str(uuid.uuid4())
        
        tasks[task_id] = {
            'status': 'uploading',
            'progress': 0,
            'message': 'Iniciando subida a plataformas...',
            'created_at': datetime.now().isoformat(),
            'uploads': {}
        }
        
        def upload_task():
            try:
                total_platforms = len(platforms)
                completed = 0
                
                for platform in platforms:
                    tasks[task_id]['message'] = f'Subiendo a {platform}...'
                    
                    if platform == 'youtube':
                        result = youtube_uploader.upload(video_path, custom_description)
                        tasks[task_id]['uploads']['youtube'] = result
                    elif platform == 'instagram':
                        result = instagram_uploader.upload(video_path, custom_description)
                        tasks[task_id]['uploads']['instagram'] = result
                    
                    completed += 1
                    tasks[task_id]['progress'] = (completed / total_platforms) * 100
                
                tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Subida completada a todas las plataformas'
                })
                
            except Exception as e:
                tasks[task_id].update({
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                })
        
        thread = threading.Thread(target=upload_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Subida iniciada'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rutas para documentos requeridos por Instagram API
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-of-service') 
def terms_of_service():
    return render_template('terms-of-service.html')

@app.route('/data-deletion')
def data_deletion():
    return render_template('data-deletion.html')

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)

@app.route('/api/process', methods=['POST'])
def process_complete():
    """Endpoint para procesar completo: descargar y subir"""
    try:
        data = request.get_json()
        url = data.get('url')
        platforms = data.get('platforms', [])
        custom_title = data.get('title', '')
        custom_description = data.get('description', '')
        
        if not url or not platforms:
            return jsonify({'error': 'URL and platforms are required'}), 400
        
        task_id = str(uuid.uuid4())
        
        # Debug info (opcional - remover en producción)
        title_preview = custom_title[:30] + "..." if custom_title else "Sin título personalizado"
        print(f"[INFO] Procesando: URL={url}, Plataformas={platforms}, Título='{title_preview}'")
        
        tasks[task_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Iniciando procesamiento...',
            'created_at': datetime.now().isoformat(),
            'video_info': None,
            'uploads': {}
        }
        
        def complete_process():
            try:
                # Paso 1: Descargar
                tasks[task_id]['message'] = 'Descargando video de TikTok...'
                tasks[task_id]['progress'] = 10
                
                download_result = tiktok_downloader.download(url, task_id)
                tasks[task_id]['video_info'] = download_result
                
                # Paso 2: Procesar video
                tasks[task_id]['message'] = 'Procesando video...'
                tasks[task_id]['progress'] = 30
                
                print(f"[INFO] Procesando video: {download_result['video_path']}")
                
                processed_video = video_processor.process(
                    download_result['video_path'],
                    download_result['metadata']
                )
                
                print(f"[INFO] Video listo para subida: {processed_video.get('path', 'ERROR')}")
                
                # Paso 3: Preparar título y descripción
                title = custom_title if custom_title else download_result['metadata']['description']
                description = custom_description if custom_description else download_result['metadata']['description']
                
                # Paso 4: Subir a plataformas
                total_platforms = len(platforms)
                upload_progress_start = 50
                upload_progress_per_platform = 50 / total_platforms
                
                for i, platform in enumerate(platforms):
                    current_progress = upload_progress_start + (i * upload_progress_per_platform)
                    tasks[task_id]['progress'] = current_progress
                    tasks[task_id]['message'] = f'Subiendo a {platform}...'
                    
                    if platform == 'youtube':
                        print(f"[INFO] 🎬 Subiendo a YouTube Shorts...")
                        try:
                            result = youtube_uploader.upload(processed_video['path'], description, processed_video['thumbnail'], title)
                            tasks[task_id]['uploads']['youtube'] = result
                            print(f"[SUCCESS] ✅ YouTube Short subido: {result.get('video_url', 'URL no disponible')}")
                        except Exception as yt_error:
                            print(f"[ERROR] ❌ Error en YouTube: {str(yt_error)}")
                            raise yt_error
                    elif platform == 'instagram':
                        print(f"[INFO] 📱 Subiendo a Instagram Reels...")
                        try:
                            result = instagram_uploader.upload(processed_video['path'], description, processed_video['thumbnail'], title)
                            tasks[task_id]['uploads']['instagram'] = result
                            print(f"[SUCCESS] ✅ Instagram Reel subido: {result.get('permalink', 'URL no disponible')}")
                        except Exception as ig_error:
                            print(f"[ERROR] ❌ Error en Instagram: {str(ig_error)}")
                            raise ig_error
                
                tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Procesamiento completado exitosamente'
                })
                
            except Exception as e:
                print(f"[ERROR] ❌ Error en procesamiento: {str(e)}")
                tasks[task_id].update({
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                })
        
        thread = threading.Thread(target=complete_process)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Procesamiento iniciado'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Iniciando TikTok to Shorts/Reels Uploader...")
    print("📱 Accede a: http://localhost:5000")
    
    # Configuración para producción
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 