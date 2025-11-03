"""
Gerador de vídeos usando MoviePy + FFmpeg
"""
import os
from typing import Dict, Optional
from moviepy.editor import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips
)
from src.config.settings import settings

class VideoGenerator:
    """Gerador de vídeos educacionais"""
    
    def __init__(self):
        self.output_dir = settings.VIDEO_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_video(
        self, 
        script: str, 
        audio_path: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """
        Gera vídeo completo
        
        Args:
            script: Roteiro completo
            audio_path: Caminho do arquivo de áudio (TTS)
            metadata: Metadados do vídeo (título, duração, etc)
            video_id: ID do vídeo no banco
        
        Returns:
            Dict com informações do vídeo gerado
        """
        try:
            # 1. Carregar áudio
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # 2. Gerar slides com texto (simplificado)
            scenes = self._parse_script_to_scenes(script, duration)
            video_clips = []
            
            for scene in scenes:
                clip = self._create_scene_clip(
                    text=scene['text'],
                    duration=scene['duration']
                )
                video_clips.append(clip)
            
            # 3. Concatenar cenas
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # 4. Adicionar áudio
            final_video = final_video.set_audio(audio)
            
            # 5. Salvar
            output_path = os.path.join(self.output_dir, f"video_{video_id}.mp4")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac"
            )
            
            # 6. Gerar thumbnail
            thumbnail_path = self._generate_thumbnail(final_video, video_id)
            
            # 7. Limpar recursos
            audio.close()
            final_video.close()
            
            return {
                "file_path": output_path,
                "file_size": os.path.getsize(output_path),
                "duration": int(duration),
                "thumbnail_path": thumbnail_path
            }
            
        except Exception as e:
            print(f"Erro ao gerar vídeo: {e}")
            raise
    
    def _parse_script_to_scenes(self, script: str, total_duration: float) -> list:
        """
        Divide roteiro em cenas
        """
        # Simplificado: divide por parágrafos
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [script]
        
        scene_duration = total_duration / len(paragraphs)
        
        scenes = []
        for paragraph in paragraphs:
            scenes.append({
                'text': paragraph[:200],  # Limita texto
                'duration': scene_duration
            })
        
        return scenes
    
    def _create_scene_clip(self, text: str, duration: float) -> ImageClip:
        """
        Cria um clip de cena com texto sobre fundo
        """
        # Fundo simples (azul)
        bg_clip = ImageClip(
            self._create_solid_color((1920, 1080), (41, 128, 185)),
            duration=duration
        )
        
        # Texto
        try:
            txt_clip = TextClip(
                text,
                fontsize=48,
                color='white',
                size=(1600, 900),
                method='caption',
                align='center'
            ).set_duration(duration).set_position('center')
            
            # Compor
            return CompositeVideoClip([bg_clip, txt_clip])
        except:
            # Fallback se TextClip falhar
            return bg_clip
    
    def _create_solid_color(self, size: tuple, color: tuple) -> str:
        """
        Cria imagem temporária de cor sólida
        """
        import numpy as np
        from PIL import Image
        
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        img[:] = color
        
        temp_path = f"/tmp/bg_{color[0]}_{color[1]}_{color[2]}.png"
        Image.fromarray(img).save(temp_path)
        
        return temp_path
    
    def _generate_thumbnail(self, video_clip, video_id: int) -> str:
        """Gera thumbnail do vídeo"""
        thumbnail_path = os.path.join(self.output_dir, f"thumb_{video_id}.jpg")
        
        # Captura frame no meio do vídeo
        frame_time = video_clip.duration / 2
        frame = video_clip.get_frame(frame_time)
        
        from PIL import Image
        Image.fromarray(frame).save(thumbnail_path, quality=85)
        
        return thumbnail_path
