# Migração: Adicionar coluna metadata na tabela options

## Contexto

A coluna `metadata` (tipo JSON) foi adicionada ao modelo `Option` para armazenar dados extras gerados pelos agentes LangGraph durante a geração de opções, como:

- `alignment_score`: Score de alinhamento com o briefing
- `overall_score`: Score geral combinado
- `rank`: Posição no ranking
- `passed_filters`: Status de aprovação nos filtros
- `ranking_rationale`: Justificativa do ranking

## Como aplicar a migração

### No Render (Produção)

1. Acesse o **Shell** do serviço `ensinalab-api` no Render
2. Execute o script de migração:

```bash
python -m scripts.add_metadata_column
```

3. Verifique a saída:
   - ✅ "Coluna metadata adicionada com sucesso!" → Migração aplicada
   - ℹ️ "Coluna metadata já existe" → Já foi aplicada anteriormente

### Localmente (Desenvolvimento)

```bash
# Com ambiente virtual ativado
python -m scripts.add_metadata_column
```

## Verificação

Após aplicar a migração, crie um novo briefing e verifique que as opções são geradas com sucesso:

```bash
# Criar briefing
curl -X POST https://ensinalab-api.onrender.com/api/v1/briefings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste Metadata",
    "description": "Validando coluna metadata",
    "target_audience": "Professores",
    "subject_area": "Geral",
    "teacher_experience_level": "intermediário",
    "training_goal": "Teste",
    "duration_minutes": 10,
    "tone": "prático"
  }'

# Aguardar processamento (~10-30 segundos)

# Listar opções (verificar campo metadata)
curl https://ensinalab-api.onrender.com/api/v1/briefings/{id}/options
```

O campo `metadata` deve conter um objeto JSON com os dados extras dos agentes.

## Rollback (se necessário)

Caso precise reverter:

```sql
ALTER TABLE options DROP COLUMN metadata;
```

⚠️ **Atenção**: Isso apagará todos os dados extras armazenados.

## Status

- ✅ Modelo `Option` atualizado
- ✅ Schema `OptionResponse` atualizado
- ✅ Service `OptionService` atualizado para popular metadata
- ✅ Script de migração criado
- ⏳ **Pendente**: Executar migração no banco de dados do Render
