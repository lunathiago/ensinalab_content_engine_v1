"""
Configuração de Rate Limiting

Proteção contra abuso de API através de limitação de requisições por IP/usuário
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configurar limiter
# key_func determina como agrupar requests (por IP)
limiter = Limiter(key_func=get_remote_address)

# Limites sugeridos por tipo de endpoint:
# - Auth: 5 req/min (evitar brute force)
# - Leitura (GET): 30 req/min
# - Escrita (POST/PUT/DELETE): 10 req/min
# - Download: 3 req/min (arquivos grandes)

# Decoradores prontos para uso
RATE_LIMIT_AUTH = "5/minute"
RATE_LIMIT_READ = "30/minute"
RATE_LIMIT_WRITE = "10/minute"
RATE_LIMIT_DOWNLOAD = "3/minute"
