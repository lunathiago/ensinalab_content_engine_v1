"""
Utilitários de logging
"""
import logging
from datetime import datetime

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
