# 🔧 Fix: AttributeError em video_orientation

## 📋 Problema

### Erro Reportado
```
AttributeError: 'SimpleVideoGenerator' object has no attribute 'briefing_data'
```

### Stack Trace
```python
File "/opt/render/project/src/src/video/simple_generator.py", line 66, in generate
  slide_path = self._create_slide(...)
File "/opt/render/project/src/src/video/simple_generator.py", line 246, in _create_slide
  orientation = self.briefing_data.get('video_orientation', 'horizontal')
AttributeError: 'SimpleVideoGenerator' object has no attribute 'briefing_data'
```

### Contexto
- **Quando ocorreu:** Durante geração de vídeo após implementação da feature `video_orientation`
- **Frequência:** 100% das tentativas (3/3 retries falharam)
- **Impacto:** Geração de vídeos completamente bloqueada
- **Fase:** Criação de slides (após TTS bem-sucedido)

## 🔍 Análise da Causa Raiz

### O que aconteceu
1. Implementamos `video_orientation` no modelo `Briefing`
2. Adicionamos código em `_create_slide()` para detectar orientação: `self.briefing_data.get('video_orientation', 'horizontal')`
3. **Esquecemos** de passar/armazenar `briefing_data` no construtor ou método `generate()` do `SimpleVideoGenerator`

### Fluxo Correto (esperado)
```
Briefing (DB) 
  → VideoWorkflow (state['briefing_data']) 
    → SimpleVideoGenerator.generate(metadata) 
      → self.metadata = metadata  ❌ FALTANDO
        → _create_slide() acessa self.metadata['video_orientation']
```

### Fluxo Real (com erro)
```
Briefing (DB) 
  → VideoWorkflow (state['briefing_data']) 
    → SimpleVideoGenerator.generate(metadata) 
      → [metadata descartado]  ❌ PROBLEMA
        → _create_slide() tenta acessar self.briefing_data  ❌ NÃO EXISTE
          → AttributeError
```

## ✅ Solução Implementada

### Mudanças Realizadas

#### 1. `simple_generator.py` (linha ~50)
**Antes:**
```python
def generate(self, script: str, title: str, metadata: Dict, video_id: int) -> Dict:
    """Gera vídeo com TTS + slides"""
    try:
        print(f"📹 [SimpleGenerator] Gerando vídeo {video_id}...")
        
        # 1. Quebrar script em seções
        sections = self._parse_script_sections(script, title)
```

**Depois:**
```python
def generate(self, script: str, title: str, metadata: Dict, video_id: int) -> Dict:
    """Gera vídeo com TTS + slides"""
    try:
        print(f"📹 [SimpleGenerator] Gerando vídeo {video_id}...")
        
        # Armazenar metadata para uso nos métodos internos
        self.metadata = metadata  # ✅ NOVO
        
        # 1. Quebrar script em seções
        sections = self._parse_script_sections(script, title)
```

#### 2. `simple_generator.py` (linha ~246)
**Antes:**
```python
def _create_slide(self, title: str, content: str, slide_num: int, total_slides: int, video_id: int) -> str:
    """Cria slide visual com PIL"""
    
    # Determinar dimensões baseado na orientação
    orientation = self.briefing_data.get('video_orientation', 'horizontal')  # ❌ ERRO
```

**Depois:**
```python
def _create_slide(self, title: str, content: str, slide_num: int, total_slides: int, video_id: int) -> str:
    """Cria slide visual com PIL"""
    
    # Determinar dimensões baseado na orientação
    orientation = getattr(self, 'metadata', {}).get('video_orientation', 'horizontal')  # ✅ SEGURO
```

**Vantagens do `getattr()`:**
- ✅ Não quebra se `self.metadata` não existir (retorna `{}`)
- ✅ Default `'horizontal'` funciona em qualquer caso
- ✅ Compatível com código legado

#### 3. `video_workflow.py` (linha ~178)
**Antes:**
```python
# Preparar metadata
metadata = {
    'tone': state['briefing_data'].get('tone', 'profissional'),
    'target_audience': state['briefing_data'].get('target_audience'),
    'subject_area': state['briefing_data'].get('subject_area')
}
```

**Depois:**
```python
# Preparar metadata
metadata = {
    'tone': state['briefing_data'].get('tone', 'profissional'),
    'target_audience': state['briefing_data'].get('target_audience'),
    'subject_area': state['briefing_data'].get('subject_area'),
    'video_orientation': state['briefing_data'].get('video_orientation', 'horizontal')  # ✅ NOVO
}
```

## 🧪 Como Testar

### 1. Deploy em Produção
```bash
# O código já foi commitado e pushed
git pull origin main
docker-compose restart api worker
```

### 2. Criar Briefing com Orientação
```bash
curl -X POST https://your-api.com/api/v1/briefings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Teste Orientação Vertical",
    "description": "Teste após correção do bug",
    "target_audience": "Professores de Educação Infantil",
    "subject_area": "Pedagogia",
    "teacher_experience_level": "iniciante",
    "training_goal": "capacitação",
    "duration_minutes": 3,
    "tone": "amigável",
    "video_orientation": "vertical"  // ✅ Testar vertical
  }'
```

### 3. Verificar Logs
```bash
# Procurar por sucesso na geração
docker-compose logs worker | grep "Vídeo gerado"

# Não deve mais ter AttributeError
docker-compose logs worker | grep "AttributeError"
```

### 4. Validar Vídeo
- ✅ Vídeo deve ser criado com sucesso
- ✅ Orientação vertical: 720x1280 (9:16)
- ✅ Orientação horizontal: 1280x720 (16:9)
- ✅ Fontes e wrapping ajustados corretamente

## 📊 Testes de Regressão

### Casos de Teste
| # | Orientação | Status Esperado | Dimensões |
|---|------------|----------------|-----------|
| 1 | `vertical` | ✅ Sucesso | 720x1280 |
| 2 | `horizontal` | ✅ Sucesso | 1280x720 |
| 3 | `null` (default) | ✅ Sucesso (horizontal) | 1280x720 |
| 4 | Briefing antigo (sem campo) | ✅ Sucesso (horizontal) | 1280x720 |

### Scripts de Teste
```python
# tests/test_video_orientation_fix.py
def test_simple_generator_with_orientation():
    generator = SimpleVideoGenerator()
    
    metadata = {'video_orientation': 'vertical'}
    result = generator.generate(
        script="Teste",
        title="Teste",
        metadata=metadata,
        video_id=999
    )
    
    assert result['success'] == True
    # Verificar que orientação foi aplicada corretamente
```

## 🚀 Deploy Checklist

- [x] Código corrigido
- [x] Testes locais passaram
- [x] Commit criado com mensagem descritiva
- [x] Push para `main`
- [ ] Deploy em staging/produção
- [ ] Teste manual com briefing vertical
- [ ] Teste manual com briefing horizontal
- [ ] Monitorar logs por 24h

## 📝 Lições Aprendidas

### O que deu errado
1. **Falta de testes automatizados** para o `SimpleVideoGenerator`
2. **Não testamos** a feature completa antes do deploy
3. **Código não revisado** adequadamente (missing `self.metadata`)

### Melhorias Futuras
1. ✅ Adicionar testes unitários para `_create_slide()`
2. ✅ Validar metadata no `__init__()` ou `generate()`
3. ✅ CI/CD com testes obrigatórios antes do merge
4. ✅ Ambiente de staging para testes antes de produção

## 🔗 Referências

- **Commit:** `7267444` - fix: Corrige AttributeError em video_orientation
- **Issue:** Geração de vídeos falhando após feature video_orientation
- **PR:** (se aplicável)
- **Docs:** `VIDEO_ORIENTATION.md` - Documentação da feature

## 👥 Responsáveis

- **Bug Report:** Logs de produção (Render.com)
- **Análise:** GitHub Copilot
- **Fix:** Thiago Luna (@lunathiago)
- **Review:** (pendente)

---

**Status:** ✅ Corrigido e commitado (aguardando deploy em produção)  
**Data:** 2025-11-14  
**Versão:** 1.0.0
