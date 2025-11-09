# ✅ CHECKLIST - Deploy da Jornada Completa

## 🎯 Objetivo
Implementar e testar a jornada completa:
**Briefing → Options → Select → Video Generation → Download**

---

## 📦 1. COMMIT E PUSH (FEITO AGORA)

Arquivos alterados:
- ✅ `src/models/video.py` - Adicionado campo `script`
- ✅ `src/services/video_service.py` - Adicionado `create_video()`
- ✅ `src/services/option_service.py` - Melhorado `select_option()`
- ✅ `src/api/routes/options.py` - Endpoint `/options/{id}/select` completo
- ✅ `src/video/tts.py` - Melhorado ElevenLabs com fallback
- ✅ `scripts/add_script_column.py` - Nova migração

---

## 🚀 2. DEPLOY NO RENDER

### 2.1 Push para GitHub
```bash
git add -A
git commit -m "feat: Complete video generation journey

- Add script field to Video model
- Implement VideoService.create_video()
- Improve OptionService.select_option()
- Complete /options/{id}/select endpoint
- Enhance ElevenLabs TTS with Google fallback
- Add migration script for script column"

git push origin main
```

### 2.2 Aguardar Deploy Automático
- Render detecta push e inicia deploy
- Aguardar ~5-10 minutos
- Verificar logs no dashboard

---

## 🗄️ 3. EXECUTAR MIGRAÇÕES (CRÍTICO)

Acessar **Render Shell** (no dashboard do serviço Web):

```bash
# 1. Migração: coluna extra_data (se ainda não executou)
python -m scripts.add_metadata_column

# 2. Migração: coluna generator_type (se ainda não executou)
python -m scripts.add_generator_type_column

# 3. Migração: coluna script (NOVA)
python -m scripts.add_script_column
```

**Verificar sucesso:**
```bash
# Verificar estrutura da tabela videos
python -c "
from src.config.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \\'videos\\''))
    print('Colunas da tabela videos:')
    for row in result:
        print(f'  - {row[0]}')
"
```

Deve aparecer:
- ✅ `script`
- ✅ `generator_type`
- ✅ `extra_data` (se Option também tiver)

---

## ⚙️ 4. VARIÁVEIS DE AMBIENTE

Verificar no Render Dashboard → Environment:

### **Essenciais (OBRIGATÓRIAS)**
```bash
DATABASE_URL=postgresql://...  # Fornecido pelo Render
REDIS_URL=redis://...          # Fornecido pelo Render
OPENAI_API_KEY=sk-proj-...     # Seu OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo     # Modelo mais barato
```

### **Video Generation (OBRIGATÓRIAS)**
```bash
VIDEO_GENERATOR_TYPE=simple
ELEVENLABS_API_KEY=sk_...      # Seu ElevenLabs API key
SIMPLE_GENERATOR_TTS_PROVIDER=elevenlabs
```

### **Opcionais (Fallback)**
```bash
GOOGLE_CLOUD_API_KEY=AIza...   # Se tiver Google TTS
LOG_LEVEL=INFO
CELERY_TASK_TIME_LIMIT=1800
```

---

## 🧪 5. TESTAR JORNADA COMPLETA

### 5.1 Criar Briefing
```bash
curl -X POST https://seu-app.onrender.com/api/v1/briefings \
  -H "Content-Type: application/json" \
  -d '{
    "target_audience": "Gestores escolares",
    "subject_area": "Liderança e Motivação",
    "duration_minutes": 3,
    "tone": "profissional",
    "key_topics": ["gestão de equipe", "comunicação eficaz"],
    "context": "Treinamento para diretores de escola"
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "target_audience": "Gestores escolares",
  "status": "processing",
  "created_at": "2025-11-09T..."
}
```

### 5.2 Aguardar Geração de Opções (~1-2 min)
```bash
curl https://seu-app.onrender.com/api/v1/briefings/1/options
```

**Resposta esperada:**
```json
[
  {
    "id": 1,
    "title": "Liderança Transformadora na Gestão Escolar",
    "summary": "Vídeo focado em...",
    "script_outline": "...",
    "relevance_score": 0.95,
    "estimated_duration": 180
  },
  {
    "id": 2,
    "title": "Comunicação Eficaz para Gestores",
    ...
  },
  ...
]
```

### 5.3 Selecionar Opção e Gerar Vídeo
```bash
curl -X POST https://seu-app.onrender.com/api/v1/options/1/select \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Gostei desta abordagem!"
  }'
```

**Resposta esperada:**
```json
{
  "message": "Opção selecionada! Vídeo será gerado.",
  "video_id": 1,
  "task_id": "abc123...",
  "status": "QUEUED",
  "estimated_time": "2-5 minutos"
}
```

### 5.4 Verificar Status do Vídeo
```bash
# Consultar a cada 30s
curl https://seu-app.onrender.com/api/v1/videos/1
```

**Progressão esperada:**
```json
// Inicial
{"id": 1, "status": "QUEUED", "progress": 0.0}

// Processando
{"id": 1, "status": "PROCESSING", "progress": 0.3}
{"id": 1, "status": "PROCESSING", "progress": 0.7}

// Completo
{
  "id": 1,
  "status": "COMPLETED",
  "progress": 1.0,
  "file_path": "/tmp/ensinalab_videos/video_1.mp4",
  "duration_seconds": 185,
  "file_size_bytes": 12458672,
  "thumbnail_path": "/tmp/ensinalab_thumbnails/video_1_thumb.jpg",
  "generator_type": "simple"
}
```

### 5.5 Download do Vídeo
```bash
curl -O https://seu-app.onrender.com/api/v1/videos/1/download
```

---

## 🐛 6. TROUBLESHOOTING

### Erro: "Column 'script' does not exist"
**Solução:** Execute migração `add_script_column.py`
```bash
python -m scripts.add_script_column
```

### Erro: "ELEVENLABS_API_KEY not found"
**Solução:** Adicionar variável no Render
```bash
# Render Dashboard → Environment → Add
ELEVENLABS_API_KEY=sk_your_key_here
```

### Erro: "Task timeout after 1800s"
**Solução:** Aumentar timeout
```bash
CELERY_TASK_TIME_LIMIT=3600
```

### Vídeo fica em PROCESSING forever
**Solução:** Verificar logs do Worker
```bash
# Render Dashboard → ensinalab-worker → Logs
# Procurar por erros de TTS ou MoviePy
```

### ElevenLabs retorna 401 Unauthorized
**Solução:** Verificar API key
```bash
# Testar manualmente:
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/user
```

---

## 📊 7. MÉTRICAS DE SUCESSO

### ✅ Jornada completa funcionando se:
- [ ] Briefing criado (status: processing)
- [ ] 4 opções geradas em ~1-2 min
- [ ] Opção selecionada dispara task
- [ ] Vídeo progride: QUEUED → PROCESSING → COMPLETED
- [ ] Arquivo MP4 gerado em `/tmp/ensinalab_videos/`
- [ ] Thumbnail gerado
- [ ] Download funciona

### 📈 Performance esperada:
- **Briefing → Options**: 60-120s
- **Select → Video QUEUED**: <1s
- **Video QUEUED → PROCESSING**: <5s
- **Video PROCESSING → COMPLETED**: 120-300s (vídeo de 3 min)
- **Total**: ~3-7 minutos

---

## 🎯 8. PRÓXIMOS PASSOS (APÓS SUCESSO)

- [ ] Implementar endpoint de download (`/videos/{id}/download`)
- [ ] Adicionar frontend para visualização
- [ ] Implementar sistema de filas (rate limiting)
- [ ] Adicionar storage permanente (S3/GCS)
- [ ] Implementar sistema de notificações
- [ ] Dashboard de custos e métricas
- [ ] Testes automatizados end-to-end

---

## 📝 COMANDOS RÁPIDOS

```bash
# Ver logs do Worker em tempo real
# Render Dashboard → ensinalab-worker → Logs → Live

# Restart dos serviços (se necessário)
# Render Dashboard → Manual Deploy → Clear build cache & deploy

# Verificar health check
curl https://seu-app.onrender.com/health

# Listar todos os briefings
curl https://seu-app.onrender.com/api/v1/briefings

# Listar todos os vídeos
curl https://seu-app.onrender.com/api/v1/videos
```

---

## ✅ STATUS FINAL

- [x] Modelo Video com campo script
- [x] VideoService.create_video() implementado
- [x] OptionService.select_option() melhorado
- [x] Endpoint /options/{id}/select completo
- [x] ElevenLabs TTS com fallback Google
- [x] Script de migração add_script_column.py
- [ ] **EXECUTAR MIGRAÇÕES NO RENDER** ← PRÓXIMO PASSO
- [ ] **TESTAR JORNADA COMPLETA** ← VALIDAÇÃO FINAL

---

**🚀 PRONTO PARA DEPLOY!**

Execute os passos 2 e 3, depois teste com os comandos da seção 5.
