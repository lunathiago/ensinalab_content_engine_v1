"""
Rotas para Briefings
Gestores enviam briefings simplificados aqui
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.briefing import Briefing
from src.models.user import User
from src.schemas.briefing import BriefingCreate, BriefingResponse
from src.services.briefing_service import BriefingService
from src.services.auth_service import get_current_user
from src.utils.hashid import decode_id
from src.utils.logger import log_security_event

router = APIRouter()

@router.post("/briefings", response_model=BriefingResponse, status_code=201)
async def create_briefing(
    briefing_data: BriefingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo briefing para treinamento de professores
    
    **Requer autenticação** (Header: `Authorization: Bearer {token}`)
    
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
    
    # Adicionar user_id ao briefing
    briefing_dict = briefing_data.model_dump()
    briefing_dict['user_id'] = current_user.id
    
    briefing = service.create_briefing(briefing_dict)
    
    # Iniciar processamento assíncrono para gerar opções
    # (será implementado com Celery)
    
    print(f"✅ Briefing {briefing.id} criado por {current_user.email}")
    
    return briefing

@router.get("/briefings", response_model=List[BriefingResponse])
async def list_briefings(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista briefings do usuário autenticado
    
    **Requer autenticação**
    """
    # Filtrar apenas briefings do usuário
    briefings = db.query(Briefing).filter(
        Briefing.user_id == current_user.id
    ).order_by(
        Briefing.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return briefings

@router.get("/briefings/{briefing_hash}", response_model=BriefingResponse)
async def get_briefing(
    briefing_hash: str,  # Agora recebe hash em vez de ID
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém um briefing específico
    
    **Requer autenticação** e **ownership** do briefing
    """
    # Decodificar hash para ID
    briefing_id = decode_id(briefing_hash)
    if not briefing_id:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    service = BriefingService(db)
    briefing = service.get_briefing(briefing_id)
    
    # Retornar 404 genérico para evitar info leak (não revela se existe)
    if not briefing or briefing.user_id != current_user.id:
        log_security_event("unauthorized_access_attempt", {
            "user_id": current_user.id,
            "resource": "briefing",
            "resource_id": briefing_id,
            "action": "get"
        })
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    return briefing

@router.delete("/briefings/{briefing_hash}", status_code=204)
async def delete_briefing(
    briefing_hash: str,  # Agora recebe hash em vez de ID
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta um briefing
    
    **Requer autenticação** e **ownership**
    """
    # Decodificar hash para ID
    briefing_id = decode_id(briefing_hash)
    if not briefing_id:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    service = BriefingService(db)
    briefing = service.get_briefing(briefing_id)
    
    # Retornar 404 genérico para evitar info leak
    if not briefing or briefing.user_id != current_user.id:
        log_security_event("unauthorized_delete_attempt", {
            "user_id": current_user.id,
            "resource": "briefing",
            "resource_id": briefing_id,
            "action": "delete"
        })
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    service.delete_briefing(briefing_id)
    
    return None
