"""
Workflow LangGraph para análise de briefing (multi-agente)

Fluxo: Analyzer → Generator → Filter → Ranker
"""
from typing import Dict
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.workflows.states import BriefingAnalysisState
from src.workflows.briefing_agents import (
    BriefingAnalyzerAgent,
    ContentGeneratorAgent,
    ContentFilterAgent,
    ContentRankerAgent
)

class BriefingAnalysisWorkflow:
    """
    Workflow completo de análise de briefing usando múltiplos agentes
    """
    
    def __init__(self):
        self.analyzer = BriefingAnalyzerAgent()
        self.generator = ContentGeneratorAgent()
        self.filter = ContentFilterAgent()
        self.ranker = ContentRankerAgent()
        
        # Criar grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de estados"""
        
        workflow = StateGraph(BriefingAnalysisState)
        
        # Adicionar nós (agentes)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("filter", self._filter_node)
        workflow.add_node("rank", self._rank_node)
        
        # Definir fluxo
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "generate")
        workflow.add_edge("generate", "filter")
        workflow.add_edge("filter", "rank")
        workflow.add_edge("rank", END)
        
        return workflow.compile()
    
    def _analyze_node(self, state: BriefingAnalysisState) -> BriefingAnalysisState:
        """Nó 1: Análise do briefing"""
        print(f"🔍 Analisando briefing {state['briefing_id']}...")
        
        try:
            analysis = self.analyzer.analyze(state['briefing_data'])
            state['analysis_result'] = analysis
            state['current_step'] = 'analyzed'
        except Exception as e:
            state['errors'].append(f"Erro na análise: {str(e)}")
        
        return state
    
    def _generate_node(self, state: BriefingAnalysisState) -> BriefingAnalysisState:
        """Nó 2: Geração de opções (3-6 opções)"""
        print(f"✨ Gerando opções...")
        
        try:
            options = self.generator.generate_options(
                state['briefing_data'],
                state['analysis_result']
            )
            state['generated_options'] = options
            state['current_step'] = 'generated'
            print(f"   → {len(options)} opções geradas")
        except Exception as e:
            state['errors'].append(f"Erro na geração: {str(e)}")
            state['generated_options'] = []
        
        return state
    
    def _filter_node(self, state: BriefingAnalysisState) -> BriefingAnalysisState:
        """Nó 3: Filtragem de opções"""
        print(f"🔍 Filtrando opções...")
        
        try:
            filtered = self.filter.filter_options(
                state['generated_options'],
                state['briefing_data']
            )
            state['filtered_options'] = filtered
            state['current_step'] = 'filtered'
            print(f"   → {len(filtered)} opções aprovadas nos filtros")
        except Exception as e:
            state['errors'].append(f"Erro na filtragem: {str(e)}")
            state['filtered_options'] = state['generated_options']
        
        return state
    
    def _rank_node(self, state: BriefingAnalysisState) -> BriefingAnalysisState:
        """Nó 4: Ranqueamento de opções"""
        print(f"📊 Ranqueando opções...")
        
        try:
            ranked = self.ranker.rank_options(
                state['filtered_options'],
                state['briefing_data']
            )
            state['ranked_options'] = ranked
            state['current_step'] = 'completed'
            
            if ranked:
                print(f"   → Top opção: {ranked[0]['title']} (score: {ranked[0]['overall_score']:.2f})")
        except Exception as e:
            state['errors'].append(f"Erro no ranqueamento: {str(e)}")
            state['ranked_options'] = state['filtered_options']
        
        return state
    
    def run(self, briefing_id: int, briefing_data: Dict) -> Dict:
        """
        Executa o workflow completo
        
        Args:
            briefing_id: ID do briefing
            briefing_data: Dados do briefing
        
        Returns:
            Opções ranqueadas e metadata
        """
        
        # Estado inicial
        initial_state: BriefingAnalysisState = {
            "briefing_id": briefing_id,
            "briefing_data": briefing_data,
            "analysis_result": None,
            "generated_options": [],
            "filtered_options": [],
            "ranked_options": [],
            "current_step": "initializing",
            "errors": [],
            "retry_count": 0,
            "started_at": datetime.utcnow()
        }
        
        # Executar workflow
        print(f"\n🚀 Iniciando workflow de análise de briefing #{briefing_id}")
        print("=" * 60)
        
        final_state = self.graph.invoke(initial_state)
        
        print("=" * 60)
        print(f"✅ Workflow concluído!")
        print(f"   Status: {final_state['current_step']}")
        print(f"   Opções geradas: {len(final_state['generated_options'])}")
        print(f"   Opções filtradas: {len(final_state['filtered_options'])}")
        print(f"   Opções finais: {len(final_state['ranked_options'])}")
        if final_state['errors']:
            print(f"   ⚠️ Erros: {len(final_state['errors'])}")
        print()
        
        return {
            "success": len(final_state['ranked_options']) > 0,
            "options": final_state['ranked_options'],
            "metadata": {
                "briefing_id": briefing_id,
                "analysis": final_state['analysis_result'],
                "generated_count": len(final_state['generated_options']),
                "filtered_count": len(final_state['filtered_options']),
                "final_count": len(final_state['ranked_options']),
                "errors": final_state['errors'],
                "completed_at": datetime.utcnow().isoformat()
            }
        }
