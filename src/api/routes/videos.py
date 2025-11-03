"""
Rotas para Videos
Gestão de vídeos gerados
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.schemas.video import VideoResponse
from src.services.video_service import VideoService

router = APIRouter()

@router.get("/videos", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lista todos os vídeos gerados"""
    service = VideoService(db)
    return service.list_videos(skip=skip, limit=limit)

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um vídeo específico"""
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    return video

@router.get("/videos/{video_id}/download")
async def download_video(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Baixa o arquivo de vídeo
    """
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    if video.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo ainda não está pronto. Status: {video.status}"
        )
    
    return FileResponse(
        video.file_path,
        media_type="video/mp4",
        filename=f"{video.title}.mp4"
    )

@router.get("/videos/{video_id}/status")
async def get_video_status(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Verifica o status de geração do vídeo
    
    Status possíveis:
    - queued: Na fila
    - processing: Sendo gerado
    - completed: Pronto
    - failed: Erro na geração
    """
    service = VideoService(db)
    video = service.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    return {
        "video_id": video.id,
        "status": video.status,
        "progress": video.progress,
        "message": video.error_message if video.status == "failed" else None
    }
