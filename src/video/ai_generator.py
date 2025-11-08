"""
Gerador com IA Generativa: Text-to-Video
Mais avançado e cinematográfico (experimental)
"""
import os
import requests
import time
from typing import Dict, List
from pathlib import Path

from src.video.base_generator import BaseVideoGenerator


class AIVideoGenerator(BaseVideoGenerator):
    """
    Gerador com IA generativa (Kling AI, Runway Gen-3)
    
    Features:
    - Geração de vídeo a partir de texto/prompt
    - Visual cinematográfico
    - Edição automática de cenas
    - B-roll gerado por IA
    - Narração com TTS
    
    Custo: ~$30-100/vídeo (experimental)
    """
    
    def __init__(self, provider: str = "kling"):
        super().__init__()
        self.provider = provider.lower()
        
        if self.provider == "kling":
            self.api_key = os.getenv("KLING_API_KEY")
            self.api_url = "https://api.klingai.com/v1/videos/text2video"
            if not self.api_key:
                raise ValueError("KLING_API_KEY não configurada")
        elif self.provider == "runway":
            self.api_key = os.getenv("RUNWAY_API_KEY")
            self.api_url = "https://api.runwayml.com/v1/generate"
            if not self.api_key:
                raise ValueError("RUNWAY_API_KEY não configurada")
        else:
            raise ValueError(f"Provider desconhecido: {provider}. Use 'kling' ou 'runway'")
    
    def generate(
        self, 
        script: str,
        title: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """Gera vídeo com IA generativa"""
        
        try:
            print(f"🚀 [AIGenerator] Gerando vídeo {video_id} com {self.provider}...")
            print("⚠️  Modo experimental - pode levar 5-15 minutos")
            
            # 1. Quebrar script em cenas
            scenes = self._parse_scenes(script, title)
            print(f"   → {len(scenes)} cenas identificadas")
            
            # 2. Gerar vídeo para cada cena
            scene_videos = []
            for i, scene in enumerate(scenes):
                print(f"   → Gerando cena {i+1}/{len(scenes)}: {scene['prompt'][:50]}...")
                
                if self.provider == "kling":
                    video_path = self._generate_kling_scene(scene, video_id, i)
                elif self.provider == "runway":
                    video_path = self._generate_runway_scene(scene, video_id, i)
                else:
                    raise ValueError(f"Provider não suportado: {self.provider}")
                
                scene_videos.append(video_path)
            
            # 3. Concatenar cenas
            print("   → Concatenando cenas...")
            final_path = self._concatenate_scenes(scene_videos, video_id)
            
            # 4. Adicionar narração (opcional)
            # TODO: Implementar narração com TTS
            
            # 5. Gerar thumbnail
            thumbnail_path = self._create_thumbnail(final_path)
            
            # 6. Obter informações
            file_info = self._get_file_info(final_path)
            
            print(f"✅ [AIGenerator] Vídeo gerado: {final_path}")
            
            return {
                'success': True,
                'file_path': final_path,
                'duration': file_info['duration'],
                'file_size': file_info['file_size'],
                'thumbnail_path': thumbnail_path,
                'metadata': {
                    'generator': 'ai',
                    'provider': self.provider,
                    'scenes_count': len(scenes),
                    'scene_videos': scene_videos,
                    'resolution': f"{file_info['width']}x{file_info['height']}"
                }
            }
            
        except Exception as e:
            print(f"❌ [AIGenerator] Erro: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_scenes(self, script: str, title: str) -> List[Dict]:
        """Quebra script em cenas visuais"""
        # Usar LLM para gerar prompts visuais
        from src.ml.llm_service import LLMService
        
        llm = LLMService()
        
        prompt = f"""Você é um diretor de fotografia educacional.
Dado o script abaixo, crie 3-5 prompts visuais para geração de vídeo.
Cada prompt deve descrever uma cena visual que ilustra parte do conteúdo.

Script:
{script[:2000]}

Retorne em formato JSON:
[
  {{"prompt": "descrição visual da cena 1", "duration": 5}},
  {{"prompt": "descrição visual da cena 2", "duration": 5}}
]

Prompts devem ser:
- Visuais e descritivos
- Apropriados para educação
- Profissionais e relevantes
- Em inglês (para melhor geração)
"""
        
        response = llm.generate(prompt, temperature=0.7)
        
        # Parse JSON
        import json
        import re
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                scenes = json.loads(json_match.group())
                return scenes
            except:
                pass
        
        # Fallback: cenas genéricas
        return [
            {"prompt": f"Educational video about {title}, professional setting, modern classroom", "duration": 5},
            {"prompt": f"Teacher presenting concepts, engaging visual aids, professional education", "duration": 5},
            {"prompt": f"Students learning, collaborative environment, technology integration", "duration": 5}
        ]
    
    def _generate_kling_scene(self, scene: Dict, video_id: int, scene_num: int) -> str:
        """Gera cena usando Kling AI"""
        
        payload = {
            "prompt": scene['prompt'],
            "duration": scene.get('duration', 5),
            "aspect_ratio": "16:9",
            "cfg_scale": 0.5,
            "mode": "std"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Submeter geração
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        task_id = data['data']['task_id']
        
        print(f"      Task ID: {task_id}")
        
        # Polling até completar
        video_url = self._poll_kling_status(task_id)
        
        # Download
        output_path = str(self.output_dir / f"scene_{video_id}_{scene_num:02d}.mp4")
        self._download_video_simple(video_url, output_path)
        
        return output_path
    
    def _poll_kling_status(self, task_id: str, max_attempts: int = 120, interval: int = 10) -> str:
        """Polling Kling AI status"""
        
        status_url = f"https://api.klingai.com/v1/videos/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                status = data['data']['status']
                print(f"         Status: {status} ({attempt+1}/{max_attempts})")
                
                if status == 'succeed':
                    return data['data']['works'][0]['resource']['resource']
                elif status == 'failed':
                    raise Exception(f"Kling AI falhou: {data['data'].get('error_message')}")
                
                time.sleep(interval)
                
            except requests.exceptions.RequestException as e:
                print(f"         Erro ao consultar: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval)
                else:
                    raise
        
        raise Exception(f"Timeout aguardando Kling AI")
    
    def _generate_runway_scene(self, scene: Dict, video_id: int, scene_num: int) -> str:
        """Gera cena usando Runway Gen-3"""
        
        payload = {
            "text_prompt": scene['prompt'],
            "duration": scene.get('duration', 5),
            "model": "gen3",
            "aspect_ratio": "16:9"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Submeter
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        task_id = data['id']
        
        print(f"      Task ID: {task_id}")
        
        # Polling
        video_url = self._poll_runway_status(task_id)
        
        # Download
        output_path = str(self.output_dir / f"scene_{video_id}_{scene_num:02d}.mp4")
        self._download_video_simple(video_url, output_path)
        
        return output_path
    
    def _poll_runway_status(self, task_id: str, max_attempts: int = 120, interval: int = 10) -> str:
        """Polling Runway status"""
        
        status_url = f"https://api.runwayml.com/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                status = data['status']
                print(f"         Status: {status} ({attempt+1}/{max_attempts})")
                
                if status == 'SUCCEEDED':
                    return data['output'][0]
                elif status == 'FAILED':
                    raise Exception(f"Runway falhou: {data.get('failure_reason')}")
                
                time.sleep(interval)
                
            except requests.exceptions.RequestException as e:
                print(f"         Erro: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval)
                else:
                    raise
        
        raise Exception("Timeout aguardando Runway")
    
    def _download_video_simple(self, url: str, output_path: str):
        """Download simples"""
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    
    def _concatenate_scenes(self, scene_videos: List[str], video_id: int) -> str:
        """Concatena cenas em vídeo final"""
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        
        clips = [VideoFileClip(path) for path in scene_videos]
        final_clip = concatenate_videoclips(clips, method="compose")
        
        output_path = str(self.output_dir / f"video_{video_id}_ai.mp4")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # Limpar
        final_clip.close()
        for clip in clips:
            clip.close()
        
        return output_path
    
    def estimate_cost(self, script: str, duration_minutes: int) -> float:
        """Estima custo"""
        if self.provider == "kling":
            # Kling: ~$0.50-1/segundo
            return 0.75 * duration_minutes * 60
        elif self.provider == "runway":
            # Runway Gen-3: ~$0.80-1.50/segundo
            return 1.0 * duration_minutes * 60
        return 50.0 * duration_minutes
    
    def supports_language(self, language: str) -> bool:
        """Prompts funcionam melhor em inglês"""
        return language in ['en-US', 'en-GB']
