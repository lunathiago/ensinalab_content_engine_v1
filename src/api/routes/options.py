"""
Rotas para Options (Opções de Conteúdo)
O motor gera opções que o gestor pode escolher
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.schemas.option import OptionResponse, OptionSelect
from src.services.option_service import OptionService

router = APIRouter()

@router.get("/briefings/{briefing_id}/options", response_model=List[OptionResponse])
async def get_options_for_briefing(
    briefing_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém opções geradas para um briefing
    
    O motor retorna 3-5 propostas diferentes com:
    - Título sugerido
    - Roteiro resumido
    - Duração estimada
    - Tom/abordagem
    - Pontos-chave
    """
    service = OptionService(db)
    options = service.get_options_by_briefing(briefing_id)
    
    if not options:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma opção encontrada para este briefing"
        )
    
    return options

@router.post("/options/{option_id}/select")
async def select_option(
    option_id: int,
    selection: OptionSelect,
    db: Session = Depends(get_db)
):
    """
    Gestor seleciona uma opção
    
    Isso dispara a geração do vídeo via Celery
    """
    service = OptionService(db)
    result = service.select_option(option_id, selection.notes)
    
    if not result:
        raise HTTPException(status_code=404, detail="Opção não encontrada")
    
    return {
        "message": "Opção selecionada! Vídeo será gerado em breve.",
        "video_id": result["video_id"],
        "estimated_time": "2-5 minutos"
    }

@router.post("/briefings/{briefing_id}/regenerate-options")
async def regenerate_options(
    briefing_id: int,
    db: Session = Depends(get_db)
):
    """
    Regenera opções para um briefing (se o gestor não gostou das anteriores)
    """
    service = OptionService(db)
    # Dispara task assíncrona para gerar novas opções
    
    return {
        "message": "Gerando novas opções...",
        "briefing_id": briefing_id
    }
