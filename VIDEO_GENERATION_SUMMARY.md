# 🎬 Video Generation Implementation - Summary

## ✅ O Que Foi Implementado

### 1. **Sistema de 3 Geradores** (Factory Pattern)

#### 🎯 Simple Generator (`src/video/simple_generator.py`)
- **Funcionalidade**: TTS + slides estáticos (PIL)
- **Custo**: ~$0.05-0.30/min
- **Velocidade**: 2-5 min
- **TTS Providers**: Google Cloud, ElevenLabs, Amazon Polly, Azure Speech
- **Características**:
  - Parse de roteiro em 5-7 seções
  - Slides 1920x1080 com gradientes e branding
  - Transições crossfade
  - Fallback chain entre providers TTS
  - Gera silêncio com pydub se todos TTS falharem

#### 👤 Avatar Generator (`src/video/avatar_generator.py`)
- **Funcionalidade**: Virtual presenters via API
- **Custo**: ~$3-10/min
- **Velocidade**: 5-15 min
- **Providers**: HeyGen, D-ID
- **Características**:
  - Polling automático (60 tentativas)
  - Download com streaming
  - Suporte para 100+ avatares
  - Vozes naturais em PT-BR
  - Thumbnails automáticos

#### 🎨 AI Generator (`src/video/ai_generator.py`)
- **Funcionalidade**: Text-to-video cinematográfico
- **Custo**: ~$30-100/min
- **Velocidade**: 20-60 min
- **Providers**: Kling AI, Runway Gen-3
- **Características**:
  - LLM parse de cenas visuais
  - Prompt engineering automático
  - Geração paralela de cenas
  - Concatenação com MoviePy
  - Polling robusto (120 tentativas)

### 2. **Factory Pattern** (`src/video/factory.py`)

```python
# Seleção manual
generator = VideoGeneratorFactory.create('simple', provider='google')

# Recomendação inteligente
rec = VideoGeneratorFactory.recommend_generator(
    budget_usd=10.0,
    urgency='normal',
    quality_level='high'
)

# Seleção por briefing
config = video_config.get_generator_for_briefing(briefing_data)
generator = VideoGeneratorFactory.create(**config)
```

**Características**:
- Registry de geradores
- Metadata (custos, velocidades, casos de uso)
- Sistema de recomendação
- Atalhos: `create_simple_generator()`, etc.

### 3. **Multi-Provider TTS** (`src/video/tts.py` - REESCRITO)

**Antes**:
```python
# TTS simples sem fallback
audio = tts.generate_audio(text)
```

**Depois**:
```python
# Multi-provider com fallback chain
tts = TTSService(provider='google')  # ou elevenlabs, amazon, azure
audio = tts.generate(text, voice='pt-BR-FranciscaNeural')

# Fallback automático:
# Google → ElevenLabs → Amazon → Azure → Silêncio (pydub)
```

### 4. **Workflow Integration** (`src/workflows/video_workflow.py`)

**Antes**:
```python
workflow = VideoGenerationWorkflow()
```

**Depois**:
```python
# Com seleção de gerador
workflow = VideoGenerationWorkflow(
    generator_type='avatar',  # simple, avatar, ai
    provider='heygen'
)

# Metadata passada para geradores
result = workflow.run(input_data, video_id=123)
```

### 5. **Configuration System** (`src/config/video_config.py`)

```python
class VideoGeneratorConfig:
    # Ambientes
    ENVIRONMENTS = {
        'development': {'generator_type': 'simple', 'provider': 'google'},
        'staging': {'generator_type': 'simple', 'provider': 'elevenlabs'},
        'production': {'generator_type': 'avatar', 'provider': 'heygen'},
        'premium': {'generator_type': 'ai', 'provider': 'kling'}
    }
    
    # Seleção inteligente por briefing
    @staticmethod
    def get_generator_for_briefing(briefing_data):
        # Lógica: duração, tom, assunto
        # Retorna: {'generator_type': 'avatar', 'provider': 'heygen'}
    
    # Estimativa de custos
    @staticmethod
    def estimate_cost(generator_type, duration_minutes):
        # Retorna: float (USD)
```

### 6. **Task Update** (`src/workers/tasks.py`)

**Mudanças**:
```python
@celery_app.task
def generate_video(self, video_id: int, generator_type: str = None):
    # Auto-detect baseado no briefing
    if not generator_type:
        config = video_config.get_generator_for_briefing(briefing_data)
        generator_type = config['generator_type']
        provider = config.get('provider')
    
    # Instanciar workflow com gerador
    workflow = VideoGenerationWorkflow(
        generator_type=generator_type,
        provider=provider
    )
    
    # Salvar generator_type em metadata
    video.metadata['generator_type'] = generator_type
```

### 7. **Dependencies** (`requirements.txt`)

**Adicionados**:
```txt
# TTS Multi-provider
google-cloud-texttospeech>=2.14.1,<3.0.0
elevenlabs>=0.2.27,<1.0.0
boto3>=1.29.7,<2.0.0
azure-cognitiveservices-speech>=1.31.0,<2.0.0
pydub>=0.25.1,<1.0.0

# HTTP requests (para avatar/AI APIs)
requests>=2.31.0,<3.0.0
```

### 8. **Documentation**

- **VIDEO_GENERATORS.md**: Guia completo (setup, APIs, exemplos, troubleshooting)
- **.env.example**: Todas as variáveis necessárias com comentários
- **VIDEO_GENERATION_SUMMARY.md**: Este arquivo

### 9. **Testing Script** (`scripts/test_video_generators.py`)

```bash
# Testar factory methods
python scripts/test_video_generators.py --generator factory

# Testar simple generator
python scripts/test_video_generators.py --generator simple --provider google

# Testar avatar generator (requer API key)
python scripts/test_video_generators.py --generator avatar --provider did

# Testar tudo
python scripts/test_video_generators.py --generator all
```

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────┐
│   VideoGenerationWorkflow (LangGraph)       │
│   • Analyze → Enhance → Audio → Video      │
│   • Human-in-the-loop checkpointing         │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│   VideoGeneratorFactory                     │
│   • create(type, provider)                  │
│   • recommend_generator(budget, quality)    │
│   • get_generator_for_briefing()            │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴───────┬───────────┐
        ▼               ▼           ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Simple    │  │   Avatar    │  │   AI        │
│  Generator  │  │  Generator  │  │  Generator  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ TTSService  │  │ HeyGen/D-ID │  │ Kling/Runway│
│ Multi-prov. │  │     API     │  │     API     │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 🎯 Como Usar

### 1. **Setup Mínimo (Simple Generator)**

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar Google TTS (free tier)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# 3. Testar
python scripts/test_video_generators.py --generator simple
```

### 2. **Setup Produção (Avatar Generator)**

```bash
# 1. Obter API keys
# HeyGen: https://heygen.com
# D-ID: https://d-id.com

# 2. Configurar
export HEYGEN_API_KEY=your-key
# ou
export DID_API_KEY=your-key

# 3. Configurar ambiente
export ENVIRONMENT=production
export VIDEO_GENERATOR_TYPE=avatar

# 4. Testar
python scripts/test_video_generators.py --generator avatar --provider heygen
```

### 3. **Uso via API**

```bash
# Criar briefing
curl -X POST http://localhost:8000/api/briefings \
  -H "Content-Type: application/json" \
  -d '{
    "target_audience": "Gestores escolares",
    "subject_area": "Liderança",
    "duration_minutes": 5,
    "tone": "professional"
  }'

# Gerar opções (LangGraph multi-agent)
# Sistema retorna 4 opções de roteiro

# Selecionar opção e gerar vídeo
curl -X POST http://localhost:8000/api/videos/{video_id}/generate

# Sistema escolhe gerador automaticamente baseado no briefing:
# - ≤2 min → simple
# - Tom profissional → avatar
# - >15 min → verificar budget
```

### 4. **Uso Programático**

```python
from src.video.factory import VideoGeneratorFactory
from src.config.video_config import video_config

# Opção 1: Seleção manual
generator = VideoGeneratorFactory.create('simple', provider='google')

# Opção 2: Recomendação por budget/qualidade
rec = VideoGeneratorFactory.recommend_generator(
    budget_usd=10.0,
    urgency='normal',
    quality_level='high'
)
generator = VideoGeneratorFactory.create(**rec)

# Opção 3: Seleção automática por briefing
config = video_config.get_generator_for_briefing({
    'duration_minutes': 5,
    'tone': 'professional',
    'subject_area': 'leadership'
})
generator = VideoGeneratorFactory.create(**config)

# Gerar vídeo
result = generator.generate(
    script="Seu roteiro aqui...",
    title="Título do vídeo",
    metadata={'tone': 'professional'},
    video_id=123
)

print(f"Vídeo gerado: {result['file_path']}")
print(f"Duração: {result['duration']}s")
print(f"Custo: ${result['metadata']['estimated_cost_usd']:.2f}")
```

---

## 💰 Tabela de Custos

| Gerador | Provider | Custo/min | Velocidade | Caso de Uso |
|---------|----------|-----------|------------|-------------|
| Simple | Google TTS | $0.05 | ⚡⚡⚡ 2-5 min | Dev, testes, tutoriais simples |
| Simple | ElevenLabs | $0.30 | ⚡⚡⚡ 2-5 min | Produção low-cost, alta qualidade TTS |
| Avatar | D-ID | $3-5 | ⚡⚡ 5-15 min | Produção mid-tier, demos |
| Avatar | HeyGen | $5-10 | ⚡⚡ 5-15 min | Produção premium, treinamentos oficiais |
| AI | Kling AI | $30-50 | 🐌 20-60 min | Marketing, institucional, experimental |
| AI | Runway Gen-3 | $50-100 | 🐌 20-60 min | Conteúdo cinematográfico, alta produção |

**Estimativas para vídeo de 5 minutos**:
- Simple (Google): $0.25
- Simple (ElevenLabs): $1.50
- Avatar (D-ID): $18.00
- Avatar (HeyGen): $37.50
- AI (Kling): $187.50
- AI (Runway): $375.00

---

## 🚀 Próximos Passos

### 1. **Deploy no Render** (PRIORITÁRIO)

```bash
# 1. Atualizar requirements.txt no Git
git add requirements.txt
git commit -m "Add video generation dependencies"
git push

# 2. Configurar env vars no Render
# Dashboard → Environment → Add Variables:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
VIDEO_GENERATOR_TYPE=simple
ENVIRONMENT=production

# 3. Redeploy automático

# 4. Executar migração de DB
# Render Shell:
python -m scripts.add_metadata_column
```

### 2. **Testar Simple Generator**

```bash
# Local primeiro
python scripts/test_video_generators.py --generator simple --provider google

# Via API
curl -X POST http://localhost:8000/api/videos/1/generate
```

### 3. **Setup Avatar Generator** (quando pronto para produção)

```bash
# 1. Obter API keys
# HeyGen: https://app.heygen.com/settings
# D-ID: https://studio.d-id.com/account-settings

# 2. Adicionar no Render
HEYGEN_API_KEY=...
DID_API_KEY=...
VIDEO_GENERATOR_TYPE=avatar

# 3. Testar
python scripts/test_video_generators.py --generator avatar --provider heygen
```

### 4. **Monitoramento e Otimização**

- [ ] Implementar cache de vídeos gerados (evitar regeração)
- [ ] Dashboard de custos (tracking por generator_type)
- [ ] Alertas de budget diário
- [ ] Métricas de tempo de geração
- [ ] Rate limiting por provider

### 5. **Melhorias Futuras**

- [ ] Suporte para legendas (SRT generation)
- [ ] Múltiplas resoluções (1080p, 720p, 480p)
- [ ] Watermark customizável
- [ ] Templates de slides customizáveis
- [ ] Background music (royalty-free)
- [ ] Voiceover com múltiplos speakers
- [ ] Upload direto para YouTube/Vimeo

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'google.cloud'"

```bash
pip install google-cloud-texttospeech
```

### "TTS provider 'google' failed"

```bash
# Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS  # Deve ser JSON válido

# Testar API manualmente
python -c "from google.cloud import texttospeech; client = texttospeech.TextToSpeechClient(); print('OK')"
```

### "Avatar generation timeout"

```bash
# Verificar status do job no provider
# HeyGen:
curl -H "Authorization: Bearer $HEYGEN_API_KEY" \
  https://api.heygen.com/v2/video_status/{video_id}

# Aumentar timeout (default: 10 min)
# Editar src/video/avatar_generator.py:
MAX_POLL_ATTEMPTS = 120  # 20 minutos
```

### "Database column 'extra_data' does not exist"

```bash
# Executar migração
python -m scripts.add_metadata_column

# Ou via Render Shell:
# Render Dashboard → Web Service → Shell
python -m scripts.add_metadata_column
```

---

## 📚 Referências

- [VIDEO_GENERATORS.md](./VIDEO_GENERATORS.md) - Guia completo de setup
- [.env.example](./.env.example) - Variáveis de ambiente
- [requirements.txt](./requirements.txt) - Dependências Python
- [src/video/](./src/video/) - Código dos geradores
- [src/config/video_config.py](./src/config/video_config.py) - Sistema de configuração
- [scripts/test_video_generators.py](./scripts/test_video_generators.py) - Script de testes

---

## ✅ Checklist de Deploy

- [x] BaseVideoGenerator implementado
- [x] SimpleVideoGenerator implementado (TTS + slides)
- [x] AvatarVideoGenerator implementado (HeyGen + D-ID)
- [x] AIVideoGenerator implementado (Kling + Runway)
- [x] VideoGeneratorFactory implementado
- [x] TTSService reescrito (multi-provider)
- [x] VideoGenerationWorkflow atualizado
- [x] VideoGeneratorConfig criado
- [x] tasks.py atualizado com factory
- [x] requirements.txt atualizado
- [x] .env.example atualizado
- [x] VIDEO_GENERATORS.md criado
- [x] test_video_generators.py criado
- [ ] Dependências instaladas no Render
- [ ] Google TTS configurado
- [ ] Migração de DB executada (extra_data column)
- [ ] Teste simple generator em produção
- [ ] (Opcional) Avatar providers configurados
- [ ] (Opcional) AI providers configurados

---

## 🎉 Conclusão

O sistema de geração de vídeo está **completo e pronto para deploy**!

**O que temos**:
- 3 geradores completos com fallbacks
- Factory pattern para seleção dinâmica
- Multi-provider TTS com 4 opções
- Configuração inteligente por ambiente/briefing
- Integração com LangGraph workflows
- Scripts de teste completos
- Documentação detalhada

**Próximo passo imediato**:
1. Push das mudanças para Git
2. Deploy no Render
3. Configurar Google TTS (free tier)
4. Executar migração de DB
5. Testar simple generator em produção
6. Celebrar! 🎊

**Custo para começar**: $0 (free tier do Google Cloud TTS)

**Pronto para escalar**: Sim! Basta adicionar API keys dos outros providers conforme necessário.
