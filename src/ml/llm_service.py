"""
Service de LLM - integração com OpenAI/outros modelos
"""
from typing import List, Dict
from openai import OpenAI
from src.config.settings import settings

class LLMService:
    """Serviço para interação com modelos de linguagem"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def generate_options(self, briefing_data: Dict) -> List[Dict]:
        """
        Gera múltiplas opções de conteúdo a partir de um briefing
        
        Retorna 3-5 propostas diferentes
        """
        prompt = self._build_options_prompt(briefing_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Maior criatividade para gerar opções variadas
                max_tokens=2000
            )
            
            # Parse da resposta e extração das opções
            options_text = response.choices[0].message.content
            options = self._parse_options(options_text)
            
            return options
            
        except Exception as e:
            print(f"Erro ao gerar opções: {e}")
            return []
    
    def _get_system_prompt(self) -> str:
        """Prompt de sistema para o LLM"""
        return """Você é um especialista em educação brasileira e criação de conteúdo pedagógico.
Sua tarefa é analisar briefings de gestores escolares e gerar múltiplas opções de conteúdo educacional em vídeo.

Para cada briefing, você deve:
1. Compreender o objetivo pedagógico
2. Considerar a faixa etária e série
3. Gerar 3-5 propostas DIFERENTES de abordagem
4. Cada proposta deve ter: título, resumo, roteiro esboçado, pontos-chave, tom, duração estimada

As propostas devem seguir diretrizes pedagógicas brasileiras (BNCC quando aplicável).
"""
    
    def _build_options_prompt(self, briefing_data: Dict) -> str:
        """Constrói o prompt para gerar opções"""
        return f"""
Analise este briefing e gere 3-5 opções diferentes de conteúdo em vídeo:

**Briefing:**
- Título: {briefing_data.get('title')}
- Descrição: {briefing_data.get('description')}
- Público: {briefing_data.get('target_grade', 'não especificado')} ({briefing_data.get('target_age_min')}-{briefing_data.get('target_age_max')} anos)
- Objetivo: {briefing_data.get('educational_goal', 'não especificado')}
- Duração desejada: {briefing_data.get('duration_minutes', 5)} minutos
- Tom: {briefing_data.get('tone', 'neutro')}

Gere as opções no seguinte formato JSON:
```json
[
  {{
    "title": "Título da Opção 1",
    "summary": "Resumo da proposta",
    "script_outline": "Esboço do roteiro",
    "key_points": "Ponto 1; Ponto 2; Ponto 3",
    "tone": "formal/descontraído/motivacional",
    "approach": "Abordagem pedagógica",
    "estimated_duration": 300
  }}
]
```
"""
    
    def _parse_options(self, options_text: str) -> List[Dict]:
        """Parse da resposta do LLM em lista de opções"""
        import json
        import re
        
        # Extrai JSON da resposta
        json_match = re.search(r'\[.*\]', options_text, re.DOTALL)
        if json_match:
            try:
                options = json.loads(json_match.group())
                return options
            except json.JSONDecodeError:
                pass
        
        # Fallback: retorna opção mock se parsing falhar
        return [{
            "title": "Opção de Exemplo",
            "summary": "Esta é uma opção de exemplo gerada automaticamente",
            "script_outline": "Introdução -> Desenvolvimento -> Conclusão",
            "key_points": "Ponto 1; Ponto 2; Ponto 3",
            "tone": "neutro",
            "approach": "Expositiva",
            "estimated_duration": 300
        }]
    
    def enhance_script(self, script_outline: str, context: Dict) -> str:
        """
        Aprimora um roteiro esboçado em roteiro completo
        """
        prompt = f"""
Expanda este roteiro esboçado em um roteiro completo para narração de vídeo:

**Roteiro Esboçado:**
{script_outline}

**Contexto:**
- Público: {context.get('target_grade')}
- Duração: {context.get('duration_minutes')} minutos
- Tom: {context.get('tone')}

Gere um roteiro completo, pronto para narração, dividido em cenas.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um roteirista de vídeos educacionais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao aprimorar roteiro: {e}")
            return script_outline
