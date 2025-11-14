# Guia de Scripts de Banco de Dados

## 📚 Scripts Disponíveis

### 1. `create_tables.py` - Criar Tabelas (Fresh Install)

**Uso:** Primeira instalação, banco vazio

```bash
python scripts/create_tables.py
```

**O que faz:**
- ✅ Cria todas as tabelas se não existirem
- ✅ Preserva dados existentes
- ✅ Inclui todos os campos (incluindo `video_orientation`)
- ⚠️ **NÃO** adiciona colunas faltantes em tabelas existentes

**Quando usar:**
- Setup inicial do projeto
- Ambiente de desenvolvimento novo
- Após `DROP DATABASE`

---

### 2. `recreate_tables.py` - Dropar e Recriar Todas (⚠️ DESTRUTIVO)

**Uso:** Reset completo do banco

```bash
python scripts/recreate_tables.py
```

**O que faz:**
- 🗑️ **DELETA TODOS OS DADOS**
- 🔄 Dropa todas as tabelas
- ✅ Recria tabelas do zero
- ✅ Estrutura sempre atualizada

**Quando usar:**
- ⚠️ **APENAS EM DEV/TESTES**
- Reset completo do ambiente
- Após mudanças grandes no schema
- Limpar dados de teste

**⚠️ ATENÇÃO:** Não use em produção!

---

### 3. `add_video_orientation_column.py` - Migração Específica

**Uso:** Adicionar coluna `video_orientation` em banco existente

```bash
python scripts/add_video_orientation_column.py
```

**O que faz:**
- ✅ Adiciona coluna `video_orientation` se não existir
- ✅ Define default `'horizontal'`
- ✅ Atualiza registros existentes
- ✅ Idempotente (pode executar múltiplas vezes)

**Quando usar:**
- Banco em produção com dados
- Atualizar de versão antiga para nova
- Não quer perder dados

---

### 4. `add_video_orientation_column.sql` - Migração SQL

**Uso:** Execução direta no PostgreSQL

```bash
psql -U postgres -d ensinalab_db -f scripts/add_video_orientation_column.sql
```

**O que faz:**
- ✅ Mesma funcionalidade que `.py`
- ✅ Mais rápido (SQL direto)
- ✅ Idempotente

---

### 5. `test_table_structure.py` - Validar Estrutura

**Uso:** Verificar se modelos estão corretos

```bash
python scripts/test_table_structure.py
```

**O que faz:**
- ✅ Lista todos os campos esperados
- ✅ Verifica se `video_orientation` está presente
- ✅ Valida defaults e relationships
- ✅ Testa enums

---

## 🎯 Cenários Comuns

### Cenário 1: Primeira Instalação (Banco Vazio)

```bash
# Opção A: Criar tabelas
python scripts/create_tables.py

# Opção B: Recriar (mesmo resultado se banco vazio)
python scripts/recreate_tables.py
```

**Resultado:** Todas as tabelas criadas incluindo `video_orientation`

---

### Cenário 2: Atualizar Produção (Banco com Dados)

```bash
# Executar migração
python scripts/add_video_orientation_column.py

# OU via SQL
psql -U postgres -d ensinalab_db -f scripts/add_video_orientation_column.sql
```

**Resultado:** Coluna adicionada, dados preservados

---

### Cenário 3: Reset Completo de Dev

```bash
# ⚠️ CUIDADO: Deleta tudo!
python scripts/recreate_tables.py
```

**Resultado:** Banco limpo com estrutura atualizada

---

### Cenário 4: Verificar Estrutura Atual

```bash
# Testar modelos
python scripts/test_table_structure.py
```

**Resultado:** Lista de todos os campos e validações

---

## 📋 Estrutura Completa das Tabelas

### `briefings`

```sql
CREATE TABLE briefings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    target_audience VARCHAR(100),
    subject_area VARCHAR(100),
    teacher_experience_level VARCHAR(50),
    training_goal TEXT,
    duration_minutes INTEGER,
    tone VARCHAR(100),
    video_orientation VARCHAR(20) DEFAULT 'horizontal',  -- ← NOVO
    task_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `options`

```sql
CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER NOT NULL REFERENCES briefings(id),
    title VARCHAR(255),
    summary TEXT,
    script_outline TEXT,
    key_points JSONB,
    estimated_duration INTEGER,
    tone VARCHAR(100),
    approach VARCHAR(100),
    relevance_score FLOAT,
    quality_score FLOAT,
    is_selected BOOLEAN DEFAULT FALSE,
    selection_notes TEXT,
    extra_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `videos`

```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    option_id INTEGER NOT NULL REFERENCES options(id),
    title VARCHAR(255),
    description TEXT,
    script TEXT,
    duration_seconds FLOAT,
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    thumbnail_path VARCHAR(500),
    generator_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'queued',
    progress FLOAT DEFAULT 0.0,
    error_message TEXT,
    task_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## ⚙️ Configuração

**Database URL** (`.env`):

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ensinalab_db
```

---

## 🔍 Troubleshooting

### Erro: "column video_orientation does not exist"

**Causa:** Banco antigo sem migração

**Solução:**
```bash
python scripts/add_video_orientation_column.py
```

---

### Erro: "table already exists"

**Causa:** `create_tables.py` em banco com tabelas

**Solução:** Normal! Script não falha, apenas avisa

---

### Erro: "cannot drop table briefings because other objects depend on it"

**Causa:** Foreign keys bloqueando drop

**Solução:** Use `recreate_tables.py` que dropa na ordem correta

---

## 📊 Comparação de Scripts

| Script | Cria Tabelas | Preserva Dados | Adiciona Colunas | Uso |
|--------|--------------|----------------|------------------|-----|
| `create_tables.py` | ✅ | ✅ | ❌ | Fresh install |
| `recreate_tables.py` | ✅ | ❌ | ✅ | Reset dev |
| `add_video_orientation_column.py` | ❌ | ✅ | ✅ | Migração prod |
| `add_video_orientation_column.sql` | ❌ | ✅ | ✅ | Migração prod (SQL) |
| `test_table_structure.py` | ❌ | N/A | ❌ | Validação |

---

**Última atualização:** 2025-11-14  
**Versão do Schema:** 1.1.0 (com `video_orientation`)
