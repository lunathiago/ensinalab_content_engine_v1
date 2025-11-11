# 🔧 Troubleshooting: Worker Não Dispara

## 🎯 Sintomas

- Briefing é criado com sucesso
- Nenhuma opção é gerada
- Status do briefing fica em `pending` indefinidamente
- Worker não processa tarefas

---

## 🔍 Diagnóstico Rápido

### **1. Verificar se Worker está rodando**

1. Acesse: https://dashboard.render.com
2. Encontre o serviço: **ensinalab-worker**
3. Verifique status:
   - ✅ **Running** (verde) = OK
   - ⚠️ **Build Failed** (vermelho) = Erro no deploy
   - ⏸️ **Suspended** (cinza) = Worker pausado

**Se não estiver verde:**
- Clique no serviço
- Vá em **Logs**
- Procure por erros de startup

---

### **2. Verificar Logs do Worker**

1. **ensinalab-worker** → **Logs**
2. Procure por:

#### **Startup bem-sucedido:**
```
[2025-11-11 00:00:00,000: INFO/MainProcess] Connected to redis://...
[2025-11-11 00:00:00,000: INFO/MainProcess] celery@worker ready.
```

#### **Erros comuns:**

**Erro 1: Redis não conecta**
```
[ERROR/MainProcess] consumer: Cannot connect to redis://...
```
➡️ **Solução:** Verificar `REDIS_URL` nas Environment Variables

**Erro 2: Imports falhando**
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'X' from 'Y'
```
➡️ **Solução:** Problema no código, verificar imports circulares

**Erro 3: Task não registrada**
```
[ERROR/MainProcess] Received unregistered task of type 'src.workers.tasks.generate_options'
```
➡️ **Solução:** Worker não carregou tasks.py corretamente

---

### **3. Verificar Redis**

1. Dashboard → **ensinalab-redis** (ou nome do seu Redis)
2. Status deve estar: **Available**
3. Copiar **Internal URL**: `redis://red-xxx:6379/0`

4. Verificar se **REDIS_URL** está configurado:
   - **ensinalab-worker** → Environment
   - **ensinalab-api** → Environment
   - Ambos devem ter: `REDIS_URL = redis://red-xxx:6379/0`

---

### **4. Testar Task Manualmente**

Se worker está rodando mas não processa:

1. Acesse: **ensinalab-api** → **Shell**
2. Execute:

```python
from src.workers.tasks import generate_options

# Disparar task de teste
result = generate_options.delay(1)
print(f"Task ID: {result.id}")
print(f"Status: {result.state}")
```

3. Aguarde 10-30 segundos
4. Verifique logs do **worker** para ver se processou

---

## 🛠️ Soluções Comuns

### **Problema 1: Worker não inicia**

**Causa:** Erro no build ou dependências faltando

**Solução:**
1. Verificar `requirements.txt` tem todas as dependências
2. Force rebuild:
   - **ensinalab-worker** → Settings
   - **"Manual Deploy"**
   - **"Clear build cache & deploy"**

---

### **Problema 2: Redis URL incorreto**

**Causa:** `REDIS_URL` aponta para lugar errado

**Solução:**
1. Obter URL correto:
   - Dashboard → Redis service → Connect
   - Copiar **Internal URL**

2. Atualizar em:
   - **ensinalab-worker** → Environment → `REDIS_URL`
   - **ensinalab-api** → Environment → `REDIS_URL`

3. Salvar (serviços vão reiniciar)

**Formato correto:**
```
redis://red-abc123xyz:6379/0
```

**Formatos ERRADOS:**
```
redis://localhost:6379/0          ❌ (localhost não existe no Render)
redis://127.0.0.1:6379/0          ❌ (loopback não funciona)
redis://redis:6379/0              ❌ (nome genérico não resolve)
```

---

### **Problema 3: Worker suspende sozinho**

**Causa:** Free tier do Render suspende após 15min inativo

**Solução A:** Upgrade para plano pago ($7/mês)

**Solução B:** Keep-alive temporário:
1. Criar script que dispara task dummy a cada 10min
2. Usar cron job externo (ex: cron-job.org)
3. Endpoint: `POST /api/v1/health/ping`

---

### **Problema 4: Tasks ficam em PENDING**

**Causa:** Worker não está pegando tasks da fila

**Checklist:**
- [ ] Worker está Running? (verde)
- [ ] Logs mostram "celery@worker ready"?
- [ ] REDIS_URL está correto?
- [ ] Redis está Available?
- [ ] Task está registrada? (verificar logs de startup)

**Se tudo OK mas ainda PENDING:**
1. Restart manual do worker:
   - Settings → Restart
2. Aguardar 1-2 minutos
3. Criar novo briefing de teste

---

### **Problema 5: Imports circulares**

**Sintoma:**
```
ImportError: cannot import name 'X' from partially initialized module 'Y'
```

**Solução:**
1. Verificar `src/workers/tasks.py`
2. Garantir que `import_all_models()` é chamado PRIMEIRO
3. Imports devem seguir ordem:
   ```python
   # 1. Celery
   from src.workers.celery_config import celery_app
   
   # 2. Database
   from src.config.database import SessionLocal, import_all_models
   import_all_models()  # ← IMPORTANTE
   
   # 3. Enums (não causam circular)
   from src.models.briefing import BriefingStatus
   
   # 4. Services (não importam models diretamente)
   from src.services.briefing_service import BriefingService
   ```

---

## 📋 Checklist Completo

Execute em ordem:

- [ ] **Redis está Available?**
  - Dashboard → Redis → Status = Available

- [ ] **REDIS_URL configurado?**
  - Worker → Environment → REDIS_URL existe?
  - API → Environment → REDIS_URL existe?
  - URLs são idênticas?

- [ ] **Worker está Running?**
  - Dashboard → ensinalab-worker → Status = Running

- [ ] **Logs do Worker mostram startup OK?**
  - Logs → Procurar "celery@worker ready"
  - Sem erros de import
  - Sem erros de conexão Redis

- [ ] **Tasks estão registradas?**
  - Logs → Procurar lista de tasks registradas
  - Deve incluir: generate_options, generate_video

- [ ] **Teste manual funciona?**
  - API Shell → `generate_options.delay(1)`
  - Worker logs mostram processamento

- [ ] **Briefing dispara task?**
  - Criar briefing via API
  - API logs mostram: "✅ Briefing X criado"
  - Worker logs mostram: "▶️ Gerando opções para briefing X"

---

## 🚨 Se nada funcionar

### **Opção 1: Restart completo**

1. **ensinalab-redis** → Settings → Restart
2. Aguardar 30s
3. **ensinalab-worker** → Settings → Restart
4. Aguardar 1min
5. **ensinalab-api** → Settings → Restart
6. Aguardar 1min
7. Testar criação de briefing

### **Opção 2: Verificar limites do Free Tier**

Render Free Tier tem limitações:
- Worker pode suspender após inatividade
- Redis compartilhado pode ter latência
- Build pode falhar por timeout

**Sintomas:**
- Worker fica amarelo (suspendido)
- Redis fica lento (>100ms latência)

**Solução:** Upgrade para Starter ($7/mês worker + $10/mês Redis)

### **Opção 3: Logs detalhados**

1. **ensinalab-worker** → Settings
2. Add Environment Variable:
   ```
   CELERY_LOG_LEVEL = DEBUG
   ```
3. Save → Restart
4. Verificar logs com mais detalhes

---

## 📊 Comandos úteis (API Shell)

```python
# Ver tasks na fila
from src.workers.celery_config import celery_app
inspect = celery_app.control.inspect()

# Workers ativos
print(inspect.active())

# Tasks agendadas
print(inspect.scheduled())

# Tasks reservadas
print(inspect.reserved())

# Estatísticas
print(inspect.stats())
```

---

## 🆘 Ainda com problemas?

1. **Exportar logs:**
   - Worker → Logs → Download
   - API → Logs → Download

2. **Compartilhar:**
   - Procurar por linhas com `ERROR` ou `WARNING`
   - Últimas 50 linhas do startup

3. **Informações úteis:**
   - Quando worker parou de funcionar?
   - Última vez que funcionou?
   - Mudanças recentes no código?
   - Deploy recente?

---

**Criado:** 2025-11-11  
**Atualizado:** Quando resolver, documente a solução aqui!
