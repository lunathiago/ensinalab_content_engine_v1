# LangGraph Workflows - Guia Completo

## Visão Geral

Este projeto utiliza **LangGraph** para implementar 4 workflows sofisticados de IA:

1. **Multi-Agent Briefing Analysis** - Pipeline com 4 agentes especializados
2. **Video Generation State Machine** - Máquina de estados com 7 estados
3. **Human-in-the-Loop** - Aprovação humana com checkpointing
4. **Iterative Content Refinement** - Ciclo de melhoria automática

---

## 1. Multi-Agent Briefing Analysis

**Arquivo:** `src/workflows/briefing_workflow.py`

### Pipeline de 4 Agentes

```
Analyzer → Generator → Filter → Ranker
```

#### Agente 1: Analyzer
- **Função:** Analisa o briefing e extrai intenções
- **Output:** Keywords, temas, contexto
- **Temperatura:** 0.3 (preciso)

#### Agente 2: Generator
- **Função:** Gera 3-5 opções diversas de conteúdo
- **Output:** Títulos, descrições, roteiros
- **Temperatura:** 0.8 (criativo)

#### Agente 3: Filter
- **Função:** Filtra por segurança e qualidade
- **Output:** Opções aprovadas com scores
- **Temperatura:** 0.1 (rigoroso)

#### Agente 4: Ranker
- **Função:** Ranqueia por relevância e alinhamento
- **Output:** Lista ordenada de opções
- **Temperatura:** 0.2 (objetivo)

### Uso

```python
from src.workflows.briefing_workflow import BriefingAnalysisWorkflow

workflow = BriefingAnalysisWorkflow()
result = workflow.run({
    'title': 'Gestão de Conflitos',
    'description': 'Como mediar conflitos entre alunos',
    'target_audience': 'Professores de Ensino Fundamental',
    'subject_area': 'Gestão de Sala de Aula',
    'teacher_experience_level': 'intermediário',
    'training_goal': 'Desenvolver habilidades de mediação',
    'duration_minutes': 10,
    'tone': 'empático'
})

# result contém:
# - ranked_options: Lista de opções ordenadas
# - metadata: Estatísticas do pipeline
```

### Integração com Celery

```python
# Task automática
@celery_app.task
def generate_options(briefing_id: int):
    workflow = BriefingAnalysisWorkflow()
    result = workflow.run(briefing_data)
    # Salva opções no banco
```

---

## 2. Video Generation State Machine

**Arquivo:** `src/workflows/video_workflow.py`

### Máquina de Estados (7 Estados)

```
analyze_script → enhance_script → generate_audio → generate_video
                     ↑                                    ↓
                     └──── await_approval ←──── review ──┘
                                  ↓
                             finalize
```

#### Estado 1: analyze_script
- Analisa roteiro inicial
- Identifica estrutura e temas

#### Estado 2: enhance_script
- Expande roteiro com GPT-4
- Adiciona narrativa e transições

#### Estado 3: generate_audio
- Text-to-Speech
- Gera áudio narrado

#### Estado 4: generate_video
- Combina áudio + visual
- Gera MP4 final

#### Estado 5: review
- Avaliação automática de qualidade
- Score de 0 a 1

#### Estado 6: await_approval ⏸️
- **PAUSA para aprovação humana**
- Checkpoint salvo no SQLite
- Aguarda decisão externa

#### Estado 7: finalize
- Upload de arquivo
- Atualização de status
- Conclusão

### Checkpointing

O workflow usa **SqliteSaver** para persistir estado:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string(
    f"sqlite:///{checkpoint_path}/video_{video_id}.db"
)

workflow = VideoGenerationWorkflow()
result = workflow.run(input_data, video_id=123)

# Se result['status'] == 'awaiting_approval':
#   → Workflow pausado, checkpoint salvo
```

### Retomada após Aprovação

```python
# Aprovar
workflow.resume(
    checkpoint_id="video_123",
    approved=True
)

# Rejeitar com feedback
workflow.resume(
    checkpoint_id="video_123",
    approved=False,
    feedback="Melhorar introdução"
)
```

### Uso

```python
from src.workflows.video_workflow import VideoGenerationWorkflow

workflow = VideoGenerationWorkflow()
result = workflow.run({
    "script_outline": "1. Introdução\n2. Conceitos...",
    "briefing": {...},
    "video_id": 123
}, video_id=123)

if result['status'] == 'awaiting_approval':
    # Pausado - aguardar humano
    checkpoint_id = result['checkpoint_id']
    
    # Depois...
    final = workflow.resume(checkpoint_id, approved=True)
```

---

## 3. Human-in-the-Loop

### Endpoints de API

#### POST /api/v1/videos/{video_id}/approve

Aprova o vídeo e retoma geração:

```bash
curl -X POST http://localhost:8000/api/v1/videos/123/approve
```

Resposta:
```json
{
  "video_id": 123,
  "message": "Vídeo aprovado. Retomando geração...",
  "task_id": "abc-123"
}
```

#### POST /api/v1/videos/{video_id}/reject

Rejeita e solicita revisão:

```bash
curl -X POST http://localhost:8000/api/v1/videos/123/reject \
  -H "Content-Type: application/json" \
  -d '{"feedback": "Melhorar introdução e adicionar exemplos práticos"}'
```

Resposta:
```json
{
  "video_id": 123,
  "message": "Vídeo rejeitado. Aplicando feedback e regenerando...",
  "task_id": "def-456",
  "feedback": "Melhorar introdução..."
}
```

### Status do Vídeo

```bash
GET /api/v1/videos/123/status
```

Resposta:
```json
{
  "video_id": 123,
  "status": "pending_approval",
  "progress": 0.8,
  "awaiting_approval": true
}
```

### Fluxo Completo

1. **Usuário cria briefing** → POST /api/v1/briefings
2. **Sistema gera opções** → Task automática (multi-agent)
3. **Usuário seleciona opção** → POST /api/v1/options/{id}/generate_video
4. **Workflow de vídeo inicia** → State machine
5. **Workflow pausa em review** → Status: pending_approval
6. **Usuário aprova/rejeita** → POST /api/v1/videos/{id}/approve ou /reject
7. **Workflow retoma** → Finaliza ou refaz
8. **Vídeo pronto** → Status: completed

---

## 4. Iterative Content Refinement

**Arquivo:** `src/workflows/refinement_workflow.py`

### Ciclo de Refinamento

```
Evaluate → (quality OK?) → Complete
    ↑            ↓ No
    └───── Refine
```

### Parâmetros

- **target_quality:** 0.85 (qualidade alvo)
- **max_iterations:** 5 (máximo de ciclos)
- **convergence_threshold:** 0.02 (melhoria mínima)

### Dimensões de Qualidade

1. **Clareza:** Texto objetivo e compreensível
2. **Relevância:** Alinhamento com objetivo
3. **Estrutura:** Organização lógica
4. **Aplicabilidade:** Práticas concretas
5. **Linguagem:** Adequação ao público

### Uso

```python
from src.workflows.refinement_workflow import ContentRefinementWorkflow

workflow = ContentRefinementWorkflow()
result = workflow.run(
    content="Script inicial...",
    content_type="script",
    target_quality=0.85,
    max_iterations=5
)

# result contém:
# - content: Versão refinada
# - quality: Score final (0-1)
# - metadata.iterations: Número de ciclos
# - metadata.quality_progression: [0.7, 0.78, 0.85]
```

### Integração com Celery

```python
from src.workers.tasks import refine_content

# Task assíncrona
task = refine_content.delay(
    content="Roteiro inicial...",
    content_type="script",
    target_quality=0.85
)

result = task.get()  # Aguarda conclusão
refined_script = result['content']
```

---

## Configuração

**Arquivo:** `src/config/workflows.py`

```python
VIDEO_WORKFLOW_CONFIG = {
    "checkpoint_dir": Path("/tmp/langgraph_checkpoints/video_generation"),
    "max_retries": 3,
    "review_threshold": 0.7,
    "require_human_approval": True
}

BRIEFING_WORKFLOW_CONFIG = {
    "num_options": 5,
    "filter_threshold": 0.6,
    "temperature": {
        "analyzer": 0.3,
        "generator": 0.8,
        "filter": 0.1,
        "ranker": 0.2
    }
}

REFINEMENT_WORKFLOW_CONFIG = {
    "target_quality": 0.85,
    "max_iterations": 5,
    "convergence_threshold": 0.02
}
```

---

## LangSmith Tracing (Opcional)

Para debugging e observabilidade:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=your_api_key
export LANGSMITH_PROJECT=ensinalab-content-engine
```

Ver traces em: https://smith.langchain.com/

---

## Dependências

```txt
langgraph==0.0.26
langsmith==0.0.77
langchain==0.1.0
langchain-core==0.1.10
langchain-openai==0.0.2
```

---

## Arquitetura de Arquivos

```
src/workflows/
├── __init__.py
├── states.py                    # TypedDict para estados
├── briefing_agents.py           # 4 agentes especializados
├── briefing_workflow.py         # Multi-agent pipeline
├── video_workflow.py            # State machine com 7 estados
└── refinement_workflow.py       # Ciclo de refinamento

src/workers/
└── tasks.py                     # Integração Celery + LangGraph

src/api/routes/
└── videos.py                    # Endpoints de aprovação

src/config/
└── workflows.py                 # Configurações centralizadas
```

---

## Testes

### Testar Multi-Agent Workflow

```python
from src.workflows.briefing_workflow import BriefingAnalysisWorkflow

workflow = BriefingAnalysisWorkflow()
result = workflow.run({
    'title': 'Teste',
    'description': 'Conteúdo de teste',
    'target_audience': 'Professores',
    'subject_area': 'Pedagogia',
    'teacher_experience_level': 'iniciante',
    'training_goal': 'Aprender',
    'duration_minutes': 5,
    'tone': 'objetivo'
})

print(f"Opções geradas: {len(result['ranked_options'])}")
```

### Testar State Machine

```python
from src.workflows.video_workflow import VideoGenerationWorkflow

workflow = VideoGenerationWorkflow()
result = workflow.run({
    "script_outline": "1. Intro\n2. Conteúdo",
    "briefing": {'tone': 'empático'},
    "video_id": 999
}, video_id=999)

print(f"Status: {result['status']}")
```

### Testar Refinamento

```python
from src.workflows.refinement_workflow import ContentRefinementWorkflow

workflow = ContentRefinementWorkflow()
result = workflow.run(
    content="Texto simples para refinar",
    content_type="script",
    target_quality=0.8
)

print(f"Qualidade final: {result['quality']:.2f}")
print(f"Iterações: {result['metadata']['iterations']}")
```

---

## Troubleshooting

### Checkpoint não encontrado

```python
# Verificar se diretório existe
from src.config.workflows import VIDEO_WORKFLOW_CONFIG
print(VIDEO_WORKFLOW_CONFIG["checkpoint_dir"])

# Listar checkpoints
import os
os.listdir(VIDEO_WORKFLOW_CONFIG["checkpoint_dir"])
```

### Workflow travado

```python
# Limpar checkpoints antigos
import shutil
shutil.rmtree("/tmp/langgraph_checkpoints/video_generation")
```

### Qualidade não converge

- Aumentar `max_iterations`
- Reduzir `target_quality`
- Ajustar `convergence_threshold`

---

## Próximos Passos

1. ✅ Multi-agent workflow implementado
2. ✅ State machine com checkpointing
3. ✅ Human-in-the-loop com API
4. ✅ Refinement cycle workflow
5. 🔜 Testes unitários para workflows
6. 🔜 Dashboard para monitorar workflows
7. 🔜 Métricas de qualidade personalizadas

---

## Referências

- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Multi-Agent Systems](https://python.langchain.com/docs/use_cases/agents)
- [Human-in-the-Loop](https://python.langchain.com/docs/langgraph/how-tos/human_in_the_loop)
- [Checkpointing](https://python.langchain.com/docs/langgraph/how-tos/persistence)
