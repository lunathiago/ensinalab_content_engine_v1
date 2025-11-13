"""
Factory para criar geradores de vídeo
"""
import os
from typing import Dict, Optional
from src.video.base_generator import BaseVideoGenerator
from src.video.simple_generator import SimpleVideoGenerator
from src.video.shotstack_generator import ShotstackGenerator
from src.video.avatar_generator import AvatarVideoGenerator
from src.video.ai_generator import AIVideoGenerator


class VideoGeneratorFactory:
    """
    Factory para criar geradores de vídeo dinamicamente
    
    Suporta 4 tipos:
    - shotstack: Cloud rendering (10-20x mais rápido, recomendado) ⭐
    - simple: TTS + Slides local (fallback, lento)
    - avatar: Apresentador virtual (profissional)
    - ai: IA generativa (experimental, caro)
    """
    
    # Registro de geradores disponíveis
    _generators = {
        'shotstack': ShotstackGenerator,
        'simple': SimpleVideoGenerator,
        'avatar': AvatarVideoGenerator,
        'ai': AIVideoGenerator
    }
    
    @classmethod
    def create(
        cls, 
        generator_type: str = 'auto',
        provider: Optional[str] = None,
        **kwargs
    ) -> BaseVideoGenerator:
        """
        Cria um gerador de vídeo
        
        Args:
            generator_type: Tipo do gerador ('auto', 'shotstack', 'simple', 'avatar', 'ai')
                - 'auto': Escolhe melhor disponível (Shotstack > Simple)
            provider: Provider específico (ex: 'heygen', 'd-id', 'kling', 'runway')
            **kwargs: Argumentos adicionais para o gerador
            
        Returns:
            Instância do gerador
            
        Raises:
            ValueError: Se tipo ou provider não suportado
        """
        
        generator_type = generator_type.lower()
        
        # Auto-detecção: usar Shotstack se configurado, senão Simple
        if generator_type == 'auto':
            if os.getenv("SHOTSTACK_API_KEY"):
                generator_type = 'shotstack'
            else:
                generator_type = 'simple'
        
        if generator_type not in cls._generators:
            raise ValueError(
                f"Tipo '{generator_type}' não suportado. "
                f"Use um de: {', '.join(cls._generators.keys())}"
            )
        
        generator_class = cls._generators[generator_type]
        
        # Instanciar com provider se aplicável
        if generator_type == 'shotstack':
            return generator_class()
        
        elif generator_type == 'simple':
            tts_provider = provider or kwargs.get('tts_provider', 'auto')
            return generator_class(tts_provider=tts_provider)
        
        elif generator_type == 'avatar':
            avatar_provider = provider or kwargs.get('avatar_provider', 'heygen')
            return generator_class(provider=avatar_provider)
        
        elif generator_type == 'ai':
            ai_provider = provider or kwargs.get('ai_provider', 'kling')
            return generator_class(provider=ai_provider)
        
        else:
            return generator_class(**kwargs)
    
    @classmethod
    def get_available_generators(cls) -> Dict:
        """
        Retorna informações sobre geradores disponíveis
        
        Returns:
            Dict com tipos, providers e custos estimados
        """
        return {
            'shotstack': {
                'name': 'Shotstack Cloud (Recomendado)',
                'providers': ['shotstack'],
                'cost_per_min': 0.10,
                'speed': 'muito rápido (1-2 min)',
                'quality': 'alta',
                'best_for': 'produção, escalabilidade',
                'requires': 'SHOTSTACK_API_KEY'
            },
            'simple': {
                'name': 'Simples (TTS + Slides)',
                'providers': ['elevenlabs'],  # 🔧 Apenas ElevenLabs
                'cost_per_min': 0.05,
                'speed': 'lento (5-15 min)',
                'quality': 'básica',
                'best_for': 'desenvolvimento, testes',
                'requires': 'ELEVENLABS_API_KEY'
            },
            'avatar': {
                'name': 'Avatar Virtual',
                'providers': ['heygen', 'd-id'],
                'cost_per_min': 5.0,
                'speed': 'médio (3-5 min)',
                'quality': 'profissional',
                'best_for': 'vídeos educacionais, treinamentos',
                'requires': 'HeyGen ou D-ID API'
            },
            'ai': {
                'name': 'IA Generativa',
                'providers': ['kling', 'runway'],
                'cost_per_min': 50.0,
                'speed': 'lento (10-20 min)',
                'quality': 'cinematográfica',
                'best_for': 'conteúdo premium, marketing',
                'requires': 'Kling ou Runway API'
            }
        }
    
    @classmethod
    def recommend_generator(
        cls,
        budget_usd: float,
        urgency: str = 'normal',
        quality_level: str = 'medium'
    ) -> str:
        """
        Recomenda o melhor gerador baseado em critérios
        
        Args:
            budget_usd: Orçamento disponível por vídeo
            urgency: 'low', 'normal', 'high'
            quality_level: 'basic', 'medium', 'high', 'premium'
            
        Returns:
            Tipo de gerador recomendado
        """
        
        # Sempre preferir Shotstack se disponível (melhor custo-benefício)
        if os.getenv("SHOTSTACK_API_KEY") and budget_usd >= 0.10:
            return 'shotstack'
        
        # Lógica de recomendação para outros geradores
        if budget_usd < 2:
            return 'simple'
        
        if urgency == 'high':
            return 'simple' if budget_usd < 10 else 'avatar'
        
        if quality_level in ['basic', 'medium']:
            return 'simple' if budget_usd < 5 else 'avatar'
        
        if quality_level == 'high':
            return 'avatar'
        
        if quality_level == 'premium' and budget_usd >= 50:
            return 'ai'
        
        # Default: avatar (melhor custo-benefício)
        return 'avatar' if budget_usd >= 5 else 'simple'


# Atalhos para criação rápida
def create_shotstack_generator() -> ShotstackGenerator:
    """Atalho para criar gerador Shotstack (cloud rendering)"""
    return VideoGeneratorFactory.create('shotstack')


def create_simple_generator(tts_provider: str = 'auto') -> SimpleVideoGenerator:
    """Atalho para criar gerador simples (auto-detecta melhor TTS)"""
    return VideoGeneratorFactory.create('simple', provider=tts_provider)


def create_avatar_generator(provider: str = 'heygen') -> AvatarVideoGenerator:
    """Atalho para criar gerador com avatar"""
    return VideoGeneratorFactory.create('avatar', provider=provider)


def create_ai_generator(provider: str = 'kling') -> AIVideoGenerator:
    """Atalho para criar gerador com IA"""
    return VideoGeneratorFactory.create('ai', provider=provider)
