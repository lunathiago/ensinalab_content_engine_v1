-- Script SQL para adicionar coluna user_id nas tabelas existentes
-- Execute este script diretamente no PostgreSQL do Render

-- Adicionar coluna user_id na tabela briefings
ALTER TABLE briefings 
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Adicionar constraint de foreign key
ALTER TABLE briefings 
ADD CONSTRAINT fk_briefings_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) 
ON DELETE CASCADE;

-- Criar índice para performance
CREATE INDEX IF NOT EXISTS ix_briefings_user_id ON briefings(user_id);

-- Atualizar registros existentes (se houver) para user_id = 1 (ou NULL)
-- UPDATE briefings SET user_id = 1 WHERE user_id IS NULL;

-- Tornar coluna NOT NULL (descomente após atualizar registros existentes)
-- ALTER TABLE briefings ALTER COLUMN user_id SET NOT NULL;

SELECT 'Coluna user_id adicionada com sucesso!' as resultado;
