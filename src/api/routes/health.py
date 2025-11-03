"""
Rotas de health check
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "EnsinaLab Content Engine"
    }

@router.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "EnsinaLab Content Engine API",
        "version": "0.1.0",
        "docs": "/docs"
    }
