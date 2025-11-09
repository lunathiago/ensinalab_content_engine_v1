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

@router.get("/briefings/{briefing_id}", response_model=BriefingResponse)
async def get_briefing(
    briefing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém um briefing específico
    
    **Requer autenticação** e **ownership** do briefing
    """
    service = BriefingService(db)
    briefing = service.get_briefing(briefing_id)
    
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    # Verificar ownership
    if briefing.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: este briefing pertence a outro usuário"
        )
    
    return briefing

@router.delete("/briefings/{briefing_id}", status_code=204)
async def delete_briefing(
    briefing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta um briefing
    
    **Requer autenticação** e **ownership**
    """
    service = BriefingService(db)
    briefing = service.get_briefing(briefing_id)
    
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    # Verificar ownership
    if briefing.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: você não pode deletar este briefing"
        )
    
    service.delete_briefing(briefing_id)
    
    return None
