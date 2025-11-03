# 🔄 Mudança de Contexto: Treinamento de Professores

## 📋 Resumo da Alteração

O sistema foi **reconfigurado** de um motor que gerava conteúdo **para alunos** para um motor que gera conteúdo de **treinamento/capacitação para PROFESSORES**.

---

## ✏️ Alterações nos Campos do Briefing

### ❌ Campos Removidos (contexto de alunos)
- `target_grade` - série escolar
- `target_age_min` - idade mínima dos alunos
- `target_age_max` - idade máxima dos alunos
- `educational_goal` - objetivo pedagógico para alunos

### ✅ Campos Novos (contexto de professores)
- `target_audience` - público-alvo docente (ex: "Professores Iniciantes", "Coordenadores")
- `subject_area` - área/disciplina (ex: "Matemática", "Gestão de Sala", "Geral")
- `teacher_experience_level` - nível de experiência (ex: "Iniciante", "Intermediário", "Avançado")
- `training_goal` - objetivo do treinamento/capacitação

---

## 📝 Exemplo de Briefing (ANTES vs DEPOIS)

### ❌ ANTES (contexto de alunos)
```json
{
  "title": "Vídeo sobre Fotossíntese",
  "description": "Explicar fotossíntese para alunos do 6º ano",
  "target_grade": "6º ano",
  "target_age_min": 11,
  "target_age_max": 12,
  "educational_goal": "Compreender o processo de fotossíntese",
  "duration_minutes": 3,
  "tone": "descontraído"
}
```

### ✅ DEPOIS (contexto de professores)
```json
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

---

## 🔧 Arquivos Modificados

### 1. **Schemas** (`src/schemas/briefing.py`)
- ✅ Campos renomeados
- ✅ Descrições atualizadas para contexto docente
- ✅ Validações ajustadas

### 2. **Models** (`src/models/briefing.py`)
- ✅ Colunas do banco renomeadas
- ✅ Comentários atualizados
- ✅ Documentação ajustada

### 3. **Services** (`src/services/briefing_service.py`)
- ✅ Mapeamento de campos atualizado

### 4. **Routes** (`src/api/routes/briefings.py`)
- ✅ Documentação da API atualizada

### 5. **LLM Service** (`src/ml/llm_service.py`)
- ✅ System prompt reescrito para foco em **formação de professores**
- ✅ Prompts de geração adaptados
- ✅ Contexto atualizado: "treinamento docente" ao invés de "conteúdo para alunos"

### 6. **Workers** (`src/workers/tasks.py`)
- ✅ Campos passados para LLM atualizados

### 7. **Utils** (`src/utils/validators.py`)
- ✅ Validador de série/ano → validador de público docente

### 8. **Documentação**
- ✅ `README.md` - visão geral e exemplos atualizados
- ✅ `QUICKSTART.md` - exemplos práticos de uso
- ✅ `ARCHITECTURE.md` - diagramas e estrutura de dados
- ✅ `src/app.py` - descrição da API

---

## 🗄️ Migração do Banco de Dados

### Script de Migração
Criado: `scripts/migrate_to_teacher_training.py`

**O que faz:**
1. Renomeia `target_grade` → `target_audience`
2. Renomeia `educational_goal` → `training_goal`
3. Remove colunas `target_age_min` e `target_age_max`
4. Adiciona `subject_area` e `teacher_experience_level`

### Como Executar

**Se você JÁ tem dados no banco:**
```bash
python scripts/migrate_to_teacher_training.py
```

**Se está começando do zero:**
```bash
# Apenas crie as tabelas (já estarão corretas)
python scripts/create_tables.py
```

---

## 🎯 Exemplos de Uso (Novos)

### Exemplo 1: Gestão de Sala
```json
{
  "title": "Técnicas de Gestão de Sala de Aula",
  "description": "Estratégias práticas para manter o engajamento e disciplina",
  "target_audience": "Professores Iniciantes",
  "subject_area": "Gestão de Sala",
  "teacher_experience_level": "Iniciante",
  "training_goal": "Desenvolver habilidades de gestão comportamental",
  "duration_minutes": 5,
  "tone": "prático"
}
```

### Exemplo 2: Metodologias Ativas
```json
{
  "title": "Introdução às Metodologias Ativas",
  "description": "Como implementar aprendizagem baseada em projetos",
  "target_audience": "Todos os Professores",
  "subject_area": "Metodologias de Ensino",
  "teacher_experience_level": "Intermediário",
  "training_goal": "Aplicar metodologias ativas no planejamento das aulas",
  "duration_minutes": 8,
  "tone": "inspiracional"
}
```

### Exemplo 3: Avaliação
```json
{
  "title": "Avaliação Formativa na Prática",
  "description": "Técnicas de avaliação contínua e feedback construtivo",
  "target_audience": "Professores do Ensino Fundamental",
  "subject_area": "Avaliação",
  "teacher_experience_level": "Todos",
  "training_goal": "Implementar avaliação formativa para melhorar o aprendizado",
  "duration_minutes": 6,
  "tone": "técnico"
}
```

---

## 🤖 Prompts do LLM (Atualizado)

### System Prompt
```
Você é um especialista em FORMAÇÃO DE PROFESSORES e desenvolvimento 
profissional docente no contexto brasileiro.

Sua tarefa é gerar conteúdo para TREINAMENTO/CAPACITAÇÃO DE PROFESSORES.

IMPORTANTE:
- O público-alvo são PROFESSORES, não alunos
- Conteúdo deve ser prático, aplicável e baseado em evidências
- Considerar a realidade das escolas brasileiras
```

---

## ✅ Checklist de Migração

- [x] Schemas atualizados
- [x] Models atualizados
- [x] Services atualizados
- [x] Routes/API atualizadas
- [x] LLM prompts reescritos
- [x] Workers ajustados
- [x] Validadores atualizados
- [x] Documentação (README, QUICKSTART, ARCHITECTURE)
- [x] Script de migração do banco criado
- [x] Exemplos de uso atualizados

---

## 🚀 Próximos Passos

1. **Executar migração** (se houver dados no banco):
   ```bash
   python scripts/migrate_to_teacher_training.py
   ```

2. **Testar a API** com os novos campos:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/briefings" \
     -H "Content-Type: application/json" \
     -d @exemplo_briefing.json
   ```

3. **Validar geração de opções** pelo LLM com novo contexto

4. **Ajustar filtros** se necessário (atualmente já genéricos)

---

**🎉 Sistema agora focado em capacitação docente!**
