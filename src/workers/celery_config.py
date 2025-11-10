"""
Configuração do Celery
"""
from celery import Celery
from src.config.settings import settings
from src.config.database import import_all_models

# IMPORTANTE: Garantir que todos os models estão registrados
import_all_models()

# Criar app Celery
celery_app = Celery(
    "ensinalab_content_engine",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configuração
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutos limite por task
    worker_prefetch_multiplier=1,  # Processar uma task por vez
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['src.workers'])
