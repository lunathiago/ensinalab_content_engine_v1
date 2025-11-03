"""
Utilitários de validação
"""
import re
from typing import Optional

def validate_teacher_audience(audience: str) -> bool:
    """Valida público-alvo de professores"""
    valid_audiences = [
        'professores iniciantes',
        'professores experientes',
        'coordenadores',
        'gestores',
        'todos os professores',
        'professores do ensino fundamental',
        'professores do ensino médio',
    ]
    
    return any(valid in audience.lower() for valid in valid_audiences)

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nome de arquivo"""
    # Remove caracteres especiais
    filename = re.sub(r'[^\w\s-]', '', filename)
    # Substitui espaços por underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.lower()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto mantendo palavras inteiras"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + suffix
