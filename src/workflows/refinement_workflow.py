"""
Workflow LangGraph para refinamento iterativo de conteúdo

Ciclo: Gerar → Avaliar → Refinar → Repetir até qualidade adequada
"""
from typing import Dict, Literal
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from src.workflows.states import ContentRefinementState
from src.config.settings import settings

class ContentRefinementWorkflow:
    """
    Workflow de refinamento iterativo com avaliação automática
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.evaluator_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de refinamento"""
        
        workflow = StateGraph(ContentRefinementState)
        
        # Adicionar nós
        workflow.add_node("evaluate", self._evaluate_node)
        workflow.add_node("refine", self._refine_node)
        workflow.add_node("complete", self._complete_node)
        
        # Definir fluxo
        workflow.set_entry_point("evaluate")
        
        # Decisão após avaliação
        workflow.add_conditional_edges(
            "evaluate",
            self._should_refine,
            {
                "refine": "refine",
                "complete": "complete"
            }
        )
        
        # Loop: refinar volta para avaliar
        workflow.add_edge("refine", "evaluate")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def _evaluate_node(self, state: ContentRefinementState) -> ContentRefinementState:
        """Avalia a qualidade do conteúdo atual"""
        print(f"📊 Avaliando qualidade (iteração {state['iteration']})...")
        
        content = state['current_version'] if state['iteration'] > 0 else state['content']
        
        try:
            # Avaliar com LLM
            evaluation_prompt = self._build_evaluation_prompt(content, state['content_type'])
            
            messages = [
                SystemMessage(content="Você é um avaliador de qualidade de conteúdo educacional para professores."),
                HumanMessage(content=evaluation_prompt)
            ]
            
            response = self.evaluator_llm.invoke(messages)
            
            # Parse score (simplificado)
            score = self._parse_quality_score(response.content)
            feedback = self._extract_feedback(response.content)
            
            state['quality_scores'].append(score)
            state['quality_feedback'].append(feedback)
            
            print(f"   → Score: {score:.2f}")
            print(f"   → Feedback: {feedback[:80]}...")
            
        except Exception as e:
            print(f"   ⚠️ Erro na avaliação: {e}")
            # Score médio como fallback
            score = 0.7
            state['quality_scores'].append(score)
            state['quality_feedback'].append("Avaliação automática indisponível")
        
        return state
    
    def _refine_node(self, state: ContentRefinementState) -> ContentRefinementState:
        """Refina o conteúdo baseado no feedback"""
        print(f"🔧 Refinando conteúdo...")
        
        try:
            # Pegar última avaliação
            latest_feedback = state['quality_feedback'][-1] if state['quality_feedback'] else "Melhorar clareza e estrutura"
            
            refinement_prompt = self._build_refinement_prompt(
                state['current_version'],
                latest_feedback,
                state['content_type']
            )
            
            messages = [
                SystemMessage(content="Você é um especialista em refinamento de conteúdo educacional."),
                HumanMessage(content=refinement_prompt)
            ]
            
            response = self.llm.invoke(messages)
            refined = response.content
            
            # Salvar versão refinada
            state['refined_versions'].append(refined)
            state['current_version'] = refined
            state['iteration'] += 1
            
            # Log de melhoria
            improvement = {
                "iteration": state['iteration'],
                "feedback_applied": latest_feedback[:100],
                "timestamp": str(datetime.utcnow())
            }
            state['improvement_log'].append(improvement)
            
            print(f"   ✓ Versão refinada {state['iteration']}")
            
        except Exception as e:
            print(f"   ⚠️ Erro no refinamento: {e}")
        
        return state
    
    def _complete_node(self, state: ContentRefinementState) -> ContentRefinementState:
        """Finaliza o processo de refinamento"""
        print(f"✅ Refinamento concluído!")
        
        state['final_content'] = state['current_version']
        state['final_quality'] = state['quality_scores'][-1] if state['quality_scores'] else 0.0
        state['converged'] = True
        
        # Determinar razão de conclusão
        if state['iteration'] >= state['max_iterations']:
            state['reason'] = f"Limite de iterações atingido ({state['max_iterations']})"
        elif state['final_quality'] >= state['target_quality']:
            state['reason'] = f"Qualidade alvo atingida ({state['final_quality']:.2f} >= {state['target_quality']:.2f})"
        else:
            state['reason'] = "Convergência prematura"
        
        print(f"   → Razão: {state['reason']}")
        print(f"   → Qualidade final: {state['final_quality']:.2f}")
        print(f"   → Iterações: {state['iteration']}")
        
        return state
    
    def _should_refine(self, state: ContentRefinementState) -> Literal["refine", "complete"]:
        """Decide se deve refinar ou completar"""
        
        # Verificar limite de iterações
        if state['iteration'] >= state['max_iterations']:
            return "complete"
        
        # Verificar qualidade
        if state['quality_scores']:
            latest_score = state['quality_scores'][-1]
            if latest_score >= state['target_quality']:
                return "complete"
        
        # Verificar convergência (score não melhora)
        if len(state['quality_scores']) >= 2:
            improvement = state['quality_scores'][-1] - state['quality_scores'][-2]
            if improvement < 0.02:  # Melhoria mínima
                print(f"   → Convergência detectada (melhoria: {improvement:.3f})")
                return "complete"
        
        return "refine"
    
    def _build_evaluation_prompt(self, content: str, content_type: str) -> str:
        """Constrói prompt de avaliação"""
        return f"""
Avalie a qualidade deste {content_type} para treinamento de professores:

**Conteúdo:**
{content[:500]}...

**Critérios de Avaliação:**
1. Clareza e objetividade
2. Relevância para professores
3. Estrutura e organização
4. Aplicabilidade prática
5. Linguagem adequada

Forneça:
- Score de 0 a 1 (formato: "SCORE: 0.XX")
- Feedback específico para melhorias

Responda em formato estruturado.
"""
    
    def _build_refinement_prompt(self, content: str, feedback: str, content_type: str) -> str:
        """Constrói prompt de refinamento"""
        return f"""
Refine este {content_type} com base no feedback:

**Conteúdo Atual:**
{content}

**Feedback:**
{feedback}

**Instruções:**
- Mantenha o mesmo tamanho aproximado
- Aplique as sugestões do feedback
- Melhore clareza e estrutura
- Mantenha foco em professores como público

Retorne APENAS o conteúdo refinado.
"""
    
    def _parse_quality_score(self, evaluation: str) -> float:
        """Extrai score da avaliação"""
        import re
        
        # Procurar padrão "SCORE: 0.XX"
        match = re.search(r'SCORE:\s*([0-9.]+)', evaluation, re.IGNORECASE)
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
            except:
                pass
        
        # Fallback: score médio
        return 0.7
    
    def _extract_feedback(self, evaluation: str) -> str:
        """Extrai feedback textual"""
        # Simplificado: pegar tudo após "Feedback"
        import re
        
        match = re.search(r'Feedback[:\s]*(.+)', evaluation, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()[:200]
        
        return evaluation[:200]
    
    def run(
        self, 
        content: str, 
        content_type: str = "script",
        target_quality: float = 0.85,
        max_iterations: int = 5
    ) -> Dict:
        """
        Executa refinamento iterativo
        
        Args:
            content: Conteúdo inicial
            content_type: Tipo ('script', 'outline', 'summary')
            target_quality: Qualidade alvo (0-1)
            max_iterations: Máximo de iterações
        
        Returns:
            Conteúdo refinado e metadata
        """
        
        from datetime import datetime
        
        # Estado inicial
        initial_state: ContentRefinementState = {
            "content": content,
            "content_type": content_type,
            "target_quality": target_quality,
            "quality_scores": [],
            "quality_feedback": [],
            "refined_versions": [],
            "current_version": content,
            "iteration": 0,
            "max_iterations": max_iterations,
            "final_content": None,
            "final_quality": None,
            "improvement_log": [],
            "converged": False,
            "reason": None
        }
        
        print(f"\n🔄 Iniciando refinamento iterativo")
        print(f"   Tipo: {content_type}")
        print(f"   Qualidade alvo: {target_quality:.2f}")
        print(f"   Max iterações: {max_iterations}")
        print("=" * 60)
        
        # Executar workflow
        final_state = self.graph.invoke(initial_state)
        
        print("=" * 60)
        
        return {
            "success": final_state['converged'],
            "content": final_state['final_content'],
            "quality": final_state['final_quality'],
            "metadata": {
                "iterations": final_state['iteration'],
                "quality_progression": final_state['quality_scores'],
                "improvement_log": final_state['improvement_log'],
                "reason": final_state['reason']
            }
        }
