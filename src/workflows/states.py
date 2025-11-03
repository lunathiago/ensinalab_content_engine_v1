"""
Estados compartilhados dos workflows LangGraph
"""
from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime

class BriefingAnalysisState(TypedDict):
    """Estado para workflow de análise de briefing"""
    # Input
    briefing_id: int
    briefing_data: Dict
    
    # Processamento
    analysis_result: Optional[Dict]
    generated_options: List[Dict]
    filtered_options: List[Dict]
    ranked_options: List[Dict]
    
    # Metadata
    current_step: str
    errors: List[str]
    retry_count: int
    started_at: datetime

class VideoGenerationState(TypedDict):
    """Estado para workflow de geração de vídeo"""
    # Input
    video_id: int
    option_id: int
    briefing_data: Dict
    script_outline: str
    
    # Análise
    script_analysis: Optional[Dict]
    quality_score: float
    
    # Geração
    enhanced_script: Optional[str]
    audio_path: Optional[str]
    video_path: Optional[str]
    thumbnail_path: Optional[str]
    
    # Revisão e Aprovação
    revision_feedback: List[str]
    approval_status: Literal["pending", "approved", "rejected", "needs_revision"]
    human_feedback: Optional[str]
    
    # Refinamento
    refinement_iterations: int
    max_iterations: int
    
    # Metadata
    current_step: str
    progress: float
    errors: List[str]
    checkpoints: List[Dict]
    started_at: datetime
    completed_at: Optional[datetime]

class ContentRefinementState(TypedDict):
    """Estado para ciclo de refinamento de conteúdo"""
    # Input
    content: str
    content_type: Literal["script", "outline", "summary"]
    target_quality: float
    
    # Avaliação
    quality_scores: List[float]
    quality_feedback: List[str]
    
    # Refinamento
    refined_versions: List[str]
    current_version: str
    iteration: int
    max_iterations: int
    
    # Resultado
    final_content: Optional[str]
    final_quality: Optional[float]
    improvement_log: List[Dict]
    
    # Metadata
    converged: bool
    reason: Optional[str]

class HumanReviewState(TypedDict):
    """Estado para revisão humana (human-in-the-loop)"""
    # Input
    content_id: int
    content_type: Literal["options", "script", "video"]
    content_data: Dict
    
    # Revisão
    review_status: Literal["pending", "approved", "rejected", "revision_requested"]
    reviewer_feedback: Optional[str]
    requested_changes: List[str]
    
    # Checkpoint
    checkpoint_id: Optional[str]
    can_resume: bool
    resume_from_step: Optional[str]
    
    # Metadata
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_id: Optional[str]
