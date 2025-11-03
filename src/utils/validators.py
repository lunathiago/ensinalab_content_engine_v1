"""
Utilitários de validação
"""
import re
from typing import Optional

def validate_grade(grade: str) -> bool:
    """Valida formato de série/ano escolar"""
    patterns = [
        r'^\d+º ano$',  # Ex: "5º ano"
        r'^Ensino (Fundamental|Médio)$',
        r'^EJA$',
    ]
    
    for pattern in patterns:
        if re.match(pattern, grade, re.IGNORECASE):
            return True
    
    return False

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
