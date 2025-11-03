"""
Configurações para LangGraph Workflows
"""
import os
from pathlib import Path

# Base directory para checkpoints
CHECKPOINT_BASE_DIR = Path(os.getenv("CHECKPOINT_DIR", "/tmp/langgraph_checkpoints"))
CHECKPOINT_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Video Generation Workflow
VIDEO_WORKFLOW_CONFIG = {
    "checkpoint_dir": CHECKPOINT_BASE_DIR / "video_generation",
    "max_retries": 3,
    "review_threshold": 0.7,  # Score mínimo para auto-aprovar
    "require_human_approval": True,  # Se True, sempre aguarda aprovação humana
}

# Briefing Analysis Workflow (Multi-Agent)
BRIEFING_WORKFLOW_CONFIG = {
    "num_options": 5,  # Número de opções a gerar
    "filter_threshold": 0.6,  # Score mínimo para passar no filtro
    "temperature": {
        "analyzer": 0.3,
        "generator": 0.8,
        "filter": 0.1,
        "ranker": 0.2
    }
}

# Content Refinement Workflow
REFINEMENT_WORKFLOW_CONFIG = {
    "target_quality": 0.85,  # Qualidade alvo (0-1)
    "max_iterations": 5,  # Máximo de ciclos de refinamento
    "convergence_threshold": 0.02,  # Melhoria mínima para continuar
    "quality_dimensions": [
        "clarity",
        "relevance",
        "structure",
        "applicability",
        "language"
    ]
}

# LangSmith Tracing (opcional)
LANGSMITH_CONFIG = {
    "enabled": os.getenv("LANGSMITH_TRACING", "false").lower() == "true",
    "api_key": os.getenv("LANGSMITH_API_KEY"),
    "project": os.getenv("LANGSMITH_PROJECT", "ensinalab-content-engine")
}

# Criar diretórios de checkpoint
VIDEO_WORKFLOW_CONFIG["checkpoint_dir"].mkdir(parents=True, exist_ok=True)
