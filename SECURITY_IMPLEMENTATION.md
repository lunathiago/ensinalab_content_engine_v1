# 🔐 Plano de Segurança de Curto Prazo - EnsinaLab

## ✅ Implementado

### 1. **Ofuscação de IDs com Hashids**
- ✅ Utilitário `src/utils/hashid.py` criado
- ✅ IDs expostos agora são hashes: `jR3kM9wX` em vez de `1`
- ✅ Schemas atualizados (VideoResponse, BriefingResponse, OptionResponse)
- ✅ Routes atualizam para aceitar `{resource_hash}` em vez de `{resource_id}`
- ✅ Decodificação automática com `decode_id(hash)`

**Exemplo:**
```bash
# Antes: /api/v1/videos/1 
# Depois: /api/v1/videos/jR3kM9wX
```

### 2. **Rate Limiting**
- ✅ SlowAPI configurado em `src/config/rate_limit.py`
- ✅ Limites por tipo de endpoint:
  - Auth: 5 req/min
  - Leitura (GET): 30 req/min
  - Escrita (POST/DELETE): 10 req/min
  - Download: 3 req/min
- ✅ Integrado no FastAPI app

### 3. **Respostas Genéricas (Info Leak Prevention)**
- ✅ Erro 404 genérico em vez de 403 quando apropriado
- ✅ Não revela se recurso existe quando não autorizado
- ✅ Pattern aplicado em todos os endpoints

**Antes:**
```python
if not video:
    raise HTTPException(404, "Not found")
if video.user_id != current_user.id:
    raise HTTPException(403, "Access denied")  # ❌ Info leak!
```

**Depois:**
```python
if not video or video.user_id != current_user.id:
    raise HTTPException(404, "Not found")  # ✅ Genérico
```

### 4. **Security Logging**
- ✅ Logger específico `src/utils/logger.py::log_security_event()`
- ✅ Registra tentativas de acesso não autorizado
- ✅ Formato JSON para fácil parsing
- ✅ Aplicado em todos os endpoints

**Exemplo de log:**
```json
{
  "timestamp": "2025-11-09T...",
  "event": "unauthorized_access_attempt",
  "user_id": 123,
  "resource": "video",
  "resource_id": 456,
  "action": "download"
}
```

## 🔧 Configuração Necessária

### `.env` - Adicionar:
```env
# Hashids (geração de hash seguro)
HASHID_SALT=<gerar-com: python -c "import secrets; print(secrets.token_urlsafe(32))">
```

### Deployment:
```bash
# Instalar novas dependências
pip install hashids slowapi email-validator

# Push para produção
git add -A
git commit -m "feat: Implementar segurança (hashids, rate limiting, logging)"
git push origin main
```

## 🎯 Benefícios Implementados

| Vulnerabilidade | Antes | Depois |
|----------------|-------|--------|
| **Enumeração de IDs** | IDs sequenciais (1,2,3) | Hashes aleatórios (jR3kM9wX) |
| **Info Disclosure** | 403 revela existência | 404 genérico |
| **Brute Force** | Sem limite | 5 req/min em auth |
| **Audit Trail** | Sem logs | Logs estruturados de segurança |
| **Rate Abuse** | Ilimitado | 3-30 req/min por endpoint |

## 📊 Impacto na API

### **Mudança Breaking:**
- URLs agora usam hashes em vez de IDs
- Clients precisam usar IDs retornados pela API (já ofuscados)

### **Backward Compatibility:**
- ❌ Não compatível com IDs antigos
- ✅ Migração automática ao retornar responses

### **Exemplo de Migração Client:**
```javascript
// Antes
const response = await fetch('/api/v1/videos/1');

// Depois (usar ID do response)
const listResp = await fetch('/api/v1/videos');
const videos = await listResp.json();
const videoId = videos[0].id; // "jR3kM9wX"
const response = await fetch(`/api/v1/videos/${videoId}`);
```

## ⚠️ Avisos

1. **HASHID_SALT é secreto** - Não commitar salt real no código
2. **Rate limiting** pode bloquear testes automatizados - usar `RATE_LIMIT_ENABLED=false` em dev
3. **Logs de segurança** devem ser monitorados regularmente

## 🚀 Próximos Passos (Médio Prazo)

- [ ] Migrar para UUIDs em novos recursos
- [ ] Implementar CAPTCHA em login após 3 tentativas
- [ ] Dashboard de monitoramento de segurança
- [ ] Alertas automáticos para tentativas suspeitas
- [ ] Testes de penetração automatizados

---

**Status**: ✅ Plano de Curto Prazo 100% Implementado
**Data**: 09 de Novembro de 2025
