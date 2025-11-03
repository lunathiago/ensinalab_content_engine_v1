"""
Agentes para workflow de análise de briefing (multi-agente)

Fluxo: Analyzer → Generator → Filter → Ranker
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.config.settings import settings

class BriefingAnalyzerAgent:
    """
    Agente 1: Analisa o briefing e extrai intenções
    
    Responsabilidades:
    - Compreender o objetivo do treinamento
    - Identificar público-alvo e necessidades
    - Extrair palavras-chave e temas
    - Detectar gaps ou ambiguidades
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # Mais determinístico para análise
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def analyze(self, briefing_data: Dict) -> Dict:
        """Analisa um briefing"""
        
        system_prompt = """Você é um analista especializado em formação de professores.
Sua tarefa é analisar briefings de capacitação docente e extrair:

1. Objetivo principal do treinamento
2. Público-alvo detalhado (perfil dos professores)
3. Nível de profundidade necessário
4. Palavras-chave e conceitos principais
5. Possíveis lacunas ou ambiguidades no briefing
6. Sugestões de melhoria

Retorne em formato estruturado."""

        user_prompt = f"""
Analise este briefing de capacitação docente:

**Título:** {briefing_data.get('title')}
**Descrição:** {briefing_data.get('description')}
**Público-alvo:** {briefing_data.get('target_audience', 'Não especificado')}
**Área:** {briefing_data.get('subject_area', 'Não especificado')}
**Nível:** {briefing_data.get('teacher_experience_level', 'Não especificado')}
**Objetivo:** {briefing_data.get('training_goal', 'Não especificado')}
**Duração:** {briefing_data.get('duration_minutes', 5)} minutos
**Tom:** {briefing_data.get('tone', 'Não especificado')}

Forneça uma análise estruturada.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse da resposta (simplificado - em produção usar JSON)
        return {
            "analysis": response.content,
            "is_clear": True,  # TODO: detectar clareza
            "missing_info": [],
            "keywords": self._extract_keywords(briefing_data),
            "complexity": self._assess_complexity(briefing_data)
        }
    
    def _extract_keywords(self, briefing_data: Dict) -> List[str]:
        """Extrai palavras-chave relevantes"""
        text = f"{briefing_data.get('title', '')} {briefing_data.get('description', '')} {briefing_data.get('training_goal', '')}"
        # Simplificado - em produção usar NLP
        keywords = [word for word in text.lower().split() if len(word) > 4]
        return list(set(keywords))[:10]
    
    def _assess_complexity(self, briefing_data: Dict) -> str:
        """Avalia complexidade do briefing"""
        duration = briefing_data.get('duration_minutes', 5)
        if duration <= 3:
            return "simples"
        elif duration <= 7:
            return "médio"
        else:
            return "complexo"


class ContentGeneratorAgent:
    """
    Agente 2: Gera múltiplas opções de conteúdo
    
    Responsabilidades:
    - Gerar 3-5 propostas diferentes
    - Diversificar abordagens
    - Criar títulos atraentes
    - Esboçar roteiros
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.8,  # Mais criativo
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def generate_options(self, briefing_data: Dict, analysis: Dict) -> List[Dict]:
        """Gera opções baseadas no briefing e análise"""
        
        system_prompt = """Você é um especialista em criação de conteúdo para formação de professores.
Gere 4 propostas DIFERENTES de vídeos de capacitação, variando:
- Abordagem (teórica, prática, casos reais, passo-a-passo)
- Tom (formal, inspiracional, técnico, conversacional)
- Estrutura (linear, problematização, storytelling)

Cada proposta deve ter:
- Título atraente
- Resumo (2-3 frases)
- Roteiro esboçado
- 3-5 pontos-chave
- Duração estimada
- Abordagem pedagógica"""

        user_prompt = f"""
**Briefing:**
{briefing_data.get('title')}

**Análise:**
{analysis.get('analysis', 'N/A')}

**Contexto:**
- Público: {briefing_data.get('target_audience')}
- Área: {briefing_data.get('subject_area')}
- Nível: {briefing_data.get('teacher_experience_level')}
- Duração alvo: {briefing_data.get('duration_minutes')} minutos

Gere 4 propostas diversificadas em formato JSON:
```json
[
  {{
    "title": "...",
    "summary": "...",
    "script_outline": "...",
    "key_points": "ponto1; ponto2; ponto3",
    "estimated_duration": 300,
    "tone": "...",
    "approach": "..."
  }}
]
```
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON (simplificado)
        import json
        import re
        
        json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
        if json_match:
            try:
                options = json.loads(json_match.group())
                return options
            except:
                pass
        
        # Fallback
        return self._generate_fallback_options(briefing_data)
    
    def _generate_fallback_options(self, briefing_data: Dict) -> List[Dict]:
        """Gera opções fallback se parsing falhar"""
        base_title = briefing_data.get('title', 'Treinamento')
        return [
            {
                "title": f"{base_title} - Abordagem Prática",
                "summary": "Vídeo com foco em aplicação imediata",
                "script_outline": "Introdução → Exemplos práticos → Dicas → Conclusão",
                "key_points": "Aplicabilidade; Exemplos reais; Passo a passo",
                "estimated_duration": briefing_data.get('duration_minutes', 5) * 60,
                "tone": "prático",
                "approach": "Hands-on"
            },
            {
                "title": f"{base_title} - Fundamentos Teóricos",
                "summary": "Vídeo explicando a base conceitual",
                "script_outline": "Contextualização → Teoria → Aplicações → Conclusão",
                "key_points": "Conceitos; Teoria; Aplicações",
                "estimated_duration": briefing_data.get('duration_minutes', 5) * 60,
                "tone": "técnico",
                "approach": "Teórico-prático"
            }
        ]


class ContentFilterAgent:
    """
    Agente 3: Filtra e valida opções geradas
    
    Responsabilidades:
    - Aplicar filtros de segurança
    - Validar qualidade mínima
    - Detectar conteúdo problemático
    - Verificar alinhamento com briefing
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Mais rápido para validação
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def filter_options(self, options: List[Dict], briefing_data: Dict) -> List[Dict]:
        """Filtra opções aplicando critérios de qualidade"""
        
        filtered = []
        
        for option in options:
            # 1. Filtro de segurança
            if not self._safety_check(option):
                continue
            
            # 2. Validação de completude
            if not self._completeness_check(option):
                continue
            
            # 3. Alinhamento com briefing
            alignment_score = self._check_alignment(option, briefing_data)
            if alignment_score < 0.5:
                continue
            
            # Adicionar metadata
            option['alignment_score'] = alignment_score
            option['passed_filters'] = True
            
            filtered.append(option)
        
        return filtered
    
    def _safety_check(self, option: Dict) -> bool:
        """Verifica segurança do conteúdo"""
        blocked_keywords = [
            'político-partidário', 'discriminação', 'violência',
            'conteúdo inadequado', 'ofensivo'
        ]
        
        text = f"{option.get('title', '')} {option.get('summary', '')}".lower()
        
        return not any(keyword in text for keyword in blocked_keywords)
    
    def _completeness_check(self, option: Dict) -> bool:
        """Verifica se opção está completa"""
        required_fields = ['title', 'summary', 'script_outline', 'key_points']
        return all(option.get(field) for field in required_fields)
    
    def _check_alignment(self, option: Dict, briefing_data: Dict) -> float:
        """Calcula alinhamento com briefing (0-1)"""
        score = 0.5  # Base
        
        # Verifica duração compatível
        target_duration = briefing_data.get('duration_minutes', 5) * 60
        option_duration = option.get('estimated_duration', 300)
        duration_diff = abs(target_duration - option_duration)
        
        if duration_diff < 60:
            score += 0.3
        elif duration_diff < 120:
            score += 0.15
        
        # Verifica tom
        if briefing_data.get('tone') == option.get('tone'):
            score += 0.2
        
        return min(score, 1.0)


class ContentRankerAgent:
    """
    Agente 4: Ranqueia e pontua opções filtradas
    
    Responsabilidades:
    - Calcular scores de relevância
    - Calcular scores de qualidade
    - Ordenar opções
    - Fornecer justificativas
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def rank_options(self, options: List[Dict], briefing_data: Dict) -> List[Dict]:
        """Ranqueia opções por relevância e qualidade"""
        
        for option in options:
            # Calcular scores
            option['relevance_score'] = self._calculate_relevance(option, briefing_data)
            option['quality_score'] = self._calculate_quality(option)
            option['overall_score'] = (
                option['relevance_score'] * 0.6 + 
                option['quality_score'] * 0.4
            )
            
            # Gerar justificativa
            option['ranking_rationale'] = self._generate_rationale(option, briefing_data)
        
        # Ordenar por score geral
        ranked = sorted(options, key=lambda x: x['overall_score'], reverse=True)
        
        return ranked
    
    def _calculate_relevance(self, option: Dict, briefing_data: Dict) -> float:
        """Calcula relevância (0-1)"""
        score = 0.5
        
        # Alinhamento com objetivo
        if briefing_data.get('training_goal'):
            goal_words = set(briefing_data['training_goal'].lower().split())
            summary_words = set(option.get('summary', '').lower().split())
            overlap = len(goal_words & summary_words)
            score += min(overlap * 0.1, 0.3)
        
        # Alinhamento com tom
        if briefing_data.get('tone') == option.get('tone'):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_quality(self, option: Dict) -> float:
        """Calcula qualidade (0-1)"""
        score = 0.5
        
        # Completude
        if len(option.get('summary', '')) > 50:
            score += 0.15
        if len(option.get('script_outline', '')) > 100:
            score += 0.15
        
        # Estrutura
        if 'key_points' in option and len(option['key_points'].split(';')) >= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_rationale(self, option: Dict, briefing_data: Dict) -> str:
        """Gera justificativa do ranking"""
        reasons = []
        
        if option['relevance_score'] > 0.8:
            reasons.append("Alta relevância com objetivo do treinamento")
        
        if option['quality_score'] > 0.8:
            reasons.append("Conteúdo bem estruturado e completo")
        
        if option.get('tone') == briefing_data.get('tone'):
            reasons.append(f"Tom '{option['tone']}' alinhado com solicitação")
        
        return "; ".join(reasons) if reasons else "Opção adequada"
