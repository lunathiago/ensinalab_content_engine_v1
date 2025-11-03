# EnsinaLab Content Engine 🎓🎬

Motor de conteúdos inteligente para gestores escolares - gera vídeos de treinamento/capacitação de professores personalizados a partir de briefings simplificados.

## 📋 Visão Geral

O EnsinaLab Content Engine é um sistema backend que:

1. **Recebe briefings simplificados** de gestores escolares sobre necessidades de capacitação docente
2. **Processa e filtra** usando IA (LLM + filtros de relevância e qualidade)
3. **Gera múltiplas opções** de conteúdo de treinamento para professores
4. **Produz vídeos curtos de capacitação** após aprovação do gestor
5. **Entrega conteúdo pronto** para desenvolvimento profissional dos professores

## 🏗️ Arquitetura

```
┌─────────────┐
│   Gestor    │ → Envia briefing
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────┐
│           FastAPI (Backend)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Briefing │→ │  Options │→ │  Videos  │  │
│  │   API    │  │   API    │  │   API    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────┬─────────────────────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
┌──────▼──────┐          ┌──────▼──────┐
│   LLM/RAG   │          │   Celery    │
│  (OpenAI)   │          │   Workers   │
│             │          │             │
│ • Gera      │          │ • TTS       │
│   opções    │          │ • MoviePy   │
│ • Filtra    │          │ • FFmpeg    │
│ • Score     │          │             │
└─────────────┘          └─────────────┘
       │                         │
       └────────────┬────────────┘
                    ↓
           ┌────────────────┐
           │   PostgreSQL   │
           │     + Redis    │
           └────────────────┘
```

## 🚀 Setup Rápido

### Pré-requisitos

- Python 3.9+
- PostgreSQL
- Redis
- FFmpeg

### 1. Clone e instale dependências

```bash
# Clone o repositório
git clone <repository-url>
cd ensinalab_content_engine_v1

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env com suas credenciais
nano .env
```

**Variáveis essenciais:**
- `OPENAI_API_KEY`: Sua chave da API OpenAI
- `DB_PASSWORD`: Senha do PostgreSQL
- Demais configurações conforme necessário

### 3. Configure banco de dados

```bash
# Crie o banco de dados
createdb ensinalab_content

# Execute migrações (se houver)
# alembic upgrade head
```

### 4. Inicie os serviços

**Terminal 1 - API:**
```bash
python -m src.main
```

**Terminal 2 - Celery Worker:**
```bash
celery -A src.workers.celery_config worker --loglevel=info
```

**Terminal 3 - Redis (se não estiver rodando como serviço):**
```bash
redis-server
```

### 5. Acesse a documentação

Abra no navegador: **http://localhost:8000/docs**

## 📁 Estrutura do Projeto

```
ensinalab_content_engine_v1/
├── src/
│   ├── main.py              # Entry point
│   ├── app.py               # FastAPI app
│   │
│   ├── api/                 # Rotas da API
│   │   └── routes/
│   │       ├── briefings.py
│   │       ├── options.py
│   │       ├── videos.py
│   │       └── health.py
│   │
│   ├── services/            # Lógica de negócio
│   │   ├── briefing_service.py
│   │   ├── option_service.py
│   │   └── video_service.py
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── briefing.py
│   │   ├── option.py
│   │   └── video.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── briefing.py
│   │   ├── option.py
│   │   └── video.py
│   │
│   ├── workers/             # Celery tasks
│   │   ├── celery_config.py
│   │   └── tasks.py
│   │
│   ├── ml/                  # Machine Learning
│   │   ├── llm_service.py   # OpenAI integration
│   │   └── filters.py       # Content filters
│   │
│   ├── video/               # Geração de vídeo
│   │   ├── generator.py     # MoviePy
│   │   └── tts.py           # Text-to-Speech
│   │
│   ├── config/              # Configurações
│   │   ├── settings.py      # Pydantic Settings
│   │   └── database.py      # SQLAlchemy setup
│   │
│   └── utils/               # Utilitários
│       ├── logger.py
│       └── validators.py
│
├── tests/                   # Testes
├── requirements.txt         # Dependências
├── pyproject.toml          # Configuração do projeto
├── .env.example            # Template de variáveis
├── .gitignore
└── README.md
```

## 🔄 Fluxo de Uso

### 1️⃣ Criar Briefing

```bash
POST /api/v1/briefings
{
  "title": "Gestão de Sala de Aula - Técnicas Práticas",
  "description": "Vídeo de capacitação sobre técnicas eficazes de gestão de sala para professores iniciantes",
  "target_audience": "Professores Iniciantes",
  "subject_area": "Gestão de Sala",
  "teacher_experience_level": "Iniciante",
  "training_goal": "Desenvolver habilidades de gestão comportamental e organização da sala de aula",
  "duration_minutes": 5,
  "tone": "prático"
}
```

### 2️⃣ Motor Gera Opções (automático via Celery)

O sistema:
- Usa LLM (GPT-4) para gerar 3-5 opções diferentes
- Aplica filtros de segurança e relevância
- Calcula scores de qualidade
- Armazena opções no banco

### 3️⃣ Listar Opções

```bash
GET /api/v1/briefings/{briefing_id}/options
```

Retorna:
```json
[
  {
    "id": 1,
    "title": "5 Técnicas Imediatas para Gestão de Sala",
    "summary": "Vídeo prático com estratégias comprovadas para estabelecer rotinas e manter o engajamento dos alunos...",
    "relevance_score": 0.92,
    "quality_score": 0.88
  },
  ...
]
```

### 4️⃣ Selecionar Opção

```bash
POST /api/v1/options/{option_id}/select
{
  "notes": "Perfeito! Pode gerar."
}
```

### 5️⃣ Vídeo é Gerado (automático via Celery)

O worker:
- Aprimora o roteiro com LLM
- Converte texto em áudio (TTS)
- Gera vídeo com MoviePy + FFmpeg
- Salva arquivo MP4

### 6️⃣ Baixar Vídeo

```bash
GET /api/v1/videos/{video_id}/download
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=src tests/
```

## 🔧 Tecnologias Utilizadas

### Backend & API
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Celery**: Processamento assíncrono
- **Redis**: Message broker e cache
- **Pydantic**: Validação de dados

### IA & Machine Learning
- **OpenAI GPT-4**: Geração de conteúdo
- **LangGraph**: Workflows multi-agent e state machines
- **LangChain**: Framework de IA para LLMs
- **LangSmith**: Observabilidade e debugging (opcional)

### Geração de Vídeo
- **MoviePy**: Geração de vídeos
- **FFmpeg**: Processamento de mídia
- **Text-to-Speech**: Conversão texto-áudio

## 🤖 LangGraph Workflows

Este projeto utiliza **4 workflows avançados** com LangGraph:

### 1. Multi-Agent Briefing Analysis
Pipeline com 4 agentes especializados:
- **Analyzer**: Analisa briefing e extrai intenções
- **Generator**: Gera 3-5 opções criativas
- **Filter**: Aplica filtros de qualidade e segurança
- **Ranker**: Ranqueia por relevância

```python
Analyzer → Generator → Filter → Ranker
```

### 2. Video Generation State Machine
Máquina de estados com 7 estados e checkpointing:
- Analyze → Enhance → Generate Audio → Generate Video
- Review → Await Approval → Finalize

```python
# Suporta pausar e retomar
workflow.run(data, video_id=123)
workflow.resume(checkpoint_id, approved=True)
```

### 3. Human-in-the-Loop
Sistema de aprovação humana com persistência:
- Workflow pausa em pontos estratégicos
- Estado salvo em SQLite (checkpointing)
- API permite aprovar/rejeitar vídeos
- Retomada automática após decisão

**Endpoints:**
- `POST /api/v1/videos/{id}/approve` - Aprova vídeo
- `POST /api/v1/videos/{id}/reject` - Rejeita com feedback

### 4. Iterative Content Refinement
Ciclo automático de melhoria:
- Avalia qualidade (0-1)
- Refina conteúdo baseado em feedback
- Repete até atingir qualidade alvo
- Máximo de 5 iterações

```
Evaluate → (quality OK?) → Complete
    ↑            ↓ No
    └───── Refine
```

**📖 Veja documentação completa:** [LANGGRAPH_WORKFLOWS.md](./LANGGRAPH_WORKFLOWS.md)

## 📊 Endpoints Principais

### Health
- `GET /health` - Verifica status da API

### Briefings
- `POST /api/v1/briefings` - Criar briefing
- `GET /api/v1/briefings` - Listar briefings
- `GET /api/v1/briefings/{id}` - Obter briefing
- `DELETE /api/v1/briefings/{id}` - Deletar briefing

### Options
- `GET /api/v1/briefings/{id}/options` - Listar opções
- `POST /api/v1/options/{id}/select` - Selecionar opção

### Videos
- `GET /api/v1/videos` - Listar vídeos
- `GET /api/v1/videos/{id}` - Obter vídeo
- `GET /api/v1/videos/{id}/download` - Baixar vídeo
- `GET /api/v1/videos/{id}/status` - Status de geração

## 🔐 Segurança

- Filtros de conteúdo impróprio
- Validação de entrada com Pydantic
- Variáveis sensíveis em `.env` (nunca commitar)
- CORS configurável
- Rate limiting (TODO)

## 📝 TODO / Próximos Passos

- [ ] Autenticação JWT para gestores
- [ ] RAG com base de conhecimento educacional (BNCC)
- [ ] Integração com TTS real (ElevenLabs/Polly)
- [ ] Templates visuais customizáveis
- [ ] Dashboard de métricas
- [ ] Webhooks para notificar conclusão
- [ ] Testes unitários completos
- [ ] CI/CD pipeline
- [ ] Dockerização
- [ ] Deploy Kubernetes

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

[Definir licença]

## 👥 Equipe

EnsinaLab Team

---

**Documentação da API:** http://localhost:8000/docs

**Precisa de ajuda?** Abra uma issue no GitHub.