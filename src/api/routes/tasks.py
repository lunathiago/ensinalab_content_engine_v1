"""
Rotas para Tasks e Processos
Monitoramento de tarefas assíncronas em andamento
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.config.database import get_db
from src.models.user import User
from src.models.briefing import Briefing
from src.models.video import Video
from src.models.option import Option
from src.services.auth_service import get_current_user
from src.utils.hashid import encode_id
from src.workers.celery_config import celery_app
from celery.result import AsyncResult

router = APIRouter()

@router.get("/tasks/active")
async def list_active_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os processos em andamento do usuário
    
    **Requer autenticação** - retorna apenas tasks do usuário logado
    
    Retorna:
    - Briefings sendo processados (gerando opções)
    - Vídeos sendo gerados
    - Status da task no Celery
    - Tempo decorrido
    - Progresso estimado
    """
    active_tasks = []
    
    # 1. Buscar briefings em processamento
    briefings = db.query(Briefing).filter(
        Briefing.user_id == current_user.id,
        Briefing.status.in_(["processing", "generating_options"])
    ).all()
    
    for briefing in briefings:
        task_info = {
            "type": "briefing",
            "resource_type": "briefing",
            "resource_id": encode_id(briefing.id),
            "title": briefing.title,
            "status": briefing.status,
            "created_at": briefing.created_at.isoformat() if briefing.created_at else None,
            "elapsed_time": _calculate_elapsed_time(briefing.created_at),
            "task_id": briefing.task_id,
            "celery_status": None,
            "can_cancel": True
        }
        
        # Verificar status real no Celery
        if briefing.task_id:
            celery_status = _get_celery_task_status(briefing.task_id)
            task_info["celery_status"] = celery_status
            
        active_tasks.append(task_info)
    
    # 2. Buscar vídeos em processamento
    videos = db.query(Video).join(Option).join(Briefing).filter(
        Briefing.user_id == current_user.id,
        Video.status.in_(["queued", "processing", "pending_approval"])
    ).all()
    
    for video in videos:
        task_info = {
            "type": "video",
            "resource_type": "video",
            "resource_id": encode_id(video.id),
            "title": video.title,
            "status": video.status,
            "progress": video.progress,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "elapsed_time": _calculate_elapsed_time(video.created_at),
            "task_id": video.task_id,
            "celery_status": None,
            "generator_type": video.generator_type,
            "can_cancel": video.status in ["queued", "processing", "pending_approval"]
        }
        
        # Verificar status real no Celery
        if video.task_id:
            celery_status = _get_celery_task_status(video.task_id)
            task_info["celery_status"] = celery_status
            
        active_tasks.append(task_info)
    
    # 3. Ordenar por mais recente
    active_tasks.sort(key=lambda x: x["created_at"] or "", reverse=True)
    
    return {
        "total": len(active_tasks),
        "tasks": active_tasks,
        "summary": {
            "briefings": len([t for t in active_tasks if t["type"] == "briefing"]),
            "videos": len([t for t in active_tasks if t["type"] == "video"])
        }
    }


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtém status detalhado de uma task específica do Celery
    
    **Requer autenticação**
    
    Retorna informações diretas do Celery sobre a task:
    - Estado atual (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
    - Resultado ou erro
    - Informações de retry
    - Worker que está processando
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        task_info = {
            "task_id": task_id,
            "state": result.state,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }
        
        # Adicionar info específica por estado
        if result.state == "PENDING":
            task_info["info"] = "Task não encontrada ou ainda não iniciada"
        elif result.state == "STARTED":
            task_info["info"] = result.info or {}
        elif result.state == "SUCCESS":
            task_info["result"] = result.result
        elif result.state == "FAILURE":
            task_info["error"] = str(result.info)
            task_info["traceback"] = result.traceback
        elif result.state == "RETRY":
            task_info["info"] = result.info
            task_info["retries"] = getattr(result.info, 'retries', 0) if result.info else 0
        elif result.state == "REVOKED":
            task_info["info"] = "Task foi cancelada"
        
        return task_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar task: {str(e)}"
        )


@router.post("/tasks/cancel-all")
async def cancel_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancela TODAS as tasks em andamento do usuário
    
    **Requer autenticação** - cancela apenas tasks do usuário logado
    
    ⚠️ Use com cuidado! Isso irá cancelar:
    - Todos os briefings sendo processados
    - Todos os vídeos sendo gerados
    
    Útil para "reiniciar tudo" em caso de problemas graves.
    """
    from src.utils.logger import log_security_event
    
    cancelled = {
        "briefings": [],
        "videos": [],
        "total": 0
    }
    
    # 1. Cancelar todos os briefings em processamento
    briefings = db.query(Briefing).filter(
        Briefing.user_id == current_user.id,
        Briefing.status.in_(["processing", "generating_options"])
    ).all()
    
    for briefing in briefings:
        if briefing.task_id:
            try:
                celery_app.control.revoke(
                    briefing.task_id,
                    terminate=True,
                    signal='SIGKILL'
                )
                cancelled["briefings"].append(encode_id(briefing.id))
            except Exception as e:
                print(f"⚠️ Erro ao revogar task {briefing.task_id}: {e}")
        
        briefing.status = "cancelled"
    
    # 2. Cancelar todos os vídeos em processamento
    videos = db.query(Video).join(Option).join(Briefing).filter(
        Briefing.user_id == current_user.id,
        Video.status.in_(["queued", "processing", "pending_approval"])
    ).all()
    
    for video in videos:
        if video.task_id:
            try:
                celery_app.control.revoke(
                    video.task_id,
                    terminate=True,
                    signal='SIGKILL'
                )
                cancelled["videos"].append(encode_id(video.id))
            except Exception as e:
                print(f"⚠️ Erro ao revogar task {video.task_id}: {e}")
        
        video.status = "cancelled"
        video.error_message = "Cancelado pelo usuário (cancel-all)"
        video.progress = 0
    
    # 3. Commit no banco
    db.commit()
    
    cancelled["total"] = len(cancelled["briefings"]) + len(cancelled["videos"])
    
    # 4. Log de segurança
    log_security_event("cancel_all_tasks", {
        "user_id": current_user.id,
        "briefings_cancelled": len(cancelled["briefings"]),
        "videos_cancelled": len(cancelled["videos"])
    })
    
    return {
        "message": f"{cancelled['total']} tasks canceladas com sucesso",
        "cancelled": cancelled
    }


def _calculate_elapsed_time(created_at: datetime) -> Dict[str, Any]:
    """Calcula tempo decorrido desde a criação"""
    if not created_at:
        return {"seconds": 0, "formatted": "0s"}
    
    # Garantir timezone-aware
    if created_at.tzinfo is None:
        from datetime import timezone
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    elapsed = datetime.now(created_at.tzinfo) - created_at
    seconds = int(elapsed.total_seconds())
    
    # Formatar de forma legível
    if seconds < 60:
        formatted = f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        formatted = f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        formatted = f"{hours}h {minutes}m"
    
    return {
        "seconds": seconds,
        "formatted": formatted,
        "is_stuck": seconds > 300  # Mais de 5 minutos (task_time_limit)
    }


def _get_celery_task_status(task_id: str) -> Dict[str, Any]:
    """Obtém status da task no Celery"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            "state": result.state,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None
        }
    except Exception as e:
        return {
            "state": "UNKNOWN",
            "error": str(e)
        }
