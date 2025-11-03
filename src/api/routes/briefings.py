"""
Rotas para Briefings
Gestores enviam briefings simplificados aqui
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.briefing import Briefing
from src.schemas.briefing import BriefingCreate, BriefingResponse
from src.services.briefing_service import BriefingService

router = APIRouter()

@router.post("/briefings", response_model=BriefingResponse, status_code=201)
async def create_briefing(
    briefing_data: BriefingCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo briefing para treinamento de professores
    
    O gestor escolar envia:
    - Título/tema do treinamento
    - Público-alvo (professores iniciantes, coordenadores, etc)
    - Área/disciplina
    - Nível de experiência dos professores
    - Objetivo do treinamento
    - Duração desejada
    - Tom/estilo
    """
    service = BriefingService(db)
    briefing = service.create_briefing(briefing_data)
    
    # Iniciar processamento assíncrono para gerar opções
    # (será implementado com Celery)
    
    return briefing

@router.get("/briefings", response_model=List[BriefingResponse])
async def list_briefings(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lista todos os briefings"""
    service = BriefingService(db)
    return service.list_briefings(skip=skip, limit=limit)

@router.get("/briefings/{briefing_id}", response_model=BriefingResponse)
async def get_briefing(
    briefing_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um briefing específico"""
    service = BriefingService(db)
    briefing = service.get_briefing(briefing_id)
    
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    return briefing

@router.delete("/briefings/{briefing_id}", status_code=204)
async def delete_briefing(
    briefing_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um briefing"""
    service = BriefingService(db)
    deleted = service.delete_briefing(briefing_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    return None
