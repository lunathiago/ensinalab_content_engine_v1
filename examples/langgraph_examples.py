"""
Exemplos práticos de uso dos LangGraph Workflows
"""

# =============================================================================
# EXEMPLO 1: Multi-Agent Briefing Analysis
# =============================================================================

def exemplo_multi_agent():
    """Gera opções de conteúdo usando pipeline multi-agent"""
    from src.workflows.briefing_workflow import BriefingAnalysisWorkflow
    
    # Input: Briefing do gestor escolar
    briefing_data = {
        'title': 'Metodologias Ativas em Sala de Aula',
        'description': 'Capacitação sobre implementação de metodologias ativas para engajar alunos',
        'target_audience': 'Professores de Ensino Médio',
        'subject_area': 'Metodologias de Ensino',
        'teacher_experience_level': 'iniciante',
        'training_goal': 'Aprender a implementar aprendizagem baseada em projetos e rotação por estações',
        'duration_minutes': 12,
        'tone': 'inspirador e prático'
    }
    
    # Executar workflow
    workflow = BriefingAnalysisWorkflow()
    result = workflow.run(briefing_data)
    
    # Output: Opções ranqueadas
    print(f"✅ {len(result['ranked_options'])} opções geradas")
    
    for i, option in enumerate(result['ranked_options'], 1):
        print(f"\n📌 Opção {i}:")
        print(f"   Título: {option['title']}")
        print(f"   Score: {option['score']:.2f}")
        print(f"   Resumo: {option['summary'][:100]}...")
        print(f"   Duração estimada: {option['estimated_duration']} min")
    
    return result


# =============================================================================
# EXEMPLO 2: Video Generation State Machine com Human-in-the-Loop
# =============================================================================

def exemplo_video_com_aprovacao():
    """Gera vídeo com pausa para aprovação humana"""
    from src.workflows.video_workflow import VideoGenerationWorkflow
    
    # Input: Roteiro selecionado
    input_data = {
        "script_outline": """
        1. INTRODUÇÃO (2 min)
           - Desafios do ensino tradicional
           - Por que metodologias ativas?
        
        2. APRENDIZAGEM BASEADA EM PROJETOS (4 min)
           - Conceito e benefícios
           - Passo a passo para implementar
           - Exemplo prático: Projeto sobre sustentabilidade
        
        3. ROTAÇÃO POR ESTAÇÕES (4 min)
           - Como organizar a sala
           - Tipos de estações (digital, escrita, colaborativa)
           - Gestão do tempo e transições
        
        4. CONCLUSÃO (2 min)
           - Primeiros passos
           - Recursos adicionais
        """,
        "briefing": {
            'target_audience': 'Professores de Ensino Médio',
            'subject_area': 'Metodologias de Ensino',
            'duration_minutes': 12,
            'tone': 'inspirador',
            'title': 'Metodologias Ativas na Prática'
        },
        "video_id": 123
    }
    
    # Executar workflow (vai pausar para aprovação)
    workflow = VideoGenerationWorkflow()
    result = workflow.run(input_data, video_id=123)
    
    if result['status'] == 'awaiting_approval':
        print("⏸️  Vídeo aguardando aprovação humana")
        print(f"   Checkpoint ID: {result['checkpoint_id']}")
        print(f"   Preview: {result.get('preview_path')}")
        
        # Simular aprovação humana (na prática, via API)
        print("\n👤 Gestor aprova o vídeo...")
        
        # Retomar workflow
        final_result = workflow.resume(
            checkpoint_id=result['checkpoint_id'],
            approved=True
        )
        
        print(f"\n✅ Vídeo finalizado!")
        print(f"   Path: {final_result['file_path']}")
        print(f"   Duração: {final_result['duration']}s")
    
    return result


# =============================================================================
# EXEMPLO 3: Rejeitar e Revisar com Feedback
# =============================================================================

def exemplo_video_com_revisao():
    """Rejeita vídeo e solicita revisão com feedback"""
    from src.workflows.video_workflow import VideoGenerationWorkflow
    
    # Workflow já executado até await_approval
    checkpoint_id = "video_123"
    
    # Gestor rejeita e dá feedback
    feedback = """
    O conteúdo está bom, mas precisa:
    - Adicionar mais exemplos práticos concretos
    - Incluir dicas de gestão de tempo
    - Melhorar a transição entre os tópicos
    - Tornar a conclusão mais acionável
    """
    
    workflow = VideoGenerationWorkflow()
    
    # Retomar com rejection e feedback
    result = workflow.resume(
        checkpoint_id=checkpoint_id,
        approved=False,
        feedback=feedback
    )
    
    print("🔄 Vídeo sendo revisado com feedback...")
    print(f"   → Workflow voltou para enhance_script")
    print(f"   → Aplicando melhorias solicitadas")
    print(f"   → Regenerando áudio e vídeo")
    
    # Vai pausar novamente para nova aprovação
    if result['status'] == 'awaiting_approval':
        print("\n⏸️  Nova versão pronta para revisão")
    
    return result


# =============================================================================
# EXEMPLO 4: Content Refinement - Melhorar Script
# =============================================================================

def exemplo_refinamento():
    """Refina roteiro iterativamente até qualidade adequada"""
    from src.workflows.refinement_workflow import ContentRefinementWorkflow
    
    # Script inicial (qualidade baixa)
    script_inicial = """
    Vamos falar sobre metodologias ativas.
    
    Primeiro, aprendizagem baseada em projetos.
    Os alunos fazem projetos.
    É interessante.
    
    Depois, rotação por estações.
    Divide a sala em grupos.
    Cada grupo faz atividade diferente.
    
    No final, os professores devem implementar.
    """
    
    # Executar refinamento
    workflow = ContentRefinementWorkflow()
    result = workflow.run(
        content=script_inicial,
        content_type="script",
        target_quality=0.85,
        max_iterations=5
    )
    
    print("🔧 REFINAMENTO CONCLUÍDO")
    print(f"   Iterações: {result['metadata']['iterations']}")
    print(f"   Qualidade inicial: {result['metadata']['quality_progression'][0]:.2f}")
    print(f"   Qualidade final: {result['quality']:.2f}")
    print(f"   Razão: {result['metadata']['reason']}")
    
    print("\n📊 Progressão da qualidade:")
    for i, score in enumerate(result['metadata']['quality_progression'], 1):
        bar = "█" * int(score * 20)
        print(f"   Iteração {i}: {bar} {score:.2f}")
    
    print("\n📝 Script refinado:")
    print(result['content'])
    
    return result


# =============================================================================
# EXEMPLO 5: Integração com Celery (Assíncrono)
# =============================================================================

def exemplo_celery_integration():
    """Usa workflows via Celery tasks"""
    from src.workers.tasks import generate_options, generate_video, refine_content
    
    # 1. Gerar opções (multi-agent)
    print("1️⃣ Disparando task de geração de opções...")
    task1 = generate_options.delay(briefing_id=1)
    print(f"   Task ID: {task1.id}")
    
    # Aguardar conclusão
    result1 = task1.get(timeout=120)
    print(f"   ✅ {result1['options_count']} opções geradas")
    
    # 2. Gerar vídeo (state machine)
    print("\n2️⃣ Disparando task de geração de vídeo...")
    task2 = generate_video.delay(video_id=1)
    print(f"   Task ID: {task2.id}")
    
    # Vai pausar em pending_approval
    result2 = task2.get(timeout=300)
    
    if result2['status'] == 'awaiting_approval':
        print(f"   ⏸️  Aguardando aprovação (checkpoint: {result2['checkpoint_id']})")
        
        # Aprovar via API ou task
        from src.workers.tasks import resume_video_generation
        task3 = resume_video_generation.delay(video_id=1, approved=True)
        result3 = task3.get(timeout=180)
        print(f"   ✅ Vídeo finalizado: {result3['file_path']}")
    
    # 3. Refinar conteúdo
    print("\n3️⃣ Disparando task de refinamento...")
    task4 = refine_content.delay(
        content="Script inicial...",
        content_type="script",
        target_quality=0.85
    )
    result4 = task4.get(timeout=180)
    print(f"   ✅ Qualidade: {result4['quality']:.2f} ({result4['metadata']['iterations']} iterações)")
    
    return result1, result2, result4


# =============================================================================
# EXEMPLO 6: Fluxo Completo End-to-End
# =============================================================================

def exemplo_fluxo_completo():
    """Fluxo completo: briefing → opções → seleção → vídeo → aprovação"""
    
    print("="*80)
    print("🎯 FLUXO COMPLETO DE GERAÇÃO DE VÍDEO DE TREINAMENTO")
    print("="*80)
    
    # Passo 1: Gestor cria briefing
    print("\n📋 PASSO 1: Gestor cria briefing")
    briefing = {
        'title': 'Avaliação Formativa - Práticas Eficazes',
        'description': 'Como usar avaliação formativa para melhorar aprendizado',
        'target_audience': 'Professores do Fundamental II',
        'subject_area': 'Avaliação',
        'teacher_experience_level': 'intermediário',
        'training_goal': 'Implementar técnicas de avaliação formativa no dia a dia',
        'duration_minutes': 10,
        'tone': 'prático e encorajador'
    }
    print(f"   ✓ Briefing criado: {briefing['title']}")
    
    # Passo 2: Sistema gera opções (multi-agent)
    print("\n🤖 PASSO 2: Sistema gera opções (multi-agent workflow)")
    from src.workflows.briefing_workflow import BriefingAnalysisWorkflow
    
    workflow1 = BriefingAnalysisWorkflow()
    opcoes_result = workflow1.run(briefing)
    print(f"   ✓ {len(opcoes_result['ranked_options'])} opções geradas")
    
    # Passo 3: Gestor seleciona opção
    print("\n👤 PASSO 3: Gestor seleciona melhor opção")
    opcao_selecionada = opcoes_result['ranked_options'][0]
    print(f"   ✓ Selecionada: {opcao_selecionada['title']}")
    print(f"   ✓ Score: {opcao_selecionada['score']:.2f}")
    
    # Passo 4: Sistema gera vídeo (state machine)
    print("\n🎬 PASSO 4: Sistema gera vídeo (state machine workflow)")
    from src.workflows.video_workflow import VideoGenerationWorkflow
    
    video_input = {
        "script_outline": opcao_selecionada['script_outline'],
        "briefing": briefing,
        "video_id": 999
    }
    
    workflow2 = VideoGenerationWorkflow()
    video_result = workflow2.run(video_input, video_id=999)
    
    # Passo 5: Sistema pausa para aprovação
    if video_result['status'] == 'awaiting_approval':
        print("\n⏸️  PASSO 5: Vídeo aguardando aprovação")
        print(f"   ✓ Preview disponível: {video_result.get('preview_path')}")
        
        # Passo 6: Gestor aprova
        print("\n✅ PASSO 6: Gestor aprova vídeo")
        final_result = workflow2.resume(
            checkpoint_id=video_result['checkpoint_id'],
            approved=True
        )
        
        print(f"   ✓ Vídeo finalizado!")
        print(f"   ✓ Arquivo: {final_result['file_path']}")
        print(f"   ✓ Duração: {final_result['duration']}s")
    
    print("\n" + "="*80)
    print("🎉 FLUXO COMPLETO FINALIZADO COM SUCESSO!")
    print("="*80)
    
    return final_result


# =============================================================================
# EXECUTAR EXEMPLOS
# =============================================================================

if __name__ == "__main__":
    import os
    
    # Verificar API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY não configurada!")
        print("   Configure antes: export OPENAI_API_KEY=your_key")
        exit(1)
    
    # Menu de exemplos
    print("\n" + "="*80)
    print("📚 EXEMPLOS DE LANGGRAPH WORKFLOWS")
    print("="*80)
    print("\nEscolha um exemplo:")
    print("  1. Multi-Agent Briefing Analysis")
    print("  2. Video Generation com Aprovação")
    print("  3. Rejeição e Revisão com Feedback")
    print("  4. Content Refinement Iterativo")
    print("  5. Integração com Celery")
    print("  6. Fluxo Completo End-to-End")
    print("  0. Sair")
    
    escolha = input("\nDigite o número: ")
    
    exemplos = {
        '1': exemplo_multi_agent,
        '2': exemplo_video_com_aprovacao,
        '3': exemplo_video_com_revisao,
        '4': exemplo_refinamento,
        '5': exemplo_celery_integration,
        '6': exemplo_fluxo_completo
    }
    
    if escolha in exemplos:
        print("\n" + "="*80)
        exemplos[escolha]()
    elif escolha == '0':
        print("👋 Até logo!")
    else:
        print("❌ Opção inválida")
