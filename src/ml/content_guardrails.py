"""
Content Guardrails - Validação de briefings educacionais
Garante que apenas conteúdo relacionado a educação/treinamento seja aceito
"""
from typing import Dict, Tuple
from src.ml.llm_service import LLMService


class ContentGuardrails:
    """
    Guardrails para validar se briefings são apropriados para a plataforma
    
    Critérios:
    - Deve ser relacionado a educação, treinamento ou desenvolvimento profissional
    - Não deve conter conteúdo inapropriado, político, religioso ou comercial
    - Deve ter foco em aprendizagem e capacitação de professores/educadores
    """
    
    # Palavras-chave educacionais (alta relevância)
    EDUCATIONAL_KEYWORDS = {
        # Metodologias
        'metodologia', 'pedagogia', 'didática', 'ensino', 'aprendizagem',
        'educação', 'treinamento', 'capacitação', 'formação', 'desenvolvimento',
        
        # Públicos
        'professor', 'professora', 'educador', 'educadora', 'docente',
        'coordenador', 'gestor escolar', 'pedagogo', 'aluno', 'estudante',
        
        # Níveis
        'infantil', 'fundamental', 'médio', 'eja', 'técnico', 'superior',
        'pré-escola', 'creche', 'berçário',
        
        # Áreas
        'alfabetização', 'letramento', 'matemática', 'ciências', 'leitura',
        'escrita', 'história', 'geografia', 'artes', 'música', 'educação física',
        
        # Conceitos
        'currículo', 'bncc', 'projeto pedagógico', 'plano de aula',
        'avaliação', 'inclusão', 'diversidade', 'competências', 'habilidades',
        
        # Metodologias específicas
        'montessori', 'waldorf', 'reggio emilia', 'construtivismo',
        'sociointeracionismo', 'pbl', 'steam', 'gamificação'
    }
    
    # Palavras-chave proibidas (conteúdo inapropriado)
    FORBIDDEN_KEYWORDS = {
        # Política
        'eleição', 'partido', 'candidato', 'político', 'governo', 'esquerda', 'direita',
        
        # Religião proselitista
        'converter', 'evangelizar', 'doutrina religiosa', 'crença obrigatória',
        
        # Comercial direto
        'vender', 'comprar', 'produto comercial', 'marketing direto', 'propaganda',
        
        # Conteúdo adulto
        'pornografia', 'sexual explícito', 'violência gráfica',
        
        # Discriminação
        'supremacia', 'inferioridade racial', 'ódio', 'preconceito explícito'
    }
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def validate_briefing(
        self, 
        title: str, 
        description: str,
        subject_area: str = "",
        target_audience: str = ""
    ) -> Tuple[bool, str, float]:
        """
        Valida se um briefing é apropriado para a plataforma
        
        Args:
            title: Título do briefing
            description: Descrição detalhada
            subject_area: Área do assunto (opcional)
            target_audience: Público-alvo (opcional)
        
        Returns:
            Tuple[is_valid, reason, confidence_score]
            - is_valid: True se aprovado
            - reason: Motivo da aprovação/rejeição
            - confidence_score: 0-1, quão confiante está a validação
        """
        
        # Combinar todos os textos
        full_text = f"{title} {description} {subject_area} {target_audience}".lower()
        
        # 1. Verificação rápida: palavras proibidas
        forbidden_check = self._check_forbidden_keywords(full_text)
        if not forbidden_check['is_valid']:
            return (False, forbidden_check['reason'], 0.95)
        
        # 2. Verificação de relevância educacional (keywords)
        relevance_score = self._calculate_educational_relevance(full_text)
        
        if relevance_score < 0.3:
            # Muito baixa relevância educacional, consultar LLM
            llm_validation = self._llm_validate_educational_content(
                title, description, subject_area, target_audience
            )
            
            if not llm_validation['is_valid']:
                return (
                    False, 
                    llm_validation['reason'],
                    llm_validation['confidence']
                )
        
        # 3. Aprovado
        if relevance_score >= 0.7:
            reason = "Briefing claramente educacional com alta relevância"
            confidence = 0.95
        elif relevance_score >= 0.5:
            reason = "Briefing educacional com relevância moderada"
            confidence = 0.85
        elif relevance_score >= 0.3:
            reason = "Briefing educacional com relevância aceitável"
            confidence = 0.75
        else:
            # Passou na validação LLM mas tem baixa relevância keyword
            reason = "Aprovado por análise contextual (LLM)"
            confidence = 0.70
        
        return (True, reason, confidence)
    
    def _check_forbidden_keywords(self, text: str) -> Dict:
        """Verifica se há palavras proibidas"""
        found_forbidden = []
        
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in text:
                found_forbidden.append(keyword)
        
        if found_forbidden:
            return {
                'is_valid': False,
                'reason': f"Conteúdo inapropriado detectado: {', '.join(found_forbidden[:3])}. "
                         "A plataforma aceita apenas conteúdo educacional."
            }
        
        return {'is_valid': True}
    
    def _calculate_educational_relevance(self, text: str) -> float:
        """Calcula score de relevância educacional (0-1)"""
        matches = 0
        
        for keyword in self.EDUCATIONAL_KEYWORDS:
            if keyword in text:
                matches += 1
        
        # Normalizar (assumindo que ter 5+ keywords = 100% relevância)
        score = min(matches / 5.0, 1.0)
        
        return score
    
    def _llm_validate_educational_content(
        self,
        title: str,
        description: str,
        subject_area: str,
        target_audience: str
    ) -> Dict:
        """
        Usa LLM para validação contextual quando keywords não são suficientes
        """
        
        prompt = f"""
Você é um validador de conteúdo educacional. Analise se o briefing abaixo é apropriado para uma plataforma de treinamento de professores.

**Critérios de APROVAÇÃO:**
- Relacionado a educação, ensino, aprendizagem ou capacitação de professores
- Foco em desenvolvimento profissional de educadores
- Metodologias pedagógicas, práticas de sala de aula, gestão escolar
- Conteúdo curricular, avaliação, inclusão, tecnologia educacional

**Critérios de REJEIÇÃO:**
- Conteúdo político-partidário, religioso proselitista ou comercial
- Não relacionado a educação ou treinamento profissional
- Temas genéricos sem aplicação educacional clara
- Conteúdo inapropriado ou discriminatório

**Briefing:**
Título: {title}
Descrição: {description}
Área: {subject_area}
Público: {target_audience}

**Responda APENAS em JSON:**
{{
    "is_valid": true/false,
    "reason": "Explicação breve (máx 100 caracteres)",
    "confidence": 0.0-1.0,
    "educational_relevance": "high/medium/low/none"
}}
"""
        
        try:
            response = self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            
            return {
                'is_valid': result.get('is_valid', False),
                'reason': result.get('reason', 'Validação inconclusiva'),
                'confidence': result.get('confidence', 0.5)
            }
            
        except Exception as e:
            print(f"⚠️ Erro na validação LLM: {e}")
            # Fallback conservador: rejeitar em caso de erro
            return {
                'is_valid': False,
                'reason': "Não foi possível validar o conteúdo educacional",
                'confidence': 0.6
            }
    
    def get_educational_suggestions(self, rejected_briefing: str) -> str:
        """
        Sugere como reformular um briefing rejeitado para ser educacional
        """
        
        prompt = f"""
Um briefing foi rejeitado por não ser suficientemente educacional.

Briefing original: {rejected_briefing}

Sugira 2-3 formas de reformulá-lo para focar em:
- Treinamento de professores
- Metodologias pedagógicas
- Práticas de sala de aula
- Desenvolvimento profissional docente

Seja breve (máx 200 caracteres por sugestão).
"""
        
        try:
            response = self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response
            
        except Exception as e:
            return "Não foi possível gerar sugestões no momento."
