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
    Gestor seleciona uma opção e inicia geração de vídeo
    
    Flow:
    1. Marca opção como selecionada
    2. Cria registro de Video
    3. Dispara task Celery generate_video
    
    Returns:
        Video criado com status QUEUED
    """
    from src.services.video_service import VideoService
    from src.workers.tasks import generate_video
    
    option_service = OptionService(db)
    video_service = VideoService(db)
    
    # 1. Buscar e validar opção
    option = option_service.get_option(option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    
    # 2. Marcar opção como selecionada
    option_service.select_option(option_id, selection.notes if selection else None)
    
    # 3. Criar registro de vídeo
    video_data = {
        'option_id': option_id,
        'title': option.title,
        'description': option.summary,
        'script': option.script_outline,
        'status': 'QUEUED',
        'generator_type': 'simple'  # Default, pode ser sobrescrito
    }
    
    video = video_service.create_video(video_data)
    
    # 4. Disparar task de geração
    task = generate_video.delay(video.id)
    
    # 5. Salvar task_id
    video.task_id = task.id
    db.commit()
    
    print(f"🚀 Task {task.id} disparada para vídeo {video.id}")
    
    return {
        "message": "Opção selecionada! Vídeo será gerado.",
        "video_id": video.id,
        "task_id": task.id,
        "status": video.status,
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
