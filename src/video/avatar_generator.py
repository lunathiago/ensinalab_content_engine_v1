"""
Gerador com Avatar: Apresentador Virtual + TTS
Mais profissional, ideal para educação
"""
import os
import requests
import time
from typing import Dict
from pathlib import Path

from src.video.base_generator import BaseVideoGenerator


class AvatarVideoGenerator(BaseVideoGenerator):
    """
    Gerador com avatar virtual (HeyGen ou D-ID)
    
    Features:
    - Apresentador realista falando o script
    - Sincronização labial perfeita
    - Expressões faciais naturais
    - Background customizável
    - Slides de suporte opcionais
    
    Custo: ~$3-10/vídeo
    """
    
    def __init__(self, provider: str = "heygen"):
        super().__init__()
        self.provider = provider.lower()
        
        if self.provider == "heygen":
            self.api_key = os.getenv("HEYGEN_API_KEY")
            self.api_url = "https://api.heygen.com/v2/video/generate"
            if not self.api_key:
                raise ValueError("HEYGEN_API_KEY não configurada")
        elif self.provider == "d-id":
            self.api_key = os.getenv("DID_API_KEY")
            self.api_url = "https://api.d-id.com/talks"
            if not self.api_key:
                raise ValueError("DID_API_KEY não configurada")
        else:
            raise ValueError(f"Provider desconhecido: {provider}. Use 'heygen' ou 'd-id'")
    
    def generate(
        self, 
        script: str,
        title: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """Gera vídeo com avatar"""
        
        try:
            print(f"🎭 [AvatarGenerator] Gerando vídeo {video_id} com {self.provider}...")
            
            if self.provider == "heygen":
                result = self._generate_heygen(script, title, metadata, video_id)
            elif self.provider == "d-id":
                result = self._generate_did(script, title, metadata, video_id)
            else:
                raise ValueError(f"Provider não implementado: {self.provider}")
            
            return result
            
        except Exception as e:
            print(f"❌ [AvatarGenerator] Erro: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_heygen(self, script: str, title: str, metadata: Dict, video_id: int) -> Dict:
        """Gera vídeo usando HeyGen API"""
        
        # Mapear tom para avatar
        avatar_map = {
            'profissional': 'Anna_public_3_20240108',
            'casual': 'josh_lite3_20230714',
            'motivacional': 'Anna_public_3_20240108',
            'técnico': 'josh_lite3_20230714',
            'objetivo': 'Anna_public_3_20240108',
            'prático': 'josh_lite3_20230714'
        }
        
        avatar_id = avatar_map.get(metadata.get('tone', 'profissional'), 'Anna_public_3_20240108')
        
        # Payload da API
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script[:5000],  # Limite de caracteres
                        "voice_id": "pt-BR-FranciscaNeural",
                        "speed": 1.0
                    },
                    "background": {
                        "type": "color",
                        "value": "#1a1a2e"
                    }
                }
            ],
            "dimension": {
                "width": 1920,
                "height": 1080
            },
            "test": False,
            "title": title
        }
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Enviar requisição
        print("   → Enviando para HeyGen...")
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') != 100:
            raise Exception(f"HeyGen retornou erro: {data.get('message')}")
        
        video_id_heygen = data['data']['video_id']
        
        print(f"   → Video ID HeyGen: {video_id_heygen}")
        print("   → Aguardando processamento (pode levar 2-5 minutos)...")
        
        # Polling até completar
        video_url = self._poll_heygen_status(video_id_heygen)
        
        # Download do vídeo
        output_path = str(self.output_dir / f"video_{video_id}_avatar_heygen.mp4")
        self._download_video(video_url, output_path)
        
        # Gerar thumbnail
        thumbnail_path = self._create_thumbnail(output_path)
        
        # Obter informações
        file_info = self._get_file_info(output_path)
        
        print(f"✅ [AvatarGenerator/HeyGen] Vídeo gerado: {output_path}")
        
        return {
            'success': True,
            'file_path': output_path,
            'duration': file_info['duration'],
            'file_size': file_info['file_size'],
            'thumbnail_path': thumbnail_path,
            'metadata': {
                'generator': 'avatar',
                'provider': 'heygen',
                'avatar_id': avatar_id,
                'video_id_heygen': video_id_heygen,
                'resolution': f"{file_info['width']}x{file_info['height']}"
            }
        }
    
    def _poll_heygen_status(self, video_id: str, max_attempts: int = 60, interval: int = 10) -> str:
        """Polling do status até completar"""
        
        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"X-Api-Key": self.api_key}
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                status = data['data']['status']
                print(f"      Status: {status} ({attempt+1}/{max_attempts})")
                
                if status == 'completed':
                    return data['data']['video_url']
                elif status == 'failed':
                    error_msg = data['data'].get('error', 'Erro desconhecido')
                    raise Exception(f"HeyGen falhou: {error_msg}")
                
                time.sleep(interval)
                
            except requests.exceptions.RequestException as e:
                print(f"      Erro ao consultar status: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval)
                else:
                    raise
        
        raise Exception(f"Timeout aguardando HeyGen após {max_attempts * interval}s")
    
    def _generate_did(self, script: str, title: str, metadata: Dict, video_id: int) -> Dict:
        """Gera vídeo usando D-ID API"""
        
        # Escolher apresentador baseado no tom
        presenter_map = {
            'profissional': 'amy-jcwCkr1grs',
            'casual': 'eric-X3fJDqcLKi',
            'motivacional': 'amy-jcwCkr1grs',
            'técnico': 'eric-X3fJDqcLKi'
        }
        
        presenter_id = presenter_map.get(metadata.get('tone', 'profissional'), 'amy-jcwCkr1grs')
        
        payload = {
            "script": {
                "type": "text",
                "input": script[:3000],  # Limite D-ID
                "provider": {
                    "type": "microsoft",
                    "voice_id": "pt-BR-FranciscaNeural"
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0,
                "driver_expressions": {
                    "expressions": [
                        {"expression": "neutral", "start_frame": 0, "intensity": 1.0}
                    ]
                }
            },
            "source_url": f"https://create-images-results.d-id.com/{presenter_id}.jpg"
        }
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Enviar requisição
        print("   → Enviando para D-ID...")
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        talk_id = data['id']
        
        print(f"   → Talk ID D-ID: {talk_id}")
        print("   → Aguardando processamento (1-3 minutos)...")
        
        # Polling
        video_url = self._poll_did_status(talk_id)
        
        # Download
        output_path = str(self.output_dir / f"video_{video_id}_avatar_did.mp4")
        self._download_video(video_url, output_path)
        
        # Thumbnail
        thumbnail_path = self._create_thumbnail(output_path)
        
        # Info
        file_info = self._get_file_info(output_path)
        
        print(f"✅ [AvatarGenerator/D-ID] Vídeo gerado: {output_path}")
        
        return {
            'success': True,
            'file_path': output_path,
            'duration': file_info['duration'],
            'file_size': file_info['file_size'],
            'thumbnail_path': thumbnail_path,
            'metadata': {
                'generator': 'avatar',
                'provider': 'd-id',
                'talk_id': talk_id,
                'presenter_id': presenter_id,
                'resolution': f"{file_info['width']}x{file_info['height']}"
            }
        }
    
    def _poll_did_status(self, talk_id: str, max_attempts: int = 60, interval: int = 5) -> str:
        """Polling D-ID status"""
        
        status_url = f"https://api.d-id.com/talks/{talk_id}"
        headers = {"Authorization": f"Basic {self.api_key}"}
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                status = data['status']
                print(f"      Status: {status} ({attempt+1}/{max_attempts})")
                
                if status == 'done':
                    return data['result_url']
                elif status == 'error':
                    error_msg = data.get('error', {}).get('description', 'Erro desconhecido')
                    raise Exception(f"D-ID falhou: {error_msg}")
                
                time.sleep(interval)
                
            except requests.exceptions.RequestException as e:
                print(f"      Erro ao consultar status: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval)
                else:
                    raise
        
        raise Exception(f"Timeout aguardando D-ID após {max_attempts * interval}s")
    
    def _download_video(self, url: str, output_path: str):
        """Download do vídeo gerado"""
        print(f"   → Baixando vídeo...")
        
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r      Download: {progress:.1f}%", end='', flush=True)
        
        print(f"\n   → Download concluído: {output_path}")
    
    def estimate_cost(self, script: str, duration_minutes: int) -> float:
        """Estima custo"""
        if self.provider == "heygen":
            # HeyGen: ~$6-12/min (créditos)
            return 8.0 * duration_minutes
        elif self.provider == "d-id":
            # D-ID: ~$0.30-0.60/min
            return 0.45 * duration_minutes
        return 5.0 * duration_minutes
    
    def supports_language(self, language: str) -> bool:
        """Suporta múltiplos idiomas"""
        supported = [
            'pt-BR', 'pt-PT', 'en-US', 'en-GB', 'es-ES', 'es-MX',
            'fr-FR', 'de-DE', 'it-IT', 'ja-JP', 'ko-KR', 'zh-CN'
        ]
        return language in supported
