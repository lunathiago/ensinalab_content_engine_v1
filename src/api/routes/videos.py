"""
Rotas para Videos
Gestão de vídeos gerados
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.user import User
from src.schemas.video import VideoResponse
from src.services.video_service import VideoService
from src.services.auth_service import get_current_user
from src.utils.hashid import decode_id
from src.utils.logger import log_security_event

router = APIRouter()

@router.get("/videos", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os vídeos gerados pelo usuário atual
    
    **Requer autenticação** - retorna apenas vídeos do usuário logado
    """
    service = VideoService(db)
    # Filtrar vídeos por user_id através do relacionamento option -> briefing -> user
    from src.models.video import Video
    from src.models.option import Option
    from src.models.briefing import Briefing
    
    videos = db.query(Video).join(Option).join(Briefing).filter(
        Briefing.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return videos

@router.get("/videos/{video_hash}", response_model=VideoResponse)
async def get_video(
    video_hash: str,  # Hash ofuscado
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes de um vídeo específico
    
    **Requer autenticação** e **ownership** do vídeo
    """
    video_id = decode_id(video_hash)
    if not video_id:
        raise HTTPException(404, "Vídeo não encontrado")
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership através de option -> briefing -> user
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "access"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    return video

@router.get("/videos/{video_hash}/download")
async def download_video(
    video_hash: str,  # Hash ofuscado
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Baixa o arquivo de vídeo
    
    **Requer autenticação** e **ownership** do vídeo
    
    Se vídeo está em storage externo (R2/S3), redireciona para URL.
    Se local (desenvolvimento), serve arquivo diretamente.
    """
    import os
    from fastapi.responses import RedirectResponse
    
    video_id = decode_id(video_hash)
    if not video_id:
        raise HTTPException(404, "Vídeo não encontrado")
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "download"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    if video.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo ainda não está pronto. Status: {video.status}"
        )
    
    # Verificar se é URL externa (R2/S3) ou path local
    if video.file_path.startswith(("http://", "https://")):
        # Storage externo - redirecionar
        print(f"🔗 Redirecionando para storage: {video.file_path[:60]}...")
        return RedirectResponse(
            url=video.file_path,
            status_code=307  # Temporary Redirect (mantém método GET)
        )
    
    # Path local - servir arquivo (desenvolvimento)
    if not os.path.exists(video.file_path):
        raise HTTPException(
            status_code=503,
            detail={
                "error": "video_file_not_accessible",
                "message": "Arquivo de vídeo não está acessível no momento.",
                "reason": "Storage não configurado ou arquivo não encontrado.",
                "solution": "Configure R2_ACCESS_KEY_ID para usar Cloudflare R2.",
                "video_path": video.file_path,
                "video_id": video_id
            }
        )
    
    return FileResponse(
        video.file_path,
        media_type="video/mp4",
        filename=f"{video.title}.mp4"
    )

@router.get("/videos/{video_hash}/status")
async def get_video_status(
    video_hash: str,  # Hash ofuscado
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verifica o status de geração do vídeo
    
    **Requer autenticação** e **ownership** do vídeo
    
    Status possíveis:
    - queued: Na fila
    - processing: Sendo gerado
    - pending_approval: Aguardando aprovação humana
    - completed: Pronto
    - failed: Erro na geração
    """
    video_id = decode_id(video_hash)
    if not video_id:
        raise HTTPException(404, "Vídeo não encontrado")
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "access"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    return {
        "video_id": video.id,
        "status": video.status,
        "progress": video.progress,
        "message": video.error_message if video.status == "failed" else None,
        "awaiting_approval": video.status == "pending_approval"
    }


@router.post("/videos/{video_hash}/approve")
async def approve_video(
    video_hash: str,  # Hash ofuscado
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aprova um vídeo que está aguardando revisão humana
    
    **Requer autenticação** e **ownership** do vídeo
    
    Retoma o workflow LangGraph para finalizar a geração
    """
    from src.workers.tasks import resume_video_generation
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "access"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    if video.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo não está aguardando aprovação. Status: {video.status}"
        )
    
    # Disparar task para retomar geração
    task = resume_video_generation.delay(video_id=video_id, approved=True)
    
    return {
        "video_id": video_id,
        "message": "Vídeo aprovado. Retomando geração...",
        "task_id": task.id
    }


@router.post("/videos/{video_hash}/reject")
async def reject_video(
    video_hash: str,  # Hash ofuscado
    feedback: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rejeita um vídeo e solicita revisão
    
    **Requer autenticação** e **ownership** do vídeo
    
    Args:
        video_id: ID do vídeo
        feedback: Feedback opcional para melhorias
    
    O workflow voltará para o estágio de enhancement com o feedback
    """
    from src.workers.tasks import resume_video_generation
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "access"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    if video.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo não está aguardando aprovação. Status: {video.status}"
        )
    
    # Disparar task para retomar geração com feedback
    task = resume_video_generation.delay(
        video_id=video_id, 
        approved=False,
        feedback=feedback
    )
    
    return {
        "video_id": video_id,
        "message": "Vídeo rejeitado. Aplicando feedback e regenerando...",
        "task_id": task.id,
        "feedback": feedback
    }


@router.post("/videos/{video_hash}/cancel")
async def cancel_video(
    video_hash: str,  # Hash ofuscado
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancela a geração de um vídeo em andamento
    
    **Requer autenticação** e **ownership** do vídeo
    
    Útil para interromper vídeos que estão demorando demais ou travados.
    Revoga a task do Celery e atualiza o status para "cancelled".
    """
    from src.workers.celery_config import celery_app
    from celery.result import AsyncResult
    
    video_id = decode_id(video_hash)
    if not video_id:
        raise HTTPException(404, "Vídeo não encontrado")
    
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Verificar ownership
    if video.option.briefing.user_id != current_user.id:
        log_security_event("unauthorized_video_access", {
            "user_id": current_user.id,
            "video_id": video_id,
            "action": "cancel"
        })
        raise HTTPException(404, "Vídeo não encontrado")
    
    # Apenas vídeos em processamento podem ser cancelados
    if video.status not in ["queued", "processing", "pending_approval"]:
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo não pode ser cancelado. Status atual: {video.status}"
        )
    
    # Revogar task do Celery se tiver task_id
    revoked = False
    if video.task_id:
        try:
            celery_app.control.revoke(
                video.task_id,
                terminate=True,  # Força término imediato
                signal='SIGKILL'  # Mata o processo
            )
            revoked = True
            print(f"✓ Task {video.task_id} revogada")
        except Exception as e:
            print(f"⚠️ Erro ao revogar task: {e}")
    
    # Atualizar status no banco
    video.status = "cancelled"
    video.error_message = "Cancelado pelo usuário"
    video.progress = 0
    db.commit()
    
    log_security_event("video_cancelled", {
        "user_id": current_user.id,
        "video_id": video_id,
        "task_id": video.task_id,
        "revoked": revoked
    })
    
    return {
        "video_id": video_id,
        "message": "Vídeo cancelado com sucesso",
        "task_revoked": revoked,
        "status": "cancelled"
    }

