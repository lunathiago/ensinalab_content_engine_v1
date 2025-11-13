# Fix: Upload de Vídeo para R2 com Metadados em Português

## 🐛 Problema Identificado

**Data:** 2025-11-13 23:28

**Erro:**
```
❌ Erro inesperado: Parameter validation failed:
Non ascii characters found in S3 metadata for key "title", value: "Passo a Passo: Implementando a Metodologia Reggio Emilia na Educação Infantil".  
S3 metadata can only contain ASCII characters.
```

**Impacto:**
- ❌ Vídeo **NÃO foi enviado** para Cloudflare R2
- ✅ Thumbnail foi enviada com sucesso (sem metadados)
- ⚠️ Banco de dados salvou `file_path` local ao invés da URL do R2
- 📹 Vídeo gerado corretamente (137.2s, 17.6MB)
- 🔄 Workflow completou mas arquivo ficou apenas no filesystem local

## 🔍 Causa Raiz

A API S3/R2 da AWS/Cloudflare **rejeita caracteres não-ASCII nos metadados HTTP**.

**Metadados problemáticos:**
- Acentos: `á, é, í, ó, ú, â, ê, ô, ã, õ`
- Cedilha: `ç`
- Caracteres latinos: `ñ, ü`
- Símbolos: `¿, ¡`

**Localização no código:**
```python
# src/workers/tasks.py:238
video_url = storage.upload_video(
    local_path=result['video_path'],
    video_id=video_id,
    metadata={
        'title': briefing_data.get('title', f'Video {video_id}'),  # ← ACENTOS!
        'duration': result['metadata'].get('duration', 0),
        'generator_type': generator_type
    }
)
```

## ✅ Solução Implementada

### 1. Sanitização Automática de Metadados

**Arquivo:** `src/utils/storage.py`

**Função adicionada:**
```python
def _sanitize_metadata(self, metadata: Dict) -> Dict:
    """
    Remove caracteres não-ASCII dos metadados S3/R2
    
    Método:
    1. Normaliza Unicode (NFD = Decomposed)
    2. Remove marcas diacríticas (acentos, til, cedilha)
    3. Força encoding ASCII (ignora caracteres inválidos)
    
    Exemplos:
    - "Educação" → "Educacao"
    - "François" → "Francois"
    - "¿cómo?" → "como?"
    """
    sanitized = {}
    
    for key, value in metadata.items():
        str_value = str(value)
        
        # NFD: separa caracteres base + acentos
        nfd = unicodedata.normalize('NFD', str_value)
        
        # Remove Nonspacing Marks (acentos, til, etc)
        ascii_value = ''.join(
            char for char in nfd 
            if unicodedata.category(char) != 'Mn'
        )
        
        # Força ASCII puro (remove símbolos latinos)
        ascii_value = ascii_value.encode('ascii', 'ignore').decode('ascii')
        
        sanitized[key] = ascii_value
    
    return sanitized
```

### 2. Tratamento de Erros com Retry

**Estratégia de fallback:**
```python
try:
    # Tentar com metadados sanitizados
    self.client.upload_file(local_path, bucket, key, ExtraArgs=extra_args)
    
except ClientError as e:
    if "Parameter validation failed" in str(e) or "Non ascii" in str(e):
        # Retry SEM metadados (apenas ContentType + CacheControl)
        print("🔄 Tentando novamente sem metadados...")
        self.client.upload_file(
            local_path, bucket, key,
            ExtraArgs={'ContentType': 'video/mp4', 'CacheControl': 'max-age=31536000'}
        )
```

### 3. Logs Informativos

**Adicionados:**
- `⚠️ Metadados sanitizados (acentos removidos)` quando houver modificações
- `🔄 Tentando novamente sem metadados...` no retry
- `✅ Upload concluído (sem metadata)` no sucesso do retry

## 🧪 Testes Executados

**Script:** `scripts/test_storage_metadata.py`

**Cenários testados:**
1. ✅ Título com acentos portugueses
2. ✅ Título sem acentos (permanece inalterado)
3. ✅ Caracteres especiais diversos (espanhol, francês)

**Exemplos de conversão:**
| Original | Sanitizado |
|----------|-----------|
| `Educação Infantil` | `Educacao Infantil` |
| `François Müller` | `Francois Muller` |
| `¿cómo está?` | `como esta?` |
| `Introduction to Python` | `Introduction to Python` |

## 📋 Checklist de Correção

- [x] Importar `unicodedata` no `storage.py`
- [x] Implementar `_sanitize_metadata()` method
- [x] Atualizar `upload_video()` para usar sanitização
- [x] Adicionar tratamento de erro com retry
- [x] Criar logs informativos
- [x] Criar script de teste
- [x] Executar testes (3/3 passaram)
- [ ] **Reiniciar Celery worker** para carregar mudanças

## 🚀 Como Aplicar

### 1. Reiniciar Worker
```bash
# Parar worker atual
pkill -f 'celery.*worker'

# Iniciar com novo código
celery -A src.workers.celery_config worker --loglevel=info
```

### 2. Testar Upload
```bash
# Gerar novo vídeo via API
curl -X POST http://localhost:8000/api/videos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "option_id": 10,
    "generator_type": "simple"
  }'
```

### 3. Verificar Logs
**Esperado:**
```
📤 Fazendo upload do vídeo para storage...
   📤 Uploading para ensinalab-videos/videos/video_X.mp4...
   ⚠️  Metadados sanitizados (acentos removidos)
   ✅ Upload concluído: https://pub-XXX.r2.dev/videos/video_X.mp4
   🗑️  Arquivo local deletado: generated_videos/video_X_simple.mp4
```

## 🔄 Comparação: Antes vs Depois

### Antes (FALHA)
```
📤 Uploading para ensinalab-videos/videos/video_3.mp4...
❌ Erro inesperado: Parameter validation failed:
Non ascii characters found in S3 metadata for key "title"
```

**Resultado:**
- file_path: `generated_videos/video_3_simple.mp4` (local)
- Vídeo não acessível via API
- Disco do servidor cresce indefinidamente

### Depois (SUCESSO)
```
📤 Uploading para ensinalab-videos/videos/video_3.mp4...
⚠️  Metadados sanitizados (acentos removidos)
✅ Upload concluído: https://pub-XXX.r2.dev/videos/video_3.mp4
🗑️  Arquivo local deletado
```

**Resultado:**
- file_path: `https://pub-XXX.r2.dev/videos/video_3.mp4` (R2)
- Vídeo acessível publicamente
- Arquivo local deletado (economiza espaço)

## 📊 Impacto

**Benefícios:**
- ✅ Upload funciona com qualquer idioma (PT, ES, FR, DE, etc)
- ✅ Metadados preservados (mesmo sem acentos)
- ✅ Retry automático em caso de falha
- ✅ Limpeza automática de arquivos locais
- ✅ URLs públicas corretas no banco de dados

**Compatibilidade:**
- ✅ Cloudflare R2
- ✅ AWS S3
- ✅ Storage local (desenvolvimento)

## 📚 Referências

- [AWS S3 Object Metadata](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html)
- [Unicode Normalization Forms](https://unicode.org/reports/tr15/)
- [Python unicodedata Module](https://docs.python.org/3/library/unicodedata.html)
- [Cloudflare R2 S3 Compatibility](https://developers.cloudflare.com/r2/api/s3/api/)

## 🎯 Próximos Passos

1. **Reiniciar worker** com novo código
2. **Gerar vídeo de teste** com título acentuado
3. **Verificar URL** no response (`file_path` deve ser URL do R2)
4. **Monitorar disco** (não deve crescer indefinidamente)
5. **Validar metadados** no R2 dashboard (se disponível)

---

**Autor:** GitHub Copilot  
**Data:** 2025-11-13  
**Status:** ✅ Implementado | 🔄 Aguardando deploy (worker restart)
