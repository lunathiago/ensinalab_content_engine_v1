# Endpoints de Cancelamento

Documentação dos endpoints para cancelar processos em andamento quando estiverem demorando demais ou travados.

## 📌 Visão Geral

Foram adicionados dois endpoints para matar processos que estão demorando muito:

1. **Cancelar geração de vídeo** - Para vídeos travados ou muito lentos
2. **Cancelar geração de opções** - Para briefings travados no processamento

Ambos usam `celery.control.revoke()` com `SIGKILL` para forçar o término imediato da task.

---

## 🎥 Cancelar Geração de Vídeo

### `POST /videos/{video_hash}/cancel`

Cancela a geração de um vídeo em andamento.

#### Autenticação
- ✅ Requer JWT token
- ✅ Verifica ownership do vídeo

#### Parâmetros
- `video_hash` (path): Hash ofuscado do vídeo (ex: `aB3xY9`)

#### Status Permitidos
Apenas vídeos nesses status podem ser cancelados:
- `queued` - Na fila
- `processing` - Sendo gerado  
- `pending_approval` - Aguardando aprovação humana

#### Resposta de Sucesso

```json
{
  "video_id": "aB3xY9",
  "message": "Vídeo cancelado com sucesso",
  "task_revoked": true,
  "status": "cancelled"
}
```

#### Erros Possíveis

**404 - Vídeo não encontrado**
```json
{
  "detail": "Vídeo não encontrado"
}
```

**400 - Status inválido**
```json
{
  "detail": "Vídeo não pode ser cancelado. Status atual: completed"
}
```

#### Exemplo de Uso

```bash
curl -X POST "https://api.ensinalab.com/videos/aB3xY9/cancel" \
  -H "Authorization: Bearer {token}"
```

#### O Que Acontece

1. ✅ Verifica ownership do vídeo
2. ✅ Valida se status permite cancelamento
3. ✅ Revoga task do Celery com `SIGKILL`
4. ✅ Atualiza status do vídeo para `cancelled`
5. ✅ Define `error_message` como "Cancelado pelo usuário"
6. ✅ Reseta `progress` para 0
7. ✅ Registra evento de segurança

---

## 📋 Cancelar Geração de Opções

### `POST /briefings/{briefing_hash}/cancel-generation`

Cancela a geração de opções em andamento para um briefing.

#### Autenticação
- ✅ Requer JWT token
- ✅ Verifica ownership do briefing

#### Parâmetros
- `briefing_hash` (path): Hash ofuscado do briefing (ex: `xY5zA2`)

#### Status Permitidos
Apenas briefings nesses status podem ser cancelados:
- `processing` - Gerando opções
- `generating_options` - Gerando opções (alias)

#### Resposta de Sucesso

```json
{
  "briefing_id": "xY5zA2",
  "message": "Geração de opções cancelada com sucesso",
  "task_revoked": true,
  "status": "cancelled"
}
```

#### Erros Possíveis

**404 - Briefing não encontrado**
```json
{
  "detail": "Briefing não encontrado"
}
```

**400 - Status inválido**
```json
{
  "detail": "Briefing não está sendo processado. Status atual: options_ready"
}
```

#### Exemplo de Uso

```bash
curl -X POST "https://api.ensinalab.com/briefings/xY5zA2/cancel-generation" \
  -H "Authorization: Bearer {token}"
```

#### O Que Acontece

1. ✅ Verifica ownership do briefing
2. ✅ Valida se status permite cancelamento
3. ✅ Revoga task do Celery com `SIGKILL`
4. ✅ Atualiza status do briefing para `cancelled`
5. ✅ Registra evento de segurança

---

## 🔧 Detalhes Técnicos

### Revogação de Tasks Celery

Ambos os endpoints usam:

```python
celery_app.control.revoke(
    task_id,
    terminate=True,    # Força término imediato
    signal='SIGKILL'   # Mata o processo
)
```

**Parâmetros:**
- `terminate=True`: Não apenas remove da fila, mas mata o worker
- `signal='SIGKILL'`: Usa SIGKILL em vez de SIGTERM (não pode ser ignorado)

### Logs de Segurança

Todos os cancelamentos são registrados:

```python
log_security_event("video_cancelled", {
    "user_id": current_user.id,
    "video_id": video_id,
    "task_id": video.task_id,
    "revoked": True
})
```

### Migration Necessária

Para usar o cancelamento de briefings, é necessário rodar a migration:

```bash
python scripts/add_task_id_to_briefing.py
```

Isso adiciona o campo `task_id` à tabela `briefings`.

---

## 📊 Novos Status

### BriefingStatus

Adicionado: `CANCELLED = "cancelled"`

```python
class BriefingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    OPTIONS_READY = "options_ready"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"  # ← Novo
```

### VideoStatus

Adicionado: `CANCELLED = "cancelled"`

```python
class VideoStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"  # ← Novo
```

---

## 🎯 Casos de Uso

### Vídeo Travado

Se um vídeo está em `processing` há mais de 5 minutos (limite da task):

```bash
# Verificar status
GET /videos/aB3xY9/status

# Se travado, cancelar
POST /videos/aB3xY9/cancel

# Tentar novamente (selecionar opção novamente)
POST /options/{option_hash}/select
```

### Briefing Travado

Se um briefing está em `processing` há muito tempo:

```bash
# Verificar status do briefing
GET /briefings/xY5zA2

# Cancelar geração
POST /briefings/xY5zA2/cancel-generation

# Recriar briefing ou tentar novamente
POST /briefings
```

---

## ⚠️ Observações Importantes

1. **SIGKILL é Drástico**
   - Não permite cleanup gracioso
   - Use apenas quando realmente necessário
   - Tasks devem ser idempotentes

2. **Celery Worker Pode Demorar**
   - A revogação não é instantânea
   - Worker pode levar alguns segundos para reagir
   - Status é atualizado imediatamente no banco

3. **Ownership é Crítico**
   - Usuário só pode cancelar seus próprios recursos
   - Tentativas não autorizadas são registradas em logs

4. **Não Há Rollback Automático**
   - Arquivos parciais não são removidos automaticamente
   - Registros no banco ficam como `cancelled`
   - Pode ser necessário limpeza manual

---

## 🔐 Segurança

### Validações Implementadas

✅ Autenticação JWT obrigatória  
✅ Verificação de ownership do recurso  
✅ Validação de status antes de cancelar  
✅ Log de todas as tentativas de cancelamento  
✅ Resposta genérica para recursos não encontrados (evita info leak)

### Rate Limiting

Os endpoints de cancelamento respeitam os mesmos limites da API:

- 100 requisições/minuto por usuário (padrão)
- 10 requisições/minuto para cancelamentos (recomendado adicionar)

---

## 📝 Próximos Passos

### Melhorias Sugeridas

1. **Rate Limiting Específico**
   ```python
   @limiter.limit("10/minute")
   async def cancel_video(...):
   ```

2. **Limpeza Automática de Arquivos**
   - Deletar arquivos parciais após cancelamento
   - Usar task assíncrona para cleanup

3. **Notificações**
   - WebSocket para notificar frontend
   - Email se cancelamento falhar

4. **Métricas**
   - Contabilizar quantos cancelamentos por dia
   - Alertar se taxa de cancelamento > 10%

5. **Timeout Automático**
   - Cancelar automaticamente após 2x o tempo esperado
   - Enviar notificação ao usuário

---

## 🧪 Testes

### Teste Manual - Cancelar Vídeo

```bash
# 1. Criar briefing
curl -X POST "https://api.ensinalab.com/briefings" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "title": "Teste de Cancelamento",
    "description": "...",
    "duration_minutes": 10
  }'

# 2. Gerar opções e selecionar
# ... (seguir fluxo normal)

# 3. Imediatamente após iniciar geração, cancelar
curl -X POST "https://api.ensinalab.com/videos/{hash}/cancel" \
  -H "Authorization: Bearer {token}"

# 4. Verificar status
curl -X GET "https://api.ensinalab.com/videos/{hash}/status" \
  -H "Authorization: Bearer {token}"
# Deve retornar: { "status": "cancelled" }
```

### Teste de Segurança

```bash
# Tentar cancelar vídeo de outro usuário
curl -X POST "https://api.ensinalab.com/videos/{hash_outro_user}/cancel" \
  -H "Authorization: Bearer {token}"
# Deve retornar: 404 (não 403, para evitar info leak)
```

---

## 📚 Referências

- [Celery: Revoking Tasks](https://docs.celeryproject.org/en/stable/userguide/workers.html#revoking-tasks)
- [FastAPI: Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [PostgreSQL: Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
