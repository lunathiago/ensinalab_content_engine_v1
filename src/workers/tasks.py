"""
Tasks assíncronas do Celery com integração LangGraph
"""
from celery import Task
from src.workers.celery_config import celery_app
from src.config.database import SessionLocal
from src.services.briefing_service import BriefingService
from src.services.option_service import OptionService
from src.services.video_service import VideoService
from src.models.briefing import Briefing, BriefingStatus
from src.models.video import VideoStatus
from src.ml.llm_service import LLMService
from src.ml.filters import ContentFilter
from src.video.tts import TTSService
from src.video.generator import VideoGenerator

# LangGraph Workflows
from src.workflows.briefing_workflow import BriefingAnalysisWorkflow
from src.workflows.video_workflow import VideoGenerationWorkflow
from src.workflows.refinement_workflow import ContentRefinementWorkflow

class DatabaseTask(Task):
    """Base task com sessão de banco de dados"""
    
    def __call__(self, *args, **kwargs):
        with SessionLocal() as db:
            self.db = db
            return super().__call__(*args, **kwargs)

@celery_app.task(base=DatabaseTask, bind=True)
def generate_options(self, briefing_id: int):
    """
    Task para gerar opções de conteúdo usando Multi-Agent Workflow (LangGraph)
    
    Pipeline: Analyzer → Generator → Filter → Ranker
    """
    try:
        print(f"🔄 Gerando opções com LangGraph para briefing {briefing_id}...")
        
        # Obter briefing
        briefing_service = BriefingService(self.db)
        briefing = briefing_service.get_briefing(briefing_id)
        
        if not briefing:
            print(f"❌ Briefing {briefing_id} não encontrado")
            return
        
        # Atualizar status
        briefing_service.update_status(briefing_id, BriefingStatus.PROCESSING)
        
        # Preparar input para workflow
        briefing_data = {
            'title': briefing.title,
            'description': briefing.description,
            'target_audience': briefing.target_audience,
            'subject_area': briefing.subject_area,
            'teacher_experience_level': briefing.teacher_experience_level,
            'training_goal': briefing.training_goal,
            'duration_minutes': briefing.duration_minutes,
            'tone': briefing.tone
        }
        
        # 🤖 Executar Multi-Agent Workflow
        workflow = BriefingAnalysisWorkflow()
        result = workflow.run(briefing_id, briefing_data)
        
        if not result['success']:
            raise Exception("Multi-agent workflow falhou")
        
        ranked_options = result['options']
        
        # Salvar opções no banco
        option_service = OptionService(self.db)
        for i, option_data in enumerate(ranked_options):
            # Adicionar metadata do workflow
            option_data['briefing_id'] = briefing_id
            option_data['rank'] = i + 1
            option_data['quality_score'] = option_data.get('score', 0.0)
            
            option_service.create_option(option_data)
        
        # Atualizar status
        briefing_service.update_status(briefing_id, BriefingStatus.OPTIONS_READY)
        
        print(f"✅ {len(ranked_options)} opções geradas (multi-agent) para briefing {briefing_id}")
        
        return {
            "briefing_id": briefing_id,
            "options_count": len(ranked_options),
            "metadata": result['metadata']
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar opções: {e}")
        briefing_service.update_status(briefing_id, BriefingStatus.FAILED)
        raise

@celery_app.task(base=DatabaseTask, bind=True)
def generate_video(self, video_id: int):
    """
    Task para gerar vídeo usando State Machine Workflow (LangGraph)
    
    Pipeline: Analyze → Enhance → Generate Audio → Generate Video → Review → Await Approval → Finalize
    Suporta checkpointing e human-in-the-loop
    """
    try:
        print(f"🎬 Gerando vídeo {video_id} com LangGraph State Machine...")
        
        # Obter vídeo e opção
        video_service = VideoService(self.db)
        video = video_service.get_video(video_id)
        
        if not video:
            print(f"❌ Vídeo {video_id} não encontrado")
            return
        
        # Atualizar status
        video_service.update_status(video_id, VideoStatus.PROCESSING, progress=0.1)
        
        option = video.option
        briefing = option.briefing
        
        # Preparar input para workflow
        input_data = {
            "script_outline": option.script_outline,
            "briefing": {
                'target_audience': briefing.target_audience,
                'subject_area': briefing.subject_area,
                'duration_minutes': briefing.duration_minutes,
                'tone': briefing.tone,
                'title': option.title
            },
            "video_id": video_id
        }
        
        # 🎯 Executar Video Generation State Machine
        workflow = VideoGenerationWorkflow()
        result = workflow.run(input_data, video_id=video_id)
        
        # Verificar se precisa de aprovação humana
        if result['status'] == 'awaiting_approval':
            print(f"⏸️  Vídeo {video_id} aguardando aprovação humana")
            video_service.update_status(
                video_id, 
                VideoStatus.PENDING_APPROVAL,
                progress=0.8
            )
            
            # Salvar checkpoint_id para poder retomar depois
            video.metadata = video.metadata or {}
            video.metadata['checkpoint_id'] = result['checkpoint_id']
            self.db.commit()
            
            return {
                "video_id": video_id,
                "status": "awaiting_approval",
                "checkpoint_id": result['checkpoint_id'],
                "preview_path": result.get('preview_path')
            }
        
        # Processar resultado final
        if result['success']:
            video_service.update_status(video_id, VideoStatus.PROCESSING, progress=0.9)
            
            # Finalizar
            video_service.complete_video(
                video_id=video_id,
                file_path=result['file_path'],
                file_size=result.get('file_size', 0),
                duration=result.get('duration', 0),
                thumbnail_path=result.get('thumbnail_path')
            )
            
            print(f"✅ Vídeo {video_id} gerado com sucesso (state machine)!")
            
            return {
                "video_id": video_id,
                "file_path": result['file_path'],
                "duration": result['duration'],
                "metadata": result['metadata']
            }
        else:
            raise Exception(f"Workflow falhou: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar vídeo: {e}")
        video_service.update_status(
            video_id, 
            VideoStatus.FAILED, 
            error_message=str(e)
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def resume_video_generation(self, video_id: int, approved: bool, feedback: str = None):
    """
    Task para retomar geração de vídeo após aprovação/rejeição humana
    
    Args:
        video_id: ID do vídeo
        approved: True se aprovado, False se rejeitado
        feedback: Feedback opcional para revisão
    """
    try:
        print(f"▶️  Retomando geração do vídeo {video_id} (aprovado={approved})...")
        
        # Obter vídeo
        video_service = VideoService(self.db)
        video = video_service.get_video(video_id)
        
        if not video:
            print(f"❌ Vídeo {video_id} não encontrado")
            return
        
        # Obter checkpoint_id
        checkpoint_id = video.metadata.get('checkpoint_id') if video.metadata else None
        
        if not checkpoint_id:
            raise Exception("Checkpoint não encontrado para retomar workflow")
        
        # Retomar workflow
        workflow = VideoGenerationWorkflow()
        result = workflow.resume(
            checkpoint_id=checkpoint_id,
            approved=approved,
            feedback=feedback
        )
        
        # Processar resultado
        if result['success']:
            video_service.complete_video(
                video_id=video_id,
                file_path=result['file_path'],
                file_size=result.get('file_size', 0),
                duration=result.get('duration', 0),
                thumbnail_path=result.get('thumbnail_path')
            )
            
            print(f"✅ Vídeo {video_id} finalizado após aprovação!")
            
            return {
                "video_id": video_id,
                "file_path": result['file_path']
            }
        else:
            raise Exception(f"Retomada falhou: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Erro ao retomar vídeo: {e}")
        video_service.update_status(
            video_id, 
            VideoStatus.FAILED, 
            error_message=str(e)
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def refine_content(self, content: str, content_type: str = "script", target_quality: float = 0.85):
    """
    Task para refinar conteúdo iterativamente usando Refinement Workflow
    
    Args:
        content: Conteúdo inicial
        content_type: Tipo de conteúdo ('script', 'outline', 'summary')
        target_quality: Qualidade alvo (0-1)
    
    Returns:
        Conteúdo refinado e metadata
    """
    try:
        print(f"🔧 Refinando {content_type}...")
        
        # 🔄 Executar Refinement Cycle Workflow
        workflow = ContentRefinementWorkflow()
        result = workflow.run(
            content=content,
            content_type=content_type,
            target_quality=target_quality,
            max_iterations=5
        )
        
        if result['success']:
            print(f"✅ Refinamento concluído: qualidade {result['quality']:.2f}")
            return result
        else:
            raise Exception("Refinamento não convergiu")
        
    except Exception as e:
        print(f"❌ Erro ao refinar conteúdo: {e}")
        raise
