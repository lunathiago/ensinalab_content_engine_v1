"""
Interface base para geradores de vídeo
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path
import os


class BaseVideoGenerator(ABC):
    """Interface base para todos os geradores de vídeo"""
    
    def __init__(self):
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def generate(
        self, 
        script: str,
        title: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """
        Gera um vídeo
        
        Args:
            script: Roteiro do vídeo
            title: Título do vídeo
            metadata: Metadados adicionais (tom, público-alvo, etc)
            video_id: ID do vídeo no banco
            
        Returns:
            Dict com:
                - success: bool
                - file_path: str (caminho do vídeo)
                - duration: float (segundos)
                - file_size: int (bytes)
                - thumbnail_path: str
                - metadata: Dict
                - error: str (se success=False)
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, script: str, duration_minutes: int) -> float:
        """Estima custo de geração em USD"""
        pass
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Verifica se suporta o idioma"""
        pass
    
    def _create_thumbnail(self, video_path: str) -> str:
        """Gera thumbnail do vídeo"""
        try:
            from moviepy.editor import VideoFileClip
            
            clip = VideoFileClip(video_path)
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            
            # Captura frame aos 10% do vídeo
            frame_time = min(clip.duration * 0.1, clip.duration - 0.1)
            clip.save_frame(thumbnail_path, t=frame_time)
            clip.close()
            
            return thumbnail_path
        except Exception as e:
            print(f"⚠️  Erro ao gerar thumbnail: {e}")
            return ""
    
    def _get_file_info(self, video_path: str) -> Dict:
        """Obtém informações do arquivo de vídeo"""
        try:
            from moviepy.editor import VideoFileClip
            
            file_size = os.path.getsize(video_path)
            
            clip = VideoFileClip(video_path)
            duration = clip.duration
            width = clip.w
            height = clip.h
            fps = clip.fps
            clip.close()
            
            return {
                'file_size': file_size,
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps
            }
        except Exception as e:
            print(f"⚠️  Erro ao obter info do vídeo: {e}")
            return {
                'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0,
                'duration': 0,
                'width': 1920,
                'height': 1080,
                'fps': 24
            }
