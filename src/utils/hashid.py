"""
Utilitário para ofuscar IDs numéricos sequenciais

Converte IDs inteiros em hashes curtos e não-sequenciais:
- ID 1 -> 'jR3kM9wX'
- ID 123 -> 'pL8nQ2vZ'

Isso previne enumeração de recursos e IDOR attacks,
mantendo IDs internos como integers no banco de dados.
"""
import os
from hashids import Hashids
from typing import Optional

# Configuração do Hashids
# IMPORTANTE: HASHID_SALT deve ser secreto e único por ambiente
HASHID_SALT = os.getenv("HASHID_SALT", "ensinalab-default-salt-change-in-production")
HASHID_MIN_LENGTH = 8  # Mínimo de 8 caracteres no hash
HASHID_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

# Instância global do Hashids
hashids = Hashids(
    salt=HASHID_SALT,
    min_length=HASHID_MIN_LENGTH,
    alphabet=HASHID_ALPHABET
)


def encode_id(id: int) -> str:
    """
    Converte ID numérico em hash ofuscado
    
    Args:
        id: ID inteiro do banco de dados (ex: 1, 123, 456)
    
    Returns:
        Hash string (ex: 'jR3kM9wX', 'pL8nQ2vZ')
    
    Example:
        >>> encode_id(1)
        'jR3kM9wX'
        >>> encode_id(123)
        'pL8nQ2vZ'
    """
    if id is None:
        return None
    
    if not isinstance(id, int):
        raise ValueError(f"ID deve ser int, recebido: {type(id)}")
    
    return hashids.encode(id)


def decode_id(hash_str: str) -> Optional[int]:
    """
    Converte hash ofuscado de volta para ID numérico
    
    Args:
        hash_str: Hash string (ex: 'jR3kM9wX')
    
    Returns:
        ID inteiro ou None se inválido
    
    Example:
        >>> decode_id('jR3kM9wX')
        1
        >>> decode_id('pL8nQ2vZ')
        123
        >>> decode_id('invalid')
        None
    """
    if not hash_str:
        return None
    
    if not isinstance(hash_str, str):
        return None
    
    try:
        decoded = hashids.decode(hash_str)
        return decoded[0] if decoded else None
    except Exception:
        # Hash inválido ou corrompido
        return None


def encode_ids(ids: list[int]) -> list[str]:
    """
    Converte lista de IDs em lista de hashes
    
    Args:
        ids: Lista de IDs inteiros
    
    Returns:
        Lista de hashes
    
    Example:
        >>> encode_ids([1, 2, 3])
        ['jR3kM9wX', 'xK2pL9vN', 'mN5qR8wZ']
    """
    return [encode_id(id) for id in ids if id is not None]


def decode_ids(hashes: list[str]) -> list[int]:
    """
    Converte lista de hashes em lista de IDs
    
    Args:
        hashes: Lista de hashes
    
    Returns:
        Lista de IDs (ignora hashes inválidos)
    
    Example:
        >>> decode_ids(['jR3kM9wX', 'xK2pL9vN'])
        [1, 2]
    """
    return [id for id in (decode_id(h) for h in hashes) if id is not None]


# Validação na inicialização
if HASHID_SALT == "ensinalab-default-salt-change-in-production":
    import warnings
    warnings.warn(
        "⚠️  SECURITY WARNING: Usando HASHID_SALT padrão! "
        "Configure HASHID_SALT no .env para produção.",
        stacklevel=2
    )
