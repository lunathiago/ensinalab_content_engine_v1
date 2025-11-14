-- Migração: Adiciona coluna video_orientation à tabela briefings
-- Execução: psql -U postgres -d ensinalab_db -f scripts/add_video_orientation_column.sql

-- Verificar se coluna já existe antes de adicionar
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='briefings' 
        AND column_name='video_orientation'
    ) THEN
        -- Adicionar coluna
        ALTER TABLE briefings 
        ADD COLUMN video_orientation VARCHAR(20) DEFAULT 'horizontal';
        
        -- Atualizar registros existentes
        UPDATE briefings 
        SET video_orientation = 'horizontal' 
        WHERE video_orientation IS NULL;
        
        RAISE NOTICE 'Coluna video_orientation adicionada com sucesso!';
    ELSE
        RAISE NOTICE 'Coluna video_orientation já existe. Nada a fazer.';
    END IF;
END $$;

-- Verificar resultado
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'briefings' 
AND column_name = 'video_orientation';
