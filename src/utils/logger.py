"""
Utilitários de logging
"""
import logging
from datetime import datetime
from typing import Dict, Any
import json

def setup_logger(name: str, level=logging.INFO):
    """Configura logger customizado"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str, level=logging.INFO):
    """
    Obtém ou cria logger (alias para setup_logger para compatibilidade)
    
    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de log (default: INFO)
    
    Returns:
        Logger configurado
    """
    return setup_logger(name, level)


# Logger específico para eventos de segurança
security_logger = setup_logger("security", level=logging.WARNING)


def log_security_event(event_type: str, details: Dict[str, Any]):
    """
    Registra eventos de segurança (tentativas de acesso não autorizado)
    
    Args:
        event_type: Tipo do evento ('unauthorized_access_attempt', 'invalid_token', etc.)
        details: Detalhes do evento (user_id, resource, action, ip, etc.)
    
    Example:
        log_security_event("unauthorized_access_attempt", {
            "user_id": 123,
            "resource": "video",
            "resource_id": 456,
            "action": "download"
        })
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **details
    }
    
    # Log em formato JSON para parsing fácil
    security_logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")
    
    # TODO: Em produção, enviar para sistema de monitoramento
    # - Sentry
    # - CloudWatch
    # - ELK Stack
    # - Banco de dados de audit logs
