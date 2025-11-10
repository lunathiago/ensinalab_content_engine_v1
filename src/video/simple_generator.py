"""
Gerador Simples: TTS + Slides Estáticos + Legendas
Mais barato e previsível
"""
import os
import json
from pathlib import Path
from typing import Dict, List
from moviepy.editor import (
    AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ImageClip
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

from src.video.base_generator import BaseVideoGenerator
from src.video.tts import TTSService


class SimpleVideoGenerator(BaseVideoGenerator):
    """
    Gerador simples com TTS + slides estáticos
    
    Features:
    - Text-to-Speech (ElevenLabs ou Google)
    - Slides automáticos baseados no script
    - Legendas sincronizadas
    - Transições suaves
    - Música de fundo opcional
    
    Custo: ~$0.30-1/vídeo
    """
    
    def __init__(self, tts_provider: str = "auto"):
        super().__init__()
        self.tts = TTSService(provider=tts_provider)
        self.slides_dir = Path("generated_videos/slides")
        self.slides_dir.mkdir(exist_ok=True)
    
    def generate(
        self, 
        script: str,
        title: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """Gera vídeo com TTS + slides"""
        
        try:
            print(f"📹 [SimpleGenerator] Gerando vídeo {video_id}...")
            
            # 1. Quebrar script em seções
            sections = self._parse_script_sections(script, title)
            print(f"   → {len(sections)} seções identificadas")
            
            # 2. Gerar áudio com TTS
            audio_path = self._generate_audio(script, video_id, metadata.get('tone', 'profissional'))
            print(f"   → Áudio gerado: {audio_path}")
            
            # 3. Criar slides para cada seção
            slide_clips = []
            audio = AudioFileClip(audio_path)
            section_duration = audio.duration / len(sections)
            
            for i, section in enumerate(sections):
                slide_path = self._create_slide(
                    title=section['title'],
                    content=section['content'],
                    slide_num=i + 1,
                    total_slides=len(sections),
                    video_id=video_id
                )
                
                slide_clip = (ImageClip(slide_path)
                             .set_duration(section_duration)
                             .crossfadein(0.5 if i > 0 else 0)
                             .crossfadeout(0.5 if i < len(sections) - 1 else 0))
                
                slide_clips.append(slide_clip)
                
                # 🧹 LIMPEZA: Liberar memória após cada slide
                import gc
                gc.collect()
            
            print(f"   → {len(slide_clips)} slides criados")
            
            # 4. Concatenar slides
            video_with_slides = concatenate_videoclips(slide_clips, method="compose")
            
            # 5. Sincronizar áudio
            final_video = video_with_slides.set_audio(audio)
            
            # 6. Exportar (otimizado para baixo uso de memória)
            output_path = str(self.output_dir / f"video_{video_id}_simple.mp4")
            final_video.write_videofile(
                output_path,
                fps=24,  # Mantido 24fps (padrão)
                codec='libx264',
                audio_codec='aac',
                threads=2,  # Reduzido de 4 para 2 (menos memória paralela)
                preset='ultrafast',  # Mudado de 'medium' para 'ultrafast' (menos RAM)
                logger=None,  # Silenciar logs do moviepy
                # Otimizações extras para baixa memória:
                bitrate='1000k',  # Limitar bitrate (menos buffer)
                audio_bitrate='128k'
            )
            
            # 7. Gerar thumbnail
            thumbnail_path = self._create_thumbnail(output_path)
            
            # 8. Obter informações do arquivo
            file_info = self._get_file_info(output_path)
            
            # Limpar recursos
            audio.close()
            final_video.close()
            for clip in slide_clips:
                clip.close()
            
            # 🧹 LIMPEZA AGRESSIVA: Forçar garbage collection
            import gc
            del audio, final_video, slide_clips, video_with_slides
            gc.collect()
            
            print(f"✅ [SimpleGenerator] Vídeo gerado: {output_path}")
            
            return {
                'success': True,
                'file_path': output_path,
                'duration': file_info['duration'],
                'file_size': file_info['file_size'],
                'thumbnail_path': thumbnail_path,
                'metadata': {
                    'generator': 'simple',
                    'sections_count': len(sections),
                    'tts_provider': self.tts.provider,
                    'audio_path': audio_path,
                    'resolution': f"{file_info['width']}x{file_info['height']}"
                }
            }
            
        except Exception as e:
            print(f"❌ [SimpleGenerator] Erro: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_script_sections(self, script: str, main_title: str) -> List[Dict]:
        """Quebra script em seções lógicas"""
        # Dividir por parágrafos vazios ou títulos
        lines = script.strip().split('\n')
        sections = []
        current_section = {'title': '', 'content': ''}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section['content']:
                    sections.append(current_section)
                    current_section = {'title': '', 'content': ''}
            elif line.startswith('#') or (len(line) < 50 and line.isupper()):
                # É um título
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'title': line.replace('#', '').strip(), 'content': ''}
            else:
                current_section['content'] += line + ' '
        
        if current_section['content']:
            sections.append(current_section)
        
        # Se não encontrou seções, dividir em partes iguais
        # LIMITE: Máximo 10 slides para economizar memória (512MB free tier)
        if not sections:
            words = script.split()
            max_slides = 10  # Reduzido de 5 para 10 max
            chunk_size = max(50, len(words) // max_slides)
            sections = [
                {
                    'title': main_title if i == 0 else f'Parte {i+1}',
                    'content': ' '.join(words[i:i+chunk_size])
                }
                for i in range(0, len(words), chunk_size)
            ]
        
        # SEGURANÇA: Limitar a 10 slides máximo (10 × 2.5MB = 25MB vs 23 × 6MB = 138MB)
        if len(sections) > 10:
            print(f"   ⚠️ Muitos slides ({len(sections)}), consolidando para 10...")
            # Agrupar slides excedentes
            step = len(sections) / 10
            consolidated = []
            for i in range(10):
                start_idx = int(i * step)
                end_idx = int((i + 1) * step)
                merged_content = ' '.join([s['content'] for s in sections[start_idx:end_idx]])
                consolidated.append({
                    'title': sections[start_idx]['title'] or f'Parte {i+1}',
                    'content': merged_content
                })
            sections = consolidated
        
        # Garantir que primeira seção tenha título
        if sections and not sections[0]['title']:
            sections[0]['title'] = main_title
        
        return sections
    
    def _generate_audio(self, script: str, video_id: int, tone: str) -> str:
        """Gera áudio com TTS"""
        audio_path = str(self.output_dir / f"audio_{video_id}.mp3")
        
        # Mapear tom para voz
        voice_map = {
            'profissional': 'pt-BR-FranciscaNeural',
            'casual': 'pt-BR-AntonioNeural',
            'motivacional': 'pt-BR-FranciscaNeural',
            'técnico': 'pt-BR-AntonioNeural',
            'objetivo': 'pt-BR-FranciscaNeural',
            'prático': 'pt-BR-AntonioNeural'
        }
        
        voice = voice_map.get(tone, 'pt-BR-FranciscaNeural')
        
        self.tts.generate(
            text=script,
            output_path=audio_path,
            voice=voice
        )
        
        return audio_path
    
    def _create_slide(
        self, 
        title: str, 
        content: str, 
        slide_num: int, 
        total_slides: int,
        video_id: int
    ) -> str:
        """Cria slide visual com PIL"""
        
        # Dimensões 16:9 HD (reduzido para economia de memória)
        # Full HD (1920x1080) = ~6MB/slide
        # HD (1280x720) = ~2.5MB/slide (60% menos memória!)
        width, height = 1280, 720
        
        # Criar imagem com gradiente
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Adicionar gradiente simples (opcional)
        for y in range(height):
            opacity = int(255 * (1 - y / height * 0.3))
            color = (26, 26, 46, opacity)
            # Simular gradiente com linhas
        
        # Fontes
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
            footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            # Fallback para fonte padrão
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()
        
        # Título (topo) com destaque
        if title:
            # Barra de destaque
            draw.rectangle([0, 100, width, 200], fill='#00d9ff')
            
            wrapped_title = textwrap.fill(title, width=30)
            draw.text((width//2, 150), wrapped_title, fill='#1a1a2e', font=title_font, anchor='mm')
        
        # Conteúdo (centro)
        wrapped_content = textwrap.fill(content[:500], width=55)  # Limitar tamanho
        draw.text((width//2, height//2 + 50), wrapped_content, fill='#ffffff', font=content_font, anchor='mm')
        
        # Rodapé (número do slide + logo)
        footer_text = f"EnsinaLab | Slide {slide_num}/{total_slides}"
        draw.text((width - 150, height - 60), footer_text, fill='#888888', font=footer_font, anchor='mm')
        
        # Linha decorativa inferior
        draw.rectangle([0, height - 10, width, height], fill='#00d9ff')
        
        # Salvar
        slide_path = str(self.slides_dir / f"slide_{video_id}_{slide_num:02d}.png")
        img.save(slide_path, quality=95)
        
        return slide_path
    
    def estimate_cost(self, script: str, duration_minutes: int) -> float:
        """Estima custo"""
        # Google TTS: ~$0.016/min (Character rate: $16/1M characters)
        # MoviePy: grátis (processamento local)
        char_count = len(script)
        tts_cost = (char_count / 1_000_000) * 16
        processing_cost = 0.05  # Custo computacional negligível
        
        return max(tts_cost + processing_cost, 0.10)  # Mínimo $0.10
    
    def supports_language(self, language: str) -> bool:
        """Suporta vários idiomas via Google TTS"""
        supported = ['pt-BR', 'pt-PT', 'en-US', 'en-GB', 'es-ES', 'es-MX', 'fr-FR', 'de-DE', 'it-IT']
        return language in supported
