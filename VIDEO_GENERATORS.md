# 🎬 Video Generators - Guia Completo

Este documento explica os 3 geradores de vídeo implementados no EnsinaLab Content Engine e como configurá-los.

## 📊 Visão Geral

O sistema oferece 3 tipos de geradores com diferentes níveis de custo, qualidade e velocidade:

| Gerador | Custo/min | Velocidade | Qualidade | Melhor Para |
|---------|-----------|------------|-----------|-------------|
| **Simple** | $0.05-0.30 | ⚡ Rápido (2-5 min) | ⭐⭐⭐ Boa | Desenvolvimento, testes, conteúdo informativo |
| **Avatar** | $3-10 | ⚡⚡ Médio (5-15 min) | ⭐⭐⭐⭐ Excelente | Produção, treinamentos profissionais |
| **AI** | $30-100 | 🐌 Lento (20-60 min) | ⭐⭐⭐⭐⭐ Cinematográfica | Conteúdo premium, marketing, experimental |

## 🎯 1. Simple Generator (TTS + Slides)

### Descrição
Combina Text-to-Speech com slides estáticos gerados via PIL. O mais econômico e rápido.

### Como Funciona
1. Divide o roteiro em 5-7 seções
2. Gera áudio para cada seção via TTS
3. Cria slides com gradientes e texto (1920x1080)
4. Concatena slides com transições crossfade

### Configuração

#### TTS Providers Disponíveis

##### Google Cloud TTS (Recomendado para Dev)
```bash
# Opção 1: Service Account (mais seguro)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Opção 2: API Key
GOOGLE_CLOUD_API_KEY=AIza...
```

**Setup Google Cloud**:
1. Criar projeto em [console.cloud.google.com](https://console.cloud.google.com)
2. Ativar Cloud Text-to-Speech API
3. Criar Service Account ou API Key
4. Free tier: Até 4 milhões de caracteres/mês

##### ElevenLabs (Melhor Qualidade)
```bash
ELEVENLABS_API_KEY=sk_...
```

**Setup ElevenLabs**:
1. Criar conta em [elevenlabs.io](https://elevenlabs.io)
2. Obter API key em Settings > API Keys
3. Custo: ~$0.30/1000 caracteres (pay-as-you-go)
4. Vozes: Suporte para português com alta naturalidade

##### Amazon Polly (Free Tier Generoso)
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

**Setup AWS Polly**:
1. Criar conta AWS
2. Criar IAM User com permissão `polly:SynthesizeSpeech`
3. Free tier: 5 milhões de caracteres/mês
4. Vozes: Camila, Vitória (português BR)

##### Azure Speech
```bash
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus
```

**Setup Azure**:
1. Criar recurso Speech Service no Azure Portal
2. Copiar chave e região
3. Free tier: 500K caracteres/mês

### Exemplo de Uso
```python
from src.video.factory import VideoGeneratorFactory

# Usando Google TTS
generator = VideoGeneratorFactory.create('simple', provider='google')

# Ou com ElevenLabs (melhor qualidade)
generator = VideoGeneratorFactory.create('simple', provider='elevenlabs')

result = generator.generate(
    script="Bem-vindo ao treinamento...",
    title="Introdução à Gestão Escolar",
    metadata={'tone': 'professional'},
    video_id=1
)
```

### Estrutura de Slides
- Resolução: 1920x1080
- Background: Gradiente azul/roxo com marca d'água "EnsinaLab"
- Fonte: Arial bold, tamanho ajustado automaticamente
- Transições: Crossfade 0.5s

---

## 👤 2. Avatar Generator (Virtual Presenters)

### Descrição
Usa APIs de avatar virtual (HeyGen ou D-ID) para criar vídeos com apresentadores realistas.

### Providers

#### HeyGen (Recomendado)
```bash
HEYGEN_API_KEY=...
```

**Setup HeyGen**:
1. Criar conta em [heygen.com](https://heygen.com)
2. Obter API key no dashboard
3. Custo: ~$5-10/minuto de vídeo
4. Avatares: 100+ opções, suporte português
5. API: v2 com polling automático

**Avatares Disponíveis**:
- `Kristin_public_2`: Mulher caucasiana, formal
- `Tyler_public`: Homem caucasiano, casual
- `Eric_public_pro2`: Avatar brasileiro, PT-BR nativo

#### D-ID (Alternativa Mais Barata)
```bash
DID_API_KEY=...
```

**Setup D-ID**:
1. Criar conta em [d-id.com](https://d-id.com)
2. Obter API key em Settings
3. Custo: ~$3-5/minuto
4. API: Talk API com polling

### Exemplo de Uso
```python
from src.video.factory import VideoGeneratorFactory

# HeyGen (mais natural)
generator = VideoGeneratorFactory.create('avatar', provider='heygen')

# D-ID (mais barato)
generator = VideoGeneratorFactory.create('avatar', provider='did')

result = generator.generate(
    script="Neste treinamento, você aprenderá...",
    title="Gestão de Conflitos",
    metadata={
        'avatar_id': 'Kristin_public_2',  # Opcional
        'voice': 'pt-BR-FranciscaNeural'
    },
    video_id=2
)
```

### Polling e Timeout
- HeyGen: 60 tentativas × 10s = 10 minutos max
- D-ID: 60 tentativas × 5s = 5 minutos max
- Download automático com barra de progresso

---

## 🎨 3. AI Generator (Text-to-Video)

### Descrição
Gera vídeos cinemáticos usando IA generativa. Experimental e caro, mas resultados impressionantes.

### Providers

#### Kling AI (Recomendado)
```bash
KLING_API_KEY=...
```

**Setup Kling AI**:
1. Criar conta em [klingai.com](https://klingai.com)
2. Obter API key
3. Custo: ~$30-50/minuto
4. Qualidade: Alta, estilo realista

#### Runway Gen-3
```bash
RUNWAY_API_KEY=...
```

**Setup Runway**:
1. Criar conta em [runwayml.com](https://runwayml.com)
2. Obter API key no dashboard
3. Custo: ~$50-100/minuto
4. Qualidade: Cinematográfica, estilo artístico

### Como Funciona
1. **Parse de Cenas**: LLM divide roteiro em cenas visuais
2. **Prompt Engineering**: Gera prompts visuais descritivos
3. **Geração**: Cria vídeos para cada cena (5-10s cada)
4. **Concatenação**: Une cenas em vídeo final

### Exemplo de Uso
```python
from src.video.factory import VideoGeneratorFactory

# Kling AI (mais rápido)
generator = VideoGeneratorFactory.create('ai', provider='kling')

# Runway (mais cinematográfico)
generator = VideoGeneratorFactory.create('ai', provider='runway')

result = generator.generate(
    script="Era uma vez uma escola transformada pela tecnologia...",
    title="O Futuro da Educação",
    metadata={
        'quality': 'cinematic',  # standard, high, cinematic
        'max_scenes': 8
    },
    video_id=3
)
```

### Limitações
- ⏱️ Muito lento (20-60 min para 5 min de vídeo)
- 💰 Muito caro ($150-500 por vídeo de 5 min)
- 🧪 Experimental: resultados podem variar
- 🎭 Melhor para conteúdo visual/narrativo, não explicativo

---

## 🏭 Factory Pattern - Seleção Automática

### Uso Básico
```python
from src.video.factory import VideoGeneratorFactory

# Seleção manual
generator = VideoGeneratorFactory.create('simple')  # Padrão: Google TTS
generator = VideoGeneratorFactory.create('avatar', provider='heygen')
generator = VideoGeneratorFactory.create('ai', provider='kling')

# Atalhos
from src.video.factory import create_simple_generator, create_avatar_generator

generator = create_simple_generator(provider='elevenlabs')
generator = create_avatar_generator(provider='heygen')
```

### Seleção Inteligente
```python
from src.video.factory import VideoGeneratorFactory

# Recomendação baseada em budget/qualidade/urgência
recommendation = VideoGeneratorFactory.recommend_generator(
    budget_usd=10.0,      # Budget máximo
    urgency='normal',      # low, normal, high
    quality_level='high'   # standard, high, premium
)
# Retorna: {'type': 'avatar', 'provider': 'did', 'estimated_cost': 8.50}

generator = VideoGeneratorFactory.create(**recommendation)
```

### Seleção por Briefing
```python
from src.config.video_config import video_config

# Análise automática do briefing
config = video_config.get_generator_for_briefing({
    'duration_minutes': 3,
    'tone': 'professional',
    'subject_area': 'leadership'
})
# Retorna: {'generator_type': 'avatar', 'provider': 'heygen'}

generator = VideoGeneratorFactory.create(**config)
```

---

## ⚙️ Configuração por Ambiente

### Via Variável de Ambiente
```bash
# Development: usa simple (rápido e barato)
ENVIRONMENT=development
VIDEO_GENERATOR_TYPE=simple

# Production: usa avatar (qualidade profissional)
ENVIRONMENT=production
VIDEO_GENERATOR_TYPE=avatar

# Premium: usa AI (máxima qualidade)
ENVIRONMENT=premium
VIDEO_GENERATOR_TYPE=ai
```

### Via Código
```python
from src.config.video_config import video_config

# Obter configuração do ambiente atual
env_config = video_config.get_generator_config('production')
# Retorna: {'generator_type': 'avatar', 'provider': 'heygen'}

# Estimar custo
cost = video_config.estimate_cost('avatar', duration_minutes=5)
# Retorna: 37.50 (USD)
```

---

## 📦 Instalação de Dependências

### Dependências Básicas (Simple Generator)
```bash
pip install google-cloud-texttospeech pillow moviepy pydub
```

### Todas as Dependências
```bash
pip install -r requirements.txt
```

### Verificar Instalação
```python
from src.video.factory import VideoGeneratorFactory

# Listar geradores disponíveis
generators = VideoGeneratorFactory.get_available_generators()
for gen in generators:
    print(f"{gen['type']}: {gen['description']}")
    print(f"  Custo: ${gen['cost_per_minute']:.2f}/min")
    print(f"  Velocidade: {gen['generation_speed']}")
```

---

## 🧪 Testando os Geradores

### Teste Simple Generator
```bash
# Definir apenas Google TTS (free tier)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Executar teste
python scripts/test_workflows.py --generator simple
```

### Teste Avatar Generator
```bash
# Definir chave D-ID (mais barato para testes)
export DID_API_KEY=your-key

# Executar teste
python scripts/test_workflows.py --generator avatar --provider did
```

### Teste via API
```bash
# Criar briefing e opção
curl -X POST http://localhost:8000/api/briefings \
  -H "Content-Type: application/json" \
  -d '{
    "target_audience": "Gestores escolares",
    "subject_area": "Liderança",
    "duration_minutes": 3,
    "tone": "professional"
  }'

# Gerar vídeo (usa seleção automática)
curl -X POST http://localhost:8000/api/videos/{video_id}/generate
```

---

## 💰 Otimização de Custos

### Estratégias

#### 1. Ambiente-Based Routing
```python
# Development: sempre simple
# Staging: avatar para demos importantes
# Production: avatar como padrão
# Premium: AI apenas se solicitado explicitamente
```

#### 2. Duration-Based Selection
```python
# ≤ 2 min: simple (rápido e barato)
# 2-10 min: avatar (melhor custo-benefício)
# > 10 min: verificar budget antes de usar AI
```

#### 3. Content-Type Routing
```python
# Conteúdo informativo/tutorial: simple
# Treinamento profissional: avatar
# Marketing/institucional: AI
```

### Estimativa de Custos

| Cenário | Duração | Gerador | Custo Estimado |
|---------|---------|---------|----------------|
| Teste rápido | 1 min | Simple (Google) | $0.05 |
| Tutorial básico | 5 min | Simple (ElevenLabs) | $1.50 |
| Treinamento padrão | 5 min | Avatar (D-ID) | $18.00 |
| Treinamento premium | 5 min | Avatar (HeyGen) | $37.50 |
| Vídeo institucional | 2 min | AI (Kling) | $80.00 |
| Vídeo marketing | 3 min | AI (Runway) | $240.00 |

---

## 🚨 Troubleshooting

### Erro: "TTS provider not available"
```bash
# Verificar instalação
pip install google-cloud-texttospeech elevenlabs boto3

# Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $ELEVENLABS_API_KEY
```

### Erro: "Avatar generation timeout"
```bash
# HeyGen/D-ID estão sobrecarregados
# Aumentar timeout ou tentar novamente

# Verificar status do job manualmente
curl -H "Authorization: Bearer $HEYGEN_API_KEY" \
  https://api.heygen.com/v2/video_status/{video_id}
```

### Erro: "AI generation failed"
```bash
# Verificar prompt gerado pelo LLM
# Logs em /tmp/ensinalab_videos/ai_generator_debug.json

# Reduzir número de cenas
export AI_GENERATOR_MAX_SCENES=5
```

### Fallback Automático
O sistema tem fallbacks integrados:
1. **TTS**: Google → ElevenLabs → Amazon → Azure → Silêncio
2. **Avatar**: Provider especificado → Erro (sem fallback entre providers)
3. **AI**: Provider especificado → Erro (sem fallback entre providers)

---

## 📊 Monitoramento

### Logs
```bash
# Logs de geração
tail -f /tmp/ensinalab_videos/generation.log

# Logs de custo
tail -f /tmp/ensinalab_videos/cost_tracking.log
```

### Métricas
```python
from src.video.factory import VideoGeneratorFactory

# Metadata retornada por todos os geradores
result = generator.generate(...)
print(result['metadata'])
# {
#   'generator_type': 'avatar',
#   'provider': 'heygen',
#   'generation_time_seconds': 342,
#   'estimated_cost_usd': 37.50,
#   'file_size_mb': 45.2,
#   'duration_seconds': 300,
#   'resolution': '1920x1080',
#   'audio_provider': 'heygen_builtin'
# }
```

---

## 🎓 Recomendações

### Para Desenvolvimento
- Use **Simple Generator** com **Google TTS** (free tier)
- Configure `ENVIRONMENT=development` no `.env`
- Gere vídeos curtos (1-2 min) para testes

### Para Produção
- Use **Avatar Generator** com **HeyGen** como padrão
- Configure fallback para **D-ID** se HeyGen falhar
- Implemente cache de vídeos gerados (não regerarScripts idênticos)

### Para Casos Especiais
- **Marketing institucional**: AI Generator com Kling AI
- **Treinamentos longos (>15 min)**: Simple Generator (custo-efetivo)
- **Demos para clientes**: Avatar Generator com vozes premium

---

## 📚 Referências

### APIs
- [Google Cloud TTS](https://cloud.google.com/text-to-speech/docs)
- [ElevenLabs API](https://docs.elevenlabs.io/)
- [Amazon Polly](https://docs.aws.amazon.com/polly/)
- [Azure Speech](https://learn.microsoft.com/azure/cognitive-services/speech-service/)
- [HeyGen API](https://docs.heygen.com/)
- [D-ID API](https://docs.d-id.com/)
- [Kling AI](https://klingai.com/docs)
- [Runway API](https://docs.runwayml.com/)

### Bibliotecas
- [MoviePy](https://zulko.github.io/moviepy/)
- [Pillow (PIL)](https://pillow.readthedocs.io/)
- [Pydub](https://github.com/jiaaro/pydub)
