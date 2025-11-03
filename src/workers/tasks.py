"""
Tasks assíncronas do Celery
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

class DatabaseTask(Task):
    """Base task com sessão de banco de dados"""
    
    def __call__(self, *args, **kwargs):
        with SessionLocal() as db:
            self.db = db
            return super().__call__(*args, **kwargs)

@celery_app.task(base=DatabaseTask, bind=True)
def generate_options(self, briefing_id: int):
    """
    Task para gerar opções de conteúdo a partir de um briefing
    """
    try:
        print(f"🔄 Gerando opções para briefing {briefing_id}...")
        
        # Obter briefing
        briefing_service = BriefingService(self.db)
        briefing = briefing_service.get_briefing(briefing_id)
        
        if not briefing:
            print(f"❌ Briefing {briefing_id} não encontrado")
            return
        
        # Atualizar status
        briefing_service.update_status(briefing_id, BriefingStatus.PROCESSING)
        
        # Gerar opções com LLM
        llm_service = LLMService()
        briefing_data = {
            'title': briefing.title,
            'description': briefing.description,
            'target_grade': briefing.target_grade,
            'target_age_min': briefing.target_age_min,
            'target_age_max': briefing.target_age_max,
            'educational_goal': briefing.educational_goal,
            'duration_minutes': briefing.duration_minutes,
            'tone': briefing.tone
        }
        
        raw_options = llm_service.generate_options(briefing_data)
        
        # Aplicar filtros
        content_filter = ContentFilter()
        filtered_options = content_filter.apply_filters(raw_options, briefing_data)
        
        # Salvar opções no banco
        option_service = OptionService(self.db)
        for option_data in filtered_options:
            option_data['briefing_id'] = briefing_id
            option_service.create_option(option_data)
        
        # Atualizar status
        briefing_service.update_status(briefing_id, BriefingStatus.OPTIONS_READY)
        
        print(f"✅ {len(filtered_options)} opções geradas para briefing {briefing_id}")
        
        return {
            "briefing_id": briefing_id,
            "options_count": len(filtered_options)
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar opções: {e}")
        briefing_service.update_status(briefing_id, BriefingStatus.FAILED)
        raise

@celery_app.task(base=DatabaseTask, bind=True)
def generate_video(self, video_id: int):
    """
    Task para gerar vídeo a partir de uma opção selecionada
    """
    try:
        print(f"🎬 Gerando vídeo {video_id}...")
        
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
        
        # 1. Aprimorar roteiro
        print("📝 Aprimorando roteiro...")
        llm_service = LLMService()
        full_script = llm_service.enhance_script(
            option.script_outline,
            {
                'target_grade': briefing.target_grade,
                'duration_minutes': briefing.duration_minutes,
                'tone': briefing.tone
            }
        )
        video_service.update_status(video_id, VideoStatus.PROCESSING, progress=0.3)
        
        # 2. Gerar áudio (TTS)
        print("🎤 Gerando áudio...")
        tts_service = TTSService()
        audio_path = tts_service.generate_audio(full_script, video_id=video_id)
        video_service.update_status(video_id, VideoStatus.PROCESSING, progress=0.5)
        
        # 3. Gerar vídeo
        print("🎥 Gerando vídeo...")
        video_generator = VideoGenerator()
        result = video_generator.generate_video(
            script=full_script,
            audio_path=audio_path,
            metadata={
                'title': option.title,
                'duration': option.estimated_duration
            },
            video_id=video_id
        )
        video_service.update_status(video_id, VideoStatus.PROCESSING, progress=0.9)
        
        # 4. Finalizar
        video_service.complete_video(
            video_id=video_id,
            file_path=result['file_path'],
            file_size=result['file_size'],
            duration=result['duration'],
            thumbnail_path=result.get('thumbnail_path')
        )
        
        print(f"✅ Vídeo {video_id} gerado com sucesso!")
        
        return {
            "video_id": video_id,
            "file_path": result['file_path'],
            "duration": result['duration']
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar vídeo: {e}")
        video_service.update_status(
            video_id, 
            VideoStatus.FAILED, 
            error_message=str(e)
        )
        raise
