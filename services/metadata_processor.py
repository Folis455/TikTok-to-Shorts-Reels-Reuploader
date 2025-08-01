import os
import json
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import hashlib

class MetadataProcessor:
    def __init__(self):
        self.default_hashtags = {
            'youtube': ['#Shorts', '#YouTubeShorts', '#Viral', '#Trending'],
            'instagram': ['#reels', '#instagram', '#viral', '#fyp', '#parati']
        }
        
        self.emoji_patterns = {
            'fire': '🔥',
            'heart': '❤️',
            'laugh': '😂',
            'wow': '😱',
            'think': '🤔',
            'music': '🎵',
            'dance': '💃',
            'fun': '🤩'
        }
    
    def process_description(self, original_description, platform='both', custom_hashtags=None):
        """
        Procesa y optimiza la descripción para cada plataforma
        
        Args:
            original_description (str): Descripción original del TikTok
            platform (str): 'youtube', 'instagram' o 'both'
            custom_hashtags (list): Hashtags personalizados adicionales
            
        Returns:
            dict: Descripciones optimizadas para cada plataforma
        """
        try:
            # Limpiar descripción original
            cleaned_description = self.clean_description(original_description)
            
            # Detectar y convertir hashtags de TikTok
            converted_hashtags = self.convert_tiktok_hashtags(cleaned_description)
            
            # Agregar emojis relevantes
            enhanced_description = self.enhance_with_emojis(cleaned_description)
            
            result = {}
            
            if platform in ['youtube', 'both']:
                result['youtube'] = self.format_for_youtube(
                    enhanced_description, 
                    converted_hashtags, 
                    custom_hashtags
                )
            
            if platform in ['instagram', 'both']:
                result['instagram'] = self.format_for_instagram(
                    enhanced_description, 
                    converted_hashtags, 
                    custom_hashtags
                )
            
            return result
            
        except Exception as e:
            print(f"Error procesando descripción: {str(e)}")
            return {
                'youtube': original_description,
                'instagram': original_description
            }
    
    def clean_description(self, description):
        """Limpia la descripción eliminando elementos no deseados"""
        if not description:
            return ""
        
        # Eliminar URLs de TikTok
        description = re.sub(r'https?://(?:www\.)?tiktok\.com/\S+', '', description)
        
        # Eliminar menciones de usuarios específicas de TikTok
        description = re.sub(r'@[\w.]+', '', description)
        
        # Limpiar espacios múltiples
        description = re.sub(r'\s+', ' ', description).strip()
        
        return description
    
    def convert_tiktok_hashtags(self, description):
        """Convierte hashtags de TikTok a equivalentes para otras plataformas"""
        hashtag_mapping = {
            '#fyp': ['#viral', '#trending'],
            '#foryou': ['#parati', '#viral'],
            '#foryoupage': ['#explore', '#trending'],
            '#tiktokviral': ['#viral', '#trending'],
            '#viralvideo': ['#viral'],
            '#trending': ['#trending', '#viral'],
            '#parati': ['#parati', '#fyp'],
            '#viral': ['#viral', '#trending']
        }
        
        converted = []
        
        # Extraer hashtags existentes
        existing_hashtags = re.findall(r'#\w+', description.lower())
        
        for hashtag in existing_hashtags:
            if hashtag in hashtag_mapping:
                converted.extend(hashtag_mapping[hashtag])
            else:
                converted.append(hashtag)
        
        return list(set(converted))  # Eliminar duplicados
    
    def enhance_with_emojis(self, description):
        """Agrega emojis relevantes basados en el contenido"""
        if not description:
            return description
        
        description_lower = description.lower()
        
        # Detectar palabras clave y agregar emojis
        for keyword, emoji in self.emoji_patterns.items():
            if keyword in description_lower and emoji not in description:
                # Agregar emoji al inicio si es relevante
                if keyword in ['fire', 'wow']:
                    description = f"{emoji} {description}"
                # Agregar emoji al final para otros casos
                else:
                    description = f"{description} {emoji}"
        
        return description
    
    def format_for_youtube(self, description, hashtags, custom_hashtags=None):
        """Formatea descripción optimizada para YouTube Shorts"""
        # Límite de caracteres para YouTube
        max_chars = 5000
        
        # Hashtags base para YouTube
        youtube_hashtags = self.default_hashtags['youtube'].copy()
        youtube_hashtags.extend(hashtags)
        
        if custom_hashtags:
            youtube_hashtags.extend(custom_hashtags)
        
        # Eliminar duplicados y limitar cantidad
        youtube_hashtags = list(set(youtube_hashtags))[:15]
        
        # Construir descripción
        formatted = description
        
        # Agregar separador si hay contenido
        if formatted:
            formatted += "\n\n"
        
        # Agregar hashtags
        formatted += " ".join(youtube_hashtags)
        
        # Agregar call to action
        formatted += "\n\n🔔 ¡Suscríbete para más contenido viral!"
        formatted += "\n👍 ¡Dale LIKE si te gustó!"
        formatted += "\n💬 ¡Cuéntame en los comentarios qué opinas!"
        
        # Agregar información adicional
        formatted += "\n\n📱 Sígueme en mis redes sociales"
        formatted += "\n🎬 Videos nuevos todos los días"
        
        return formatted[:max_chars]
    
    def format_for_instagram(self, description, hashtags, custom_hashtags=None):
        """Formatea descripción optimizada para Instagram Reels"""
        # Límite de caracteres para Instagram
        max_chars = 2200
        
        # Hashtags base para Instagram
        instagram_hashtags = self.default_hashtags['instagram'].copy()
        instagram_hashtags.extend(hashtags)
        
        if custom_hashtags:
            instagram_hashtags.extend(custom_hashtags)
        
        # Eliminar duplicados y limitar cantidad
        instagram_hashtags = list(set(instagram_hashtags))[:30]
        
        # Construir descripción
        formatted = description
        
        # Agregar separador si hay contenido
        if formatted:
            formatted += "\n\n"
        
        # Agregar call to action específico para Instagram
        formatted += "❤️ Dale like si te gustó\n"
        formatted += "🔄 Comparte con tus amigos\n"
        formatted += "💬 ¿Qué opinas? ¡Comenta!\n"
        formatted += "➡️ Sígueme para más contenido\n\n"
        
        # Agregar hashtags
        formatted += " ".join(instagram_hashtags)
        
        return formatted[:max_chars]
    
    def extract_keywords(self, description):
        """Extrae palabras clave relevantes de la descripción"""
        if not description:
            return []
        
        # Palabras comunes a ignorar
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no',
            'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como',
            'las', 'del', 'los', 'una', 'al', 'todo', 'esta', 'sus', 'mi', 'me',
            'si', 'ya', 'o', 'pero', 'más', 'tiene', 'muy', 'hasta', 'cuando',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'
        }
        
        # Extraer palabras
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filtrar palabras relevantes
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:10]  # Limitar a 10 palabras clave
    
    def generate_alternative_descriptions(self, original_description, count=3):
        """Genera descripciones alternativas para A/B testing"""
        alternatives = []
        
        base_description = self.clean_description(original_description)
        
        # Versión 1: Formal
        formal = f"🎬 {base_description}\n\n✨ Contenido de calidad todos los días"
        alternatives.append({
            'style': 'formal',
            'description': formal
        })
        
        # Versión 2: Casual
        casual = f"😎 {base_description}\n\n🔥 ¿Te gustó? ¡Déjame tu opinión!"
        alternatives.append({
            'style': 'casual',
            'description': casual
        })
        
        # Versión 3: Con pregunta
        question = f"{base_description}\n\n🤔 ¿Qué harías tú en esta situación?"
        alternatives.append({
            'style': 'engaging',
            'description': question
        })
        
        return alternatives[:count]
    
    def process_thumbnail(self, thumbnail_path, platform='both'):
        """Procesa miniatura para optimizarla según la plataforma"""
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            return None
        
        try:
            # Abrir imagen
            img = Image.open(thumbnail_path)
            
            result = {}
            
            if platform in ['youtube', 'both']:
                # YouTube prefiere 16:9 pero acepta 9:16 para Shorts
                youtube_thumb = self.optimize_thumbnail_for_youtube(img)
                result['youtube'] = youtube_thumb
            
            if platform in ['instagram', 'both']:
                # Instagram Reels prefiere 9:16
                instagram_thumb = self.optimize_thumbnail_for_instagram(img)
                result['instagram'] = instagram_thumb
            
            return result
            
        except Exception as e:
            print(f"Error procesando miniatura: {str(e)}")
            return None
    
    def optimize_thumbnail_for_youtube(self, img):
        """Optimiza miniatura para YouTube"""
        # YouTube Shorts: 1080x1920 (9:16) o 1280x720 (16:9)
        target_size = (1080, 1920)  # Para Shorts verticales
        
        # Redimensionar manteniendo proporción
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Guardar versión optimizada
        output_path = thumbnail_path.replace('.jpg', '_youtube.jpg')
        img_resized.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def optimize_thumbnail_for_instagram(self, img):
        """Optimiza miniatura para Instagram"""
        # Instagram Reels: 1080x1920 (9:16)
        target_size = (1080, 1920)
        
        # Redimensionar manteniendo proporción
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Guardar versión optimizada
        output_path = thumbnail_path.replace('.jpg', '_instagram.jpg')
        img_resized.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def create_metadata_report(self, original_description, processed_descriptions, video_info=None):
        """Crea un reporte detallado del procesamiento de metadatos"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'original_description': original_description,
            'processed_descriptions': processed_descriptions,
            'statistics': {
                'original_length': len(original_description) if original_description else 0,
                'youtube_length': len(processed_descriptions.get('youtube', '')),
                'instagram_length': len(processed_descriptions.get('instagram', '')),
                'keywords_extracted': len(self.extract_keywords(original_description))
            }
        }
        
        if video_info:
            report['video_info'] = video_info
        
        return report 