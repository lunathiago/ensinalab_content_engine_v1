"""
Workflow LangGraph para geração de vídeo com state machine

Estados: análise → geração → revisão → aprovação → produção
"""
from typing import Dict, Literal, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.workflows.states import VideoGenerationState
from src.ml.llm_service import LLMService
from src.video.factory import VideoGeneratorFactory

class VideoGenerationWorkflow:
    """
    State machine para geração de vídeo com estados bem definidos
    Usa factory pattern para escolher gerador dinamicamente
    """
    
    def __init__(
        self, 
        generator_type: str = 'simple',
        provider: Optional[str] = None
    ):
        self.llm_service = LLMService()
        
        # Criar gerador via factory
        self.video_generator = VideoGeneratorFactory.create(
            generator_type=generator_type,
            provider=provider
        )
        
        self.generator_type = generator_type
        
        # Checkpointer para salvar estado
        self.checkpointer = MemorySaver()
        
        # Criar grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói a state machine"""
        
        workflow = StateGraph(VideoGenerationState)
        
        # Adicionar nós (estados)
        workflow.add_node("analyze_script", self._analyze_script_node)
        workflow.add_node("enhance_script", self._enhance_script_node)
        workflow.add_node("generate_audio", self._generate_audio_node)
        workflow.add_node("generate_video", self._generate_video_node)
        workflow.add_node("review", self._review_node)
        workflow.add_node("await_approval", self._await_approval_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Definir fluxo
        workflow.set_entry_point("analyze_script")
        
        # Fluxo principal
        workflow.add_edge("analyze_script", "enhance_script")
        workflow.add_edge("enhance_script", "generate_audio")
        workflow.add_edge("generate_audio", "generate_video")
        workflow.add_edge("generate_video", "review")
        
        # Decisão após revisão
        workflow.add_conditional_edges(
            "review",
            self._should_finalize,
            {
                "finalize": "finalize",
                "needs_revision": "enhance_script",
                "rejected": END
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _analyze_script_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 1: Análise do roteiro"""
        print("📋 Analisando roteiro...")
        
        state['current_step'] = 'analyzing'
        state['progress'] = 0.1
        
        try:
            # Análise simplificada do roteiro
            script = state['script_outline']
            
            analysis = {
                "length": len(script),
                "has_structure": "→" in script or "\n" in script,
                "estimated_words": len(script.split()),
                "quality_indicators": {
                    "has_intro": "introdução" in script.lower() or "olá" in script.lower(),
                    "has_conclusion": "conclusão" in script.lower() or "finalizar" in script.lower()
                }
            }
            
            # Score simples de qualidade inicial
            quality = 0.5
            if analysis["has_structure"]:
                quality += 0.2
            if analysis["quality_indicators"]["has_intro"]:
                quality += 0.15
            if analysis["quality_indicators"]["has_conclusion"]:
                quality += 0.15
            
            state['script_analysis'] = analysis
            state['quality_score'] = min(quality, 1.0)
            
            print(f"   ✓ Qualidade inicial: {state['quality_score']:.2f}")
            
        except Exception as e:
            state['errors'].append(f"Erro na análise: {str(e)}")
        
        return state
    
    def _enhance_script_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 2: Aprimoramento do roteiro"""
        print("✨ Aprimorando roteiro...")
        
        state['current_step'] = 'enhancing'
        state['progress'] = 0.3
        
        try:
            # Se já foi refinado, verificar feedback
            if state['refinement_iterations'] > 0 and state.get('human_feedback'):
                print(f"   → Aplicando feedback: {state['human_feedback'][:50]}...")
            
            enhanced = self.llm_service.enhance_script(
                state['script_outline'],
                state['briefing_data']
            )
            
            state['enhanced_script'] = enhanced
            state['refinement_iterations'] += 1
            
            print(f"   ✓ Roteiro aprimorado (iteração {state['refinement_iterations']})")
            
        except Exception as e:
            state['errors'].append(f"Erro no aprimoramento: {str(e)}")
            state['enhanced_script'] = state['script_outline']  # Fallback
        
        return state
    
    def _generate_audio_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 3: Geração de áudio (TTS) - REMOVIDO"""
        # O gerador agora cuida do TTS internamente
        print("🎤 Áudio será gerado pelo video generator...")
        
        state['current_step'] = 'generating_audio'
        state['progress'] = 0.5
        
        return state
    
    def _generate_video_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 4: Geração do vídeo usando factory pattern"""
        print(f"🎥 Gerando vídeo com {self.generator_type}...")
        
        state['current_step'] = 'generating_video'
        state['progress'] = 0.7
        
        try:
            # Preparar metadata
            metadata = {
                'tone': state['briefing_data'].get('tone', 'profissional'),
                'target_audience': state['briefing_data'].get('target_audience'),
                'subject_area': state['briefing_data'].get('subject_area')
            }
            
            # Gerar vídeo usando factory
            result = self.video_generator.generate(
                script=state['enhanced_script'],
                title=state['briefing_data'].get('title', 'Video'),
                metadata=metadata,
                video_id=state['video_id']
            )
            
            if result['success']:
                state['video_path'] = result['file_path']
                state['thumbnail_path'] = result.get('thumbnail_path', '')
                state['file_size'] = result.get('file_size', 0)
                state['duration'] = result.get('duration', 0)
                
                # Adicionar metadata do gerador
                if 'metadata' not in state:
                    state['metadata'] = {}
                state['metadata'].update(result.get('metadata', {}))
                
                print(f"   ✓ Vídeo gerado: {result['file_path']}")
                print(f"   → Duração: {result['duration']:.1f}s")
                print(f"   → Tamanho: {result['file_size'] / 1024 / 1024:.1f}MB")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                state['errors'].append(f"Erro na geração de vídeo: {error_msg}")
                print(f"   ✗ Falha na geração: {error_msg}")
            
        except Exception as e:
            state['errors'].append(f"Erro na geração de vídeo: {str(e)}")
            print(f"   ✗ Exceção: {e}")
        
        return state
    
    def _review_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 5: Revisão automática"""
        print("🔍 Revisando vídeo...")
        
        state['current_step'] = 'reviewing'
        state['progress'] = 0.85
        
        # Revisão automática
        feedback = []
        
        # Verificar se vídeo foi gerado
        if not state.get('video_path'):
            feedback.append("Vídeo não foi gerado")
            state['approval_status'] = 'rejected'
        elif state['quality_score'] < 0.6:
            feedback.append(f"Qualidade abaixo do esperado ({state['quality_score']:.2f})")
            state['approval_status'] = 'needs_revision'
        else:
            # ✅ FIX: Aprovar automaticamente se passou na revisão
            state['approval_status'] = 'approved'
        
        state['revision_feedback'] = feedback
        
        if feedback:
            print(f"   ⚠️ Issues encontrados: {len(feedback)}")
        else:
            print(f"   ✓ Revisão automática OK - Aprovado automaticamente")
        
        return state
    
    def _await_approval_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 6: Aguardando aprovação humana (checkpoint)"""
        print("⏸️  Aguardando aprovação humana...")
        
        state['current_step'] = 'awaiting_approval'
        state['progress'] = 0.9
        
        # Este nó cria um checkpoint - o workflow pausa aqui
        # e pode ser retomado depois que o humano aprovar
        
        print(f"   → Video ID: {state['video_id']}")
        print(f"   → Status: {state['approval_status']}")
        print(f"   → Checkpoint salvo")
        
        return state
    
    def _finalize_node(self, state: VideoGenerationState) -> VideoGenerationState:
        """Estado 7: Finalização"""
        print("✅ Finalizando...")
        
        state['current_step'] = 'completed'
        state['progress'] = 1.0
        state['completed_at'] = datetime.utcnow()
        
        print(f"   ✓ Vídeo concluído!")
        print(f"   → Caminho: {state.get('video_path', 'N/A')}")
        
        return state
    
    def _should_finalize(self, state: VideoGenerationState) -> Literal["finalize", "needs_revision", "rejected"]:
        """Decide próximo passo após revisão"""
        status = state['approval_status']
        
        if status == 'approved':
            return "finalize"
        elif status == 'needs_revision':
            # Verificar se já excedeu max_iterations
            if state['refinement_iterations'] >= state['max_iterations']:
                print(f"   ⚠️ Limite de iterações atingido ({state['max_iterations']})")
                return "rejected"
            return "needs_revision"
        else:  # rejected
            return "rejected"
    
    def run(
        self, 
        video_id: int, 
        option_id: int, 
        briefing_data: Dict, 
        script_outline: str,
        thread_id: str = None
    ) -> Dict:
        """
        Executa o workflow de geração de vídeo
        
        Args:
            video_id: ID do vídeo
            option_id: ID da opção selecionada
            briefing_data: Dados do briefing
            script_outline: Roteiro esboçado
            thread_id: ID da thread (para retomar checkpoint)
        
        Returns:
            Resultado e estado final
        """
        
        # Estado inicial
        initial_state: VideoGenerationState = {
            "video_id": video_id,
            "option_id": option_id,
            "briefing_data": briefing_data,
            "script_outline": script_outline,
            "script_analysis": None,
            "quality_score": 0.0,
            "enhanced_script": None,
            "audio_path": None,
            "video_path": None,
            "thumbnail_path": None,
            "revision_feedback": [],
            "approval_status": "pending",
            "human_feedback": None,
            "refinement_iterations": 0,
            "max_iterations": 3,
            "current_step": "initializing",
            "progress": 0.0,
            "errors": [],
            "checkpoints": [],
            "started_at": datetime.utcnow(),
            "completed_at": None
        }
        
        # Config para checkpointing
        config = {
            "configurable": {
                "thread_id": thread_id or f"video_{video_id}"
            }
        }
        
        print(f"\n🎬 Iniciando workflow de geração de vídeo #{video_id}")
        print("=" * 60)
        
        try:
            # Executar workflow com checkpoint
            final_state = self.graph.invoke(initial_state, config)
            
            print("=" * 60)
            
            return {
                "success": final_state['current_step'] == 'completed',
                "video_path": final_state.get('video_path'),
                "thumbnail_path": final_state.get('thumbnail_path'),
                "status": final_state['approval_status'],
                "metadata": {
                    "video_id": video_id,
                    "current_step": final_state['current_step'],
                    "progress": final_state['progress'],
                    "refinement_iterations": final_state['refinement_iterations'],
                    "errors": final_state['errors'],
                    "thread_id": config["configurable"]["thread_id"]
                }
            }
            
        except Exception as e:
            print(f"❌ Erro no workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resume(self, thread_id: str, approval_status: str, feedback: str = None) -> Dict:
        """
        Retoma workflow pausado após aprovação humana
        
        Args:
            thread_id: ID da thread salva
            approval_status: 'approved', 'rejected', 'needs_revision'
            feedback: Feedback humano opcional
        
        Returns:
            Resultado atualizado
        """
        
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        print(f"\n🔄 Retomando workflow: {thread_id}")
        print(f"   Status: {approval_status}")
        if feedback:
            print(f"   Feedback: {feedback[:100]}...")
        
        # Atualizar estado com aprovação
        # (simplificado - em produção usar update_state do LangGraph)
        current_state = self.graph.get_state(config)
        current_state.values['approval_status'] = approval_status
        if feedback:
            current_state.values['human_feedback'] = feedback
        
        # Continuar execução
        result = self.graph.invoke(None, config)
        
        return {
            "success": result.get('current_step') == 'completed',
            "status": result.get('approval_status'),
            "metadata": {
                "thread_id": thread_id,
                "resumed": True
            }
        }
