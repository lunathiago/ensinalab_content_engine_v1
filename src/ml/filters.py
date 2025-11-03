"""
Filtros para validação e scoring de opções
"""
from typing import Dict, List

class ContentFilter:
    """Filtros para validar e pontuar opções de conteúdo"""
    
    def apply_filters(self, options: List[Dict], briefing_context: Dict) -> List[Dict]:
        """
        Aplica todos os filtros e adiciona scores
        """
        filtered_options = []
        
        for option in options:
            # Filtros de bloqueio
            if not self._safety_filter(option):
                continue  # Bloqueia conteúdo inadequado
            
            # Scores
            option['relevance_score'] = self._calculate_relevance(option, briefing_context)
            option['quality_score'] = self._calculate_quality(option)
            
            filtered_options.append(option)
        
        # Ordena por relevância
        filtered_options.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_options
    
    def _safety_filter(self, option: Dict) -> bool:
        """
        Filtro de segurança - bloqueia conteúdo impróprio
        """
        # Lista de palavras bloqueadas (expandir conforme necessário)
        blocked_keywords = ['violência', 'discriminação', 'político-partidário']
        
        text = f"{option.get('title', '')} {option.get('summary', '')}".lower()
        
        for keyword in blocked_keywords:
            if keyword in text:
                return False
        
        return True
    
    def _calculate_relevance(self, option: Dict, context: Dict) -> float:
        """
        Calcula score de relevância (0-1)
        """
        score = 0.5  # Base
        
        # Verifica alinhamento com objetivo
        if context.get('educational_goal'):
            if any(word in option.get('summary', '').lower() 
                   for word in context['educational_goal'].lower().split()):
                score += 0.2
        
        # Verifica duração compatível
        target_duration = context.get('duration_minutes', 5) * 60
        estimated_duration = option.get('estimated_duration', 300)
        
        duration_diff = abs(target_duration - estimated_duration)
        if duration_diff < 60:  # Diferença menor que 1 minuto
            score += 0.2
        elif duration_diff < 120:  # Diferença menor que 2 minutos
            score += 0.1
        
        # Verifica tom compatível
        if context.get('tone') == option.get('tone'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_quality(self, option: Dict) -> float:
        """
        Calcula score de qualidade (0-1)
        """
        score = 0.5  # Base
        
        # Verifica completude
        required_fields = ['title', 'summary', 'script_outline', 'key_points']
        complete_fields = sum(1 for field in required_fields if option.get(field))
        score += (complete_fields / len(required_fields)) * 0.3
        
        # Verifica tamanho mínimo do conteúdo
        if len(option.get('summary', '')) > 50:
            score += 0.1
        
        if len(option.get('script_outline', '')) > 100:
            score += 0.1
        
        return min(score, 1.0)
