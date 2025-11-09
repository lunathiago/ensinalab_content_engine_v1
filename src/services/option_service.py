"""
Service para Options
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from src.models.option import Option
from src.models.video import Video, VideoStatus

class OptionService:
    """Serviço de gerenciamento de opções"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_options_by_briefing(self, briefing_id: int) -> List[Option]:
        """Obtém todas as opções de um briefing"""
        return self.db.query(Option).filter(
            Option.briefing_id == briefing_id
        ).order_by(
            Option.relevance_score.desc()
        ).all()
    
    def get_option(self, option_id: int) -> Optional[Option]:
        """Obtém uma opção por ID"""
        return self.db.query(Option).filter(Option.id == option_id).first()
    
    def select_option(self, option_id: int, notes: Optional[str] = None) -> Option:
        """
        Marca uma opção como selecionada
        
        Args:
            option_id: ID da opção a selecionar
            notes: Notas adicionais sobre a seleção (opcional)
        
        Returns:
            Option selecionada
        """
        option = self.get_option(option_id)
        if not option:
            raise ValueError(f"Option {option_id} not found")
        
        # Desmarcar outras opções do mesmo briefing
        self.db.query(Option).filter(
            Option.briefing_id == option.briefing_id,
            Option.id != option_id
        ).update({'is_selected': False})
        
        # Marcar esta opção
        option.is_selected = True
        if notes:
            option.selection_notes = notes
        
        self.db.commit()
        self.db.refresh(option)
        
        print(f"✅ Opção {option_id} selecionada para briefing {option.briefing_id}")
        
        return option
    
    def create_option(self, option_data: dict) -> Option:
        """Cria uma nova opção (usado pelo motor de geração)"""
        # Filtrar campos inválidos antes de criar instância de Option
        allowed_fields = {
            'briefing_id', 'title', 'summary', 'script_outline', 'key_points',
            'estimated_duration', 'tone', 'approach', 'relevance_score',
            'quality_score', 'is_selected', 'selection_notes'
        }

        sanitized = {k: v for k, v in option_data.items() if k in allowed_fields}

        # Campos extras vão para extra_data
        extra_keys = set(option_data.keys()) - set(sanitized.keys())
        if extra_keys:
            extra_data = {k: option_data[k] for k in extra_keys}
            sanitized['extra_data'] = extra_data
            print(f"ℹ️  Campos extras salvos em extra_data: {sorted(list(extra_keys))}")

        option = Option(**sanitized)
        self.db.add(option)
        self.db.commit()
        self.db.refresh(option)
        return option
