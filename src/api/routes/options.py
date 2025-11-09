"""
Rotas para Options (Opções de Conteúdo)
O motor gera opções que o gestor pode escolher
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.user import User
from src.models.briefing import Briefing
from src.schemas.option import OptionResponse, OptionSelect
from src.services.option_service import OptionService
from src.services.auth_service import get_current_user
from src.utils.hashid import decode_id
from src.utils.logger import log_security_event

router = APIRouter()

@router.get("/briefings/{briefing_hash}/options", response_model=List[OptionResponse])
async def get_options_for_briefing(
    briefing_hash: str,  # Agora recebe hash
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém opções geradas para um briefing
    
    **Requer autenticação** e **ownership** do briefing
    
    O motor retorna 3-5 propostas diferentes com:
    - Título sugerido
    - Roteiro resumido
    - Duração estimada
    - Tom/abordagem
    - Pontos-chave
    """
    # Decodificar hash para ID
    briefing_id = decode_id(briefing_hash)
    if not briefing_id:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    # Verificar se briefing existe e pertence ao usuário
    briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    
    if not briefing or briefing.user_id != current_user.id:
        log_security_event("unauthorized_access_attempt", {
            "user_id": current_user.id,
            "resource": "options",
            "briefing_id": briefing_id,
            "action": "list"
        })
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    service = OptionService(db)
    options = service.get_options_by_briefing(briefing_id)
    
    if not options:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma opção encontrada para este briefing"
        )
    
    return options

@router.post("/options/{option_hash}/select")
async def select_option(
    option_hash: str,  # Agora recebe hash
    selection: OptionSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gestor seleciona uma opção e inicia geração de vídeo
    
    **Requer autenticação** e **ownership** do briefing
    
    Flow:
    1. Marca opção como selecionada
    2. Cria registro de Video
    3. Dispara task Celery generate_video
    
    Returns:
        Video criado com status QUEUED
    """
    from src.services.video_service import VideoService
    from src.workers.tasks import generate_video
    
    # Decodificar hash para ID
    option_id = decode_id(option_hash)
    if not option_id:
        raise HTTPException(status_code=404, detail="Opção não encontrada")
    
    option_service = OptionService(db)
    video_service = VideoService(db)
    
    # 1. Buscar e validar opção
    option = option_service.get_option(option_id)
    
    # Retornar 404 genérico para evitar info leak
    if not option or option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_select_attempt", {
            "user_id": current_user.id,
            "resource": "option",
            "option_id": option_id,
            "action": "select"
        })
        raise HTTPException(status_code=404, detail="Opção não encontrada")
    
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
    
    # Retornar video_id ofuscado
    from src.utils.hashid import encode_id
    
    return {
        "message": "Opção selecionada! Vídeo será gerado.",
        "video_id": encode_id(video.id),
        "task_id": task.id,
        "status": video.status,
        "estimated_time": "2-5 minutos"
    }

@router.post("/briefings/{briefing_hash}/regenerate-options")
async def regenerate_options(
    briefing_hash: str,  # Agora recebe hash
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Regenera opções para um briefing (se o gestor não gostou das anteriores)
    
    **Requer autenticação** e **ownership** do briefing
    """
    # Decodificar hash para ID
    briefing_id = decode_id(briefing_hash)
    if not briefing_id:
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    # Verificar se briefing existe e pertence ao usuário
    briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    
    if not briefing or briefing.user_id != current_user.id:
        log_security_event("unauthorized_regenerate_attempt", {
            "user_id": current_user.id,
            "resource": "options",
            "briefing_id": briefing_id,
            "action": "regenerate"
        })
        raise HTTPException(status_code=404, detail="Briefing não encontrado")
    
    service = OptionService(db)
    # Dispara task assíncrona para gerar novas opções
    
    from src.utils.hashid import encode_id
    return {
        "message": "Gerando novas opções...",
        "briefing_id": encode_id(briefing_id)
    }
