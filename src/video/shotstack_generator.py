"""
Shotstack Video Generator - Cloud-based rendering (10-20x faster than MoviePy)
"""
import os
import time
import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

from src.video.base_generator import BaseVideoGenerator
from src.utils.logger import get_logger
from src.video.tts import TTSService

logger = get_logger(__name__)


class ShotstackGenerator(BaseVideoGenerator):
    """
    Gerador de vídeo usando Shotstack API
    
    Vantagens:
    - 10-20x mais rápido que MoviePy (GPU remoto)
    - CDN integrado (vídeo já disponível em URL pública)
    - Não consome recursos do servidor
    - Templates profissionais
    
    Custo:
    - Free tier: 20 renders/mês
    - Paid: $49/mês = 500 renders (~$0.10/vídeo)
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuração Shotstack
        self.api_key = os.getenv("SHOTSTACK_API_KEY")
        self.api_url = os.getenv("SHOTSTACK_API_URL", "https://api.shotstack.io/v1")
        self.stage = os.getenv("SHOTSTACK_STAGE", "stage")  # stage ou v1 (prod)
        
        if not self.api_key:
            raise ValueError("SHOTSTACK_API_KEY não configurado")
        
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # TTS Service
        self.tts = TTSService()
        
        logger.info(f"✅ ShotstackGenerator inicializado (stage: {self.stage})")
    
    def generate(
        self, 
        script: str,
        title: str,
        metadata: Dict,
        video_id: int
    ) -> Dict:
        """
        Gera vídeo usando Shotstack API
        
        Fluxo:
        1. Converter script em slides (seções)
        2. Gerar áudio via TTS
        3. Upload áudio para CDN temporário (se necessário)
        4. Montar timeline JSON (Shotstack format)
        5. Enviar render request
        6. Aguardar conclusão (polling)
        7. Retornar URL do vídeo (CDN)
        """
        try:
            logger.info(f"🎬 [ShotstackGenerator] Gerando vídeo {video_id}...")
            
            # 1. Parsear script em slides
            slides = self._parse_script_to_slides(script)
            logger.info(f"   → {len(slides)} slides identificados")
            
            # 2. Gerar áudio TTS
            audio_path = self._generate_audio(script, video_id)
            logger.info(f"   → Áudio gerado: {audio_path}")
            
            # 3. Upload áudio para CDN temporário (Shotstack requer URL público)
            audio_url = self._upload_audio(audio_path)
            logger.info(f"   → Áudio disponível: {audio_url}")
            
            # 4. Montar timeline Shotstack
            timeline = self._build_timeline(slides, audio_url, metadata)
            
            # 5. Enviar render request
            render_id = self._submit_render(timeline)
            logger.info(f"   → Render ID: {render_id}")
            
            # 6. Aguardar conclusão
            video_url = self._poll_render_status(render_id, timeout=300)  # 5min max
            logger.info(f"✅ [ShotstackGenerator] Vídeo pronto: {video_url}")
            
            # 7. Download info (opcional - para obter file_size)
            video_info = self._get_video_info(video_url)
            
            return {
                'success': True,
                'video_path': video_url,  # URL pública (CDN)
                'duration': video_info.get('duration', 0),
                'file_size': video_info.get('file_size', 0),
                'thumbnail_path': video_info.get('thumbnail', ''),
                'metadata': {
                    'generator': 'shotstack',
                    'render_id': render_id,
                    'slides_count': len(slides),
                    'audio_provider': self.tts.active_provider
                }
            }
            
        except Exception as e:
            logger.error(f"❌ [ShotstackGenerator] Erro: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_script_to_slides(self, script: str) -> List[Dict]:
        """
        Converte script markdown em slides
        
        Formato esperado:
        # Título
        Conteúdo do slide 1
        
        ## Subtítulo
        Conteúdo do slide 2
        """
        slides = []
        lines = script.strip().split('\n')
        
        current_slide = {'title': '', 'content': [], 'level': 0}
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Detectar título (# ou ##)
            if line.startswith('#'):
                # Salvar slide anterior
                if current_slide['title'] or current_slide['content']:
                    slides.append({
                        'title': current_slide['title'],
                        'content': '\n'.join(current_slide['content']),
                        'level': current_slide['level']
                    })
                
                # Novo slide
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_slide = {'title': title, 'content': [], 'level': level}
            else:
                # Adicionar conteúdo ao slide atual
                current_slide['content'].append(line)
        
        # Adicionar último slide
        if current_slide['title'] or current_slide['content']:
            slides.append({
                'title': current_slide['title'],
                'content': '\n'.join(current_slide['content']),
                'level': current_slide['level']
            })
        
        # Limitar número de slides (Shotstack free tier)
        if len(slides) > 10:
            logger.warning(f"   ⚠️ Muitos slides ({len(slides)}), consolidando para 10...")
            slides = self._consolidate_slides(slides, max_slides=10)
        
        return slides
    
    def _consolidate_slides(self, slides: List[Dict], max_slides: int) -> List[Dict]:
        """Consolidar slides para caber no limite"""
        if len(slides) <= max_slides:
            return slides
        
        # Agrupar slides mantendo os principais (level=1)
        main_slides = [s for s in slides if s['level'] == 1]
        sub_slides = [s for s in slides if s['level'] > 1]
        
        # Se ainda tem muitos principais, pegar os primeiros N
        if len(main_slides) > max_slides:
            return main_slides[:max_slides]
        
        # Distribuir sub-slides entre principais
        consolidated = []
        slots_remaining = max_slides - len(main_slides)
        
        for main in main_slides:
            consolidated.append(main)
        
        # Adicionar sub-slides até preencher
        for sub in sub_slides[:slots_remaining]:
            consolidated.append(sub)
        
        return consolidated
    
    def _generate_audio(self, script: str, video_id: int) -> str:
        """Gera áudio TTS do script"""
        audio_path = self.output_dir / f"audio_{video_id}.mp3"
        
        # Extrair apenas texto do script (sem markdown)
        text = self._extract_text_from_script(script)
        
        # Gerar áudio
        success = self.tts.generate(text, str(audio_path))
        
        if not success:
            raise Exception("Falha ao gerar áudio TTS")
        
        return str(audio_path)
    
    def _extract_text_from_script(self, script: str) -> str:
        """Remove markdown e extrai texto puro"""
        text = script
        
        # Remover títulos markdown
        text = text.replace('#', '')
        
        # Remover múltiplas linhas vazias
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return ' '.join(lines)
    
    def _upload_audio(self, audio_path: str) -> str:
        """
        Upload áudio para CDN temporário
        
        Opções:
        1. Usar Shotstack Assets (recomendado)
        2. Usar Cloudflare R2 (se já configurado)
        3. Usar serviço temporário (file.io, tmpfiles.org)
        """
        # Opção 1: Shotstack Assets API
        try:
            upload_url = f"{self.api_url}/assets"
            
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    upload_url,
                    headers={'x-api-key': self.api_key},
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 201:
                data = response.json()
                asset_url = data['data']['attributes']['url']
                logger.info(f"   ✓ Áudio enviado para Shotstack Assets")
                return asset_url
        except Exception as e:
            logger.warning(f"   ⚠️ Falha no upload Shotstack Assets: {e}")
        
        # Fallback: Usar R2 se disponível
        from src.utils.storage import get_storage
        storage = get_storage()
        
        if storage.use_r2:
            try:
                # Upload temporário para R2
                import boto3
                s3_client = storage.s3_client
                bucket = storage.bucket_name
                
                key = f"temp/audio_{os.path.basename(audio_path)}"
                s3_client.upload_file(audio_path, bucket, key)
                
                # Gerar presigned URL (válido por 1 hora)
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': key},
                    ExpiresIn=3600
                )
                
                logger.info(f"   ✓ Áudio enviado para R2 (temp)")
                return url
            except Exception as e:
                logger.warning(f"   ⚠️ Falha no upload R2: {e}")
        
        # Fallback final: Erro (requer CDN configurado)
        raise Exception(
            "Não foi possível fazer upload do áudio. "
            "Configure Shotstack Assets ou Cloudflare R2."
        )
    
    def _build_timeline(
        self, 
        slides: List[Dict], 
        audio_url: str,
        metadata: Dict
    ) -> Dict:
        """
        Monta timeline no formato Shotstack
        
        Docs: https://shotstack.io/docs/guide/
        """
        # Calcular duração de cada slide (baseado no áudio total)
        # Assumir ~10s por slide como padrão
        slide_duration = 10.0
        
        # Track 1: Slides (texto + background)
        video_clips = []
        
        for i, slide in enumerate(slides):
            start_time = i * slide_duration
            
            # Criar clip de título
            title_clip = {
                "asset": {
                    "type": "title",
                    "text": slide['title'],
                    "style": "minimal",  # ou "bold", "blockbuster", etc
                    "color": "#ffffff",
                    "size": "large",
                    "background": "#000000",
                    "position": "center"
                },
                "start": start_time,
                "length": slide_duration,
                "transition": {
                    "in": "fade",
                    "out": "fade"
                }
            }
            
            video_clips.append(title_clip)
            
            # Se tem conteúdo, adicionar subtitle
            if slide['content']:
                content_clip = {
                    "asset": {
                        "type": "title",
                        "text": slide['content'][:200],  # Limitar caracteres
                        "style": "subtitle",
                        "color": "#ffffff",
                        "size": "small",
                        "position": "bottom"
                    },
                    "start": start_time,
                    "length": slide_duration
                }
                video_clips.append(content_clip)
        
        # Track 2: Áudio (narração)
        audio_clip = {
            "asset": {
                "type": "audio",
                "src": audio_url,
                "volume": 1.0
            },
            "start": 0,
            "length": len(slides) * slide_duration
        }
        
        # Montar timeline completo
        timeline = {
            "timeline": {
                "background": "#000000",
                "tracks": [
                    {
                        "clips": video_clips
                    },
                    {
                        "clips": [audio_clip]
                    }
                ]
            },
            "output": {
                "format": "mp4",
                "resolution": "hd",  # 720p (ou "sd", "1080")
                "fps": 25,
                "quality": "medium"  # low, medium, high
            }
        }
        
        return timeline
    
    def _submit_render(self, timeline: Dict) -> str:
        """Envia requisição de render para Shotstack"""
        url = f"{self.api_url}/{self.stage}/render"
        
        response = requests.post(
            url,
            headers=self.headers,
            json=timeline,
            timeout=30
        )
        
        if response.status_code != 201:
            raise Exception(f"Shotstack render falhou: {response.text}")
        
        data = response.json()
        render_id = data['response']['id']
        
        return render_id
    
    def _poll_render_status(self, render_id: str, timeout: int = 300) -> str:
        """
        Aguarda conclusão do render (polling)
        
        Status possíveis:
        - queued: Na fila
        - fetching: Baixando assets
        - rendering: Renderizando
        - saving: Salvando
        - done: Completo ✅
        - failed: Falhou ❌
        """
        url = f"{self.api_url}/{self.stage}/render/{render_id}"
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Falha ao verificar status: {response.text}")
            
            data = response.json()
            status = data['response']['status']
            
            if status != last_status:
                logger.info(f"   📊 Status: {status}")
                last_status = status
            
            if status == 'done':
                video_url = data['response']['url']
                return video_url
            
            if status == 'failed':
                error = data['response'].get('error', 'Unknown error')
                raise Exception(f"Render falhou: {error}")
            
            # Aguardar antes de próximo poll
            time.sleep(5)
        
        raise Exception(f"Timeout ao aguardar render (>{timeout}s)")
    
    def _get_video_info(self, video_url: str) -> Dict:
        """Obtém informações do vídeo renderizado"""
        try:
            # HEAD request para obter file size
            response = requests.head(video_url, timeout=10)
            file_size = int(response.headers.get('Content-Length', 0))
            
            # Shotstack geralmente retorna duração no response, mas não temos acesso aqui
            # Estimativa baseada em slides
            duration = 0  # Será atualizado pelo worker se necessário
            
            return {
                'file_size': file_size,
                'duration': duration,
                'thumbnail': ''  # Shotstack pode gerar thumbnail automaticamente
            }
        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao obter info do vídeo: {e}")
            return {'file_size': 0, 'duration': 0, 'thumbnail': ''}
    
    def estimate_cost(self, script: str, duration_minutes: int) -> float:
        """
        Estima custo de geração
        
        Shotstack pricing:
        - Free tier: 20 renders/mês ($0)
        - Paid: $49/mês = 500 renders = $0.098/render
        """
        # Assumir tier pago
        cost_per_render = 0.10
        return cost_per_render
    
    def supports_language(self, language: str) -> bool:
        """Shotstack suporta qualquer texto (UTF-8)"""
        return True
