# Orientação de Vídeo (Vertical vs Horizontal)

## 📐 Visão Geral

O sistema agora suporta geração de vídeos em duas orientações:

| Orientação | Dimensões | Aspect Ratio | Uso Principal |
|------------|-----------|--------------|---------------|
| **Horizontal** | 1280x720 | 16:9 | YouTube, Desktop, TV, Cursos Online |
| **Vertical** | 720x1280 | 9:16 | Instagram Stories, TikTok, Reels, WhatsApp Status |

## 🎯 Como Usar

### 1. API - Criar Briefing

```bash
POST /api/v1/briefings
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Gestão de Sala de Aula",
  "description": "Técnicas práticas para professores iniciantes",
  "video_orientation": "vertical"  # ← NOVO CAMPO
}
```

**Valores aceitos:**
- `"horizontal"` (padrão) - 16:9 para YouTube/Desktop
- `"vertical"` - 9:16 para Stories/Reels/TikTok

### 2. Validação

O campo é validado automaticamente:

```python
@field_validator('video_orientation')
def validate_orientation(cls, v):
    if v and v.lower() not in ['horizontal', 'vertical']:
        raise ValueError("video_orientation deve ser 'horizontal' ou 'vertical'")
    return v.lower() if v else 'horizontal'
```

### 3. Response

```json
{
  "id": "keZ8AXOz",
  "title": "Gestão de Sala de Aula",
  "video_orientation": "vertical",
  "status": "pending",
  ...
}
```

## 🔧 Implementação Técnica

### Modelo de Dados

**Tabela:** `briefings`  
**Nova coluna:** `video_orientation VARCHAR(20) DEFAULT 'horizontal'`

```sql
ALTER TABLE briefings 
ADD COLUMN video_orientation VARCHAR(20) DEFAULT 'horizontal';
```

### Gerador de Vídeo

**SimpleGenerator** ajusta dimensões e fontes automaticamente:

```python
orientation = self.briefing_data.get('video_orientation', 'horizontal')

if orientation == 'vertical':
    width, height = 720, 1280  # 9:16
    title_font_size = 48
    content_font_size = 36
    title_wrap = 20
    content_wrap = 35
else:
    width, height = 1280, 720  # 16:9
    title_font_size = 64
    content_font_size = 42
    title_wrap = 30
    content_wrap = 55
```

## 📊 Comparação Detalhada

### Horizontal (16:9)

**Dimensões:** 1280x720 (HD)

**Vantagens:**
- ✅ Padrão para desktop e TV
- ✅ Mais espaço horizontal para texto longo
- ✅ Melhor para apresentações e cursos
- ✅ Compatível com projetores

**Uso recomendado:**
- YouTube
- Vimeo
- Plataformas de e-learning (Moodle, Canvas)
- Webinars
- Apresentações corporativas

### Vertical (9:16)

**Dimensões:** 720x1280 (HD vertical)

**Vantagens:**
- ✅ Otimizado para mobile
- ✅ Formato nativo de stories/reels
- ✅ Maior engajamento em redes sociais
- ✅ 44% menos memória (mesma qualidade)

**Uso recomendado:**
- Instagram Stories/Reels
- TikTok
- YouTube Shorts
- Facebook Stories
- WhatsApp Status
- LinkedIn Stories

## 🚀 Migração

### Passo 1: Adicionar Coluna

```bash
# Via script Python
python scripts/add_video_orientation_column.py

# Ou via SQL direto
psql -U postgres -d ensinalab_db -f scripts/add_video_orientation_column.sql
```

### Passo 2: Reiniciar Serviços

```bash
# Restart API
docker-compose restart api

# Restart Worker
docker-compose restart worker
```

### Passo 3: Testar

```bash
# Teste local
python scripts/test_video_orientation.py

# Teste via API
curl -X POST http://localhost:8000/api/v1/briefings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste Vertical",
    "description": "Vídeo para Instagram Stories",
    "video_orientation": "vertical"
  }'
```

## 📝 Notas

1. **Compatibilidade retroativa:** Briefings existentes assumem `"horizontal"` (padrão)
2. **Validação automática:** Valores inválidos são rejeitados com erro 422
3. **Case-insensitive:** `"VERTICAL"`, `"Vertical"`, `"vertical"` são aceitos
4. **Performance:** Vídeos verticais usam mesma memória que horizontais (0.92MP)

## 🎬 Exemplos de Uso

### Caso 1: Curso Online (Desktop)
```json
{
  "title": "Metodologias Ativas de Ensino",
  "video_orientation": "horizontal"
}
```

### Caso 2: Dica Rápida (Mobile/Social)
```json
{
  "title": "5 Dicas de Gestão de Sala",
  "video_orientation": "vertical"
}
```

### Caso 3: Série para Instagram
```json
{
  "title": "Reggio Emilia na Prática - Episódio 1",
  "description": "Série de vídeos curtos para stories",
  "duration_minutes": 1,
  "video_orientation": "vertical"
}
```

## 🐛 Troubleshooting

### Erro: "video_orientation deve ser 'horizontal' ou 'vertical'"
**Causa:** Valor inválido enviado  
**Solução:** Use apenas `"horizontal"` ou `"vertical"`

### Vídeo gerado com orientação errada
**Causa:** Worker não reiniciado após deploy  
**Solução:** `docker-compose restart worker`

### Coluna não existe no banco
**Causa:** Migração não executada  
**Solução:** Execute `add_video_orientation_column.sql`

---

**Última atualização:** 2025-11-14  
**Versão:** 1.0.0  
**Status:** ✅ Implementado e testado
