"""
Configuração de geradores de vídeo
Define qual gerador usar baseado em ambiente/custo/qualidade
"""
import os
from typing import Dict


class VideoGeneratorConfig:
    """Configuração centralizada dos geradores"""
    
    # Gerador padrão (pode ser sobrescrito por env var)
    DEFAULT_GENERATOR = os.getenv("VIDEO_GENERATOR_TYPE", "simple")
    
    # Provider padrão por gerador
    DEFAULT_PROVIDERS = {
        'simple': os.getenv("TTS_PROVIDER", "google"),
        'avatar': os.getenv("AVATAR_PROVIDER", "heygen"),
        'ai': os.getenv("AI_VIDEO_PROVIDER", "kling")
    }
    
    # Configurações por ambiente
    ENVIRONMENTS = {
        'development': {
            'generator': 'simple',
            'provider': 'google',
            'description': 'Desenvolvimento local - barato e rápido'
        },
        'staging': {
            'generator': 'simple',
            'provider': 'google',
            'description': 'Staging - testes'
        },
        'production': {
            'generator': 'avatar',
            'provider': 'heygen',
            'description': 'Produção - qualidade profissional'
        },
        'premium': {
            'generator': 'ai',
            'provider': 'kling',
            'description': 'Premium - máxima qualidade'
        }
    }
    
    @classmethod
    def get_generator_config(cls, environment: str = None) -> Dict:
        """
        Retorna configuração do gerador baseado no ambiente
        
        Args:
            environment: Ambiente ('development', 'staging', 'production', 'premium')
            
        Returns:
            Dict com generator_type e provider
        """
        
        # Detectar ambiente se não especificado
        if not environment:
            environment = os.getenv("APP_ENV", "development")
        
        config = cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS['development'])
        
        return {
            'generator_type': config['generator'],
            'provider': config['provider'],
            'environment': environment,
            'description': config['description']
        }
    
    @classmethod
    def get_generator_for_briefing(cls, briefing_data: Dict) -> Dict:
        """
        Escolhe gerador baseado nas características do briefing
        
        Args:
            briefing_data: Dados do briefing
            
        Returns:
            Config do gerador recomendado
        """
        
        duration = briefing_data.get('duration_minutes', 10)
        tone = briefing_data.get('tone', 'profissional')
        subject = briefing_data.get('subject_area', '')
        
        # Lógica de recomendação
        if duration <= 5:
            # Vídeos curtos: simple é suficiente
            return {'generator_type': 'simple', 'provider': 'google'}
        
        if tone in ['profissional', 'técnico']:
            # Tom profissional: avatar recomendado
            return {'generator_type': 'avatar', 'provider': 'heygen'}
        
        if 'premium' in subject.lower() or duration >= 20:
            # Conteúdo premium ou longo: considerar AI
            return {'generator_type': 'ai', 'provider': 'kling'}
        
        # Default: avatar (melhor custo-benefício)
        return {'generator_type': 'avatar', 'provider': 'd-id'}
    
    @classmethod
    def estimate_cost(cls, generator_type: str, duration_minutes: int) -> float:
        """
        Estima custo de geração
        
        Args:
            generator_type: Tipo do gerador
            duration_minutes: Duração em minutos
            
        Returns:
            Custo estimado em USD
        """
        
        costs = {
            'simple': 0.05 * duration_minutes,
            'avatar': 5.0 * duration_minutes,
            'ai': 50.0 * duration_minutes
        }
        
        return costs.get(generator_type, 1.0)


# Singleton da config
video_config = VideoGeneratorConfig()
