"""
Rotas para Briefings
Gestores enviam briefings simplificados aqui
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.briefing import Briefing, BriefingStatus
from src.models.user import User
from src.schemas.briefing import BriefingCreate, BriefingResponse
from src.services.briefing_service import BriefingService
from src.services.auth_service import get_current_user
from src.utils.hashid import decode_id
from src.utils.logger import log_security_event
from src.ml.content_guardrails import ContentGuardrails

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
    
    **Guardrails**: Apenas conteúdo educacional é aceito. Briefings sobre
    política, religião ou temas não-educacionais serão rejeitados.
    
    O gestor escolar envia:
    - Título/tema do treinamento
    - Público-alvo (professores iniciantes, coordenadores, etc)
    - Área/disciplina
    - Nível de experiência dos professores
    - Objetivo do treinamento
    - Duração desejada
    - Tom/estilo
    """
    
    # 🛡️ GUARDRAIL: Validar conteúdo educacional
    guardrails = ContentGuardrails()
    is_valid, reason, confidence = guardrails.validate_briefing(
        title=briefing_data.title,
        description=briefing_data.description,
        subject_area=briefing_data.subject_area,
        target_audience=briefing_data.target_audience
    )
    
    if not is_valid:
        # Log tentativa rejeitada
        log_security_event(
            event_type="content_guardrail_rejection",
            user_id=current_user.id,
            details={
                "reason": reason,
                "confidence": confidence,
                "title": briefing_data.title[:100]
            }
        )
        
        # Retornar erro 422 (Unprocessable Entity)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Briefing rejeitado: conteúdo não-educacional",
                "reason": reason,
                "confidence": confidence,
                "hint": "A plataforma aceita apenas conteúdo relacionado a educação, "
                        "treinamento de professores e desenvolvimento pedagógico."
            }
        )
    
    print(f"✅ Guardrail aprovado: {reason} (confiança: {confidence:.2f})")
    
    service = BriefingService(db)
    
    # Adicionar user_id ao briefing data
    briefing_dict = briefing_data.model_dump()
    briefing_dict['user_id'] = current_user.id
    
    # Criar briefing passando dicionário
    briefing = Briefing(
        user_id=current_user.id,
        title=briefing_data.title,
        description=briefing_data.description,
        target_audience=briefing_data.target_audience,
        subject_area=briefing_data.subject_area,
        teacher_experience_level=briefing_data.teacher_experience_level,
        training_goal=briefing_data.training_goal,
        duration_minutes=briefing_data.duration_minutes,
        tone=briefing_data.tone,
        status=BriefingStatus.PENDING
    )
    
    db.add(briefing)
    db.commit()
    db.refresh(briefing)
    
    # Disparar task Celery para gerar opções
    from src.workers.tasks import generate_options
    generate_options.delay(briefing.id)
    
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
