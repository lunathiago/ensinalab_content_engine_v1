# Sistema de Autenticação - EnsinaLab Content Engine

## 📋 Visão Geral

Este sistema implementa autenticação JWT completa com registro de usuários, login, e controle de acesso baseado em ownership.

**Características:**
- ✅ Registro e login de usuários
- ✅ JWT tokens com expiração de 60 minutos
- ✅ Senha criptografada com bcrypt
- ✅ Controle de acesso por ownership (usuários só veem seus recursos)
- ✅ Suporte a roles (admin/user)
- ✅ Limites de uso (daily_video_limit, monthly_video_limit)

---

## 🚀 Configuração Inicial

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Novas dependências adicionadas:**
- `python-jose[cryptography]==3.3.0` - JWT
- `passlib[bcrypt]==1.7.4` - Password hashing

### 2. Configurar Variáveis de Ambiente

Adicione ao seu `.env`:

```env
# JWT Configuration
JWT_SECRET=seu-secret-key-super-seguro-aqui-mude-em-producao
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

⚠️ **IMPORTANTE**: Gere um secret key seguro para produção:

```bash
# Gerar secret key seguro
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Executar Migração

```bash
python scripts/add_auth_system.py
```

**O script de migração:**
- ✅ Cria tabela `users`
- ✅ Cria usuário admin padrão
- ✅ Adiciona coluna `user_id` em `briefings`
- ✅ Associa briefings existentes ao admin
- ✅ Adiciona constraints e índices

**Credenciais do Admin (para testes):**
- Email: `admin@ensinalab.com`
- Senha: `admin123`

⚠️ **Altere a senha do admin em produção!**

---

## 🔐 Endpoints de Autenticação

### 1. Registrar Novo Usuário

**POST** `/api/v1/auth/register`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gestor@escola.com",
    "username": "gestor_escola",
    "password": "senha_segura_123",
    "full_name": "João Gestor Silva"
  }'
```

**Response (201 Created):**
```json
{
  "id": 2,
  "email": "gestor@escola.com",
  "username": "gestor_escola",
  "full_name": "João Gestor Silva",
  "is_active": true,
  "is_admin": false,
  "daily_video_limit": 10,
  "monthly_video_limit": 100,
  "created_at": "2025-11-09T14:30:00"
}
```

**Erros Comuns:**
- `400`: Email ou username já existem
- `422`: Validação falhou (senha < 8 caracteres, email inválido, etc.)

### 2. Login (Obter Token)

**POST** `/api/v1/auth/login`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gestor@escola.com",
    "password": "senha_segura_123"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Erros Comuns:**
- `401`: Email ou senha incorretos
- `403`: Usuário inativo

### 3. Obter Dados do Usuário Atual

**GET** `/api/v1/auth/me`

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "id": 2,
  "email": "gestor@escola.com",
  "username": "gestor_escola",
  "full_name": "João Gestor Silva",
  "is_active": true,
  "is_admin": false,
  "daily_video_limit": 10,
  "monthly_video_limit": 100,
  "created_at": "2025-11-09T14:30:00",
  "last_login": "2025-11-09T15:00:00"
}
```

**Erros Comuns:**
- `401`: Token inválido, expirado ou ausente

---

## 🔒 Usando Autenticação em Requisições

Todos os endpoints de briefings, options e vídeos agora **requerem autenticação**.

### Padrão de Autenticação

```bash
curl -X GET "http://localhost:8000/api/v1/briefings" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Exemplo: Criar Briefing Autenticado

```bash
# 1. Login para obter token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gestor@escola.com",
    "password": "senha_segura_123"
  }' | jq -r '.access_token')

# 2. Criar briefing com token
curl -X POST "http://localhost:8000/api/v1/briefings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Metodologia Reggio Emilia",
    "target_audience": "Educadores de Educação Infantil",
    "duration_minutes": 5,
    "language": "pt-BR",
    "tone": "professional",
    "key_points": [
      "100 linguagens da criança",
      "Ambiente como terceiro educador",
      "Documentação pedagógica"
    ]
  }'
```

---

## 🎯 Controle de Acesso (Ownership)

### Princípios de Segurança

1. **Isolamento por Usuário**: Cada usuário só vê seus próprios recursos
2. **Ownership Verification**: Todas as operações verificam propriedade
3. **403 Forbidden**: Retornado ao tentar acessar recursos de outros usuários

### Exemplo de Ownership

```bash
# Usuário A cria briefing (ID=10)
curl -X POST "http://localhost:8000/api/v1/briefings" \
  -H "Authorization: Bearer TOKEN_USER_A" \
  -d '{"topic": "Matemática Lúdica", ...}'

# Usuário B tenta acessar briefing de A (ID=10)
curl -X GET "http://localhost:8000/api/v1/briefings/10" \
  -H "Authorization: Bearer TOKEN_USER_B"

# Response: 403 Forbidden
{
  "detail": "Acesso negado"
}
```

### Endpoints Protegidos

| Endpoint | Autenticação | Ownership | Descrição |
|----------|--------------|-----------|-----------|
| `POST /briefings` | ✅ | Auto (cria para user) | Cria briefing |
| `GET /briefings` | ✅ | Auto (filtra por user) | Lista próprios briefings |
| `GET /briefings/{id}` | ✅ | ✅ Verifica | Detalhes do briefing |
| `DELETE /briefings/{id}` | ✅ | ✅ Verifica | Deleta briefing |
| `GET /briefings/{id}/options` | ✅ | ✅ Verifica | Lista opções |
| `POST /options/{id}/select` | ✅ | ✅ Verifica | Seleciona opção |
| `GET /videos` | ✅ | Auto (filtra por user) | Lista vídeos |
| `GET /videos/{id}` | ✅ | ✅ Verifica | Detalhes do vídeo |
| `GET /videos/{id}/download` | ✅ | ✅ Verifica | Download vídeo |
| `POST /videos/{id}/approve` | ✅ | ✅ Verifica | Aprova vídeo |
| `POST /videos/{id}/reject` | ✅ | ✅ Verifica | Rejeita vídeo |

---

## 👥 Roles e Permissões

### User (Padrão)

```json
{
  "is_admin": false,
  "daily_video_limit": 10,
  "monthly_video_limit": 100
}
```

**Permissões:**
- ✅ Criar briefings
- ✅ Gerenciar seus briefings
- ✅ Gerar vídeos (com limites)
- ❌ Acessar recursos de outros usuários
- ❌ Gerenciar usuários

### Admin

```json
{
  "is_admin": true,
  "daily_video_limit": 10,
  "monthly_video_limit": 100
}
```

**Permissões extras (futuras):**
- ✅ Todos os recursos de User
- ✅ Ver estatísticas globais
- ✅ Gerenciar usuários (futuro)
- ✅ Ajustar limites de uso (futuro)

---

## 🔄 Fluxo Completo de Uso

### 1. Registro e Login

```bash
# 1. Registrar novo usuário
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@escola.com",
    "username": "maria_prof",
    "password": "senhaForte123!",
    "full_name": "Maria Professora"
  }'

# 2. Fazer login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@escola.com",
    "password": "senhaForte123!"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Criar Briefing

```bash
BRIEFING_ID=$(curl -X POST "http://localhost:8000/api/v1/briefings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Alfabetização Construtivista",
    "target_audience": "Professores de 1º ano",
    "duration_minutes": 7,
    "language": "pt-BR",
    "tone": "conversational",
    "key_points": [
      "Fases da escrita segundo Ferreiro",
      "Atividades de consciência fonológica",
      "Criação de ambiente alfabetizador"
    ]
  }' | jq -r '.id')

echo "Briefing criado: $BRIEFING_ID"
```

### 3. Obter Opções

```bash
# Aguardar geração das opções (workflow assíncrono)
sleep 30

# Listar opções geradas
curl -X GET "http://localhost:8000/api/v1/briefings/$BRIEFING_ID/options" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 4. Selecionar Opção e Gerar Vídeo

```bash
OPTION_ID=1  # ID da opção escolhida

VIDEO_INFO=$(curl -X POST "http://localhost:8000/api/v1/options/$OPTION_ID/select" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Gostei da abordagem prática"
  }')

VIDEO_ID=$(echo $VIDEO_INFO | jq -r '.video_id')
echo "Vídeo em geração: $VIDEO_ID"
```

### 5. Verificar Status do Vídeo

```bash
# Verificar status periodicamente
curl -X GET "http://localhost:8000/api/v1/videos/$VIDEO_ID/status" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 6. Download do Vídeo

```bash
# Quando status = "completed"
curl -X GET "http://localhost:8000/api/v1/videos/$VIDEO_ID/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o "meu_video.mp4"
```

---

## 🛡️ Segurança

### Boas Práticas Implementadas

1. **Password Hashing**: Bcrypt com salt automático
2. **JWT Signing**: HS256 com secret key
3. **Token Expiration**: 60 minutos (configurável)
4. **Stateless Auth**: Sem sessões no servidor
5. **HTTPOnly**: Frontend deve armazenar token em memória ou localStorage
6. **Ownership Checks**: Todas as operações verificam propriedade

### Recomendações para Produção

1. **Secret Key**: Gere uma chave forte e mantenha em segredo
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **HTTPS**: Use sempre em produção (tokens visíveis em HTTP)

3. **Rate Limiting**: Adicione rate limiting em endpoints de login

4. **Refresh Tokens**: Considere implementar para UX melhor

5. **Token Blacklist**: Para logout real, use Redis para blacklist

6. **Password Policy**: Enforce senhas fortes no frontend

---

## 🧪 Testes

### Testar Autenticação Completa

```bash
# Script de teste completo
#!/bin/bash

API="http://localhost:8000/api/v1"

# 1. Registrar usuário
echo "1. Registrando usuário..."
curl -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "username": "testuser",
    "password": "test123456",
    "full_name": "Test User"
  }'

# 2. Login
echo -e "\n\n2. Fazendo login..."
TOKEN=$(curl -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Verificar perfil
echo -e "\n\n3. Verificando perfil..."
curl -X GET "$API/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Criar briefing
echo -e "\n\n4. Criando briefing..."
curl -X POST "$API/briefings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Teste Auth",
    "target_audience": "Professores",
    "duration_minutes": 3,
    "language": "pt-BR",
    "tone": "professional",
    "key_points": ["Ponto 1", "Ponto 2"]
  }' | jq

# 5. Listar briefings
echo -e "\n\n5. Listando briefings..."
curl -X GET "$API/briefings" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n✅ Testes concluídos!"
```

---

## ❓ FAQ

### Como o token é validado?

O token JWT é extraído do header `Authorization: Bearer <token>`, decodificado e validado:
1. Verificação da assinatura (usando JWT_SECRET)
2. Verificação da expiração
3. Extração do `user_id` do claim `sub`
4. Busca do usuário no banco
5. Verificação se usuário está ativo

### O que acontece quando o token expira?

- Frontend recebe `401 Unauthorized`
- Usuário deve fazer login novamente
- Considere implementar refresh tokens para UX melhor

### Como fazer logout?

JWT é stateless, então:
- **Frontend**: Deletar token do localStorage/memória
- **Backend**: Token continua válido até expirar
- **Para logout real**: Implemente token blacklist com Redis

### Posso ter múltiplos tokens?

Sim! Cada login gera um novo token. Tokens antigos continuam válidos até expirar.

### Como alterar a duração do token?

No `.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=120  # 2 horas
```

### Como criar um usuário admin?

1. Registrar usuário normalmente
2. No banco, atualizar:
   ```sql
   UPDATE users SET is_admin = true WHERE email = 'admin@escola.com';
   ```

---

## 📊 Modelo de Dados

### User Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    daily_video_limit INTEGER DEFAULT 10 NOT NULL,
    monthly_video_limit INTEGER DEFAULT 100 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Briefing → User Relationship

```sql
-- Briefings pertencem a usuários
ALTER TABLE briefings ADD COLUMN user_id INTEGER NOT NULL;
ALTER TABLE briefings ADD CONSTRAINT fk_briefings_user 
    FOREIGN KEY (user_id) REFERENCES users(id);
CREATE INDEX idx_briefings_user_id ON briefings(user_id);
```

---

## 🔗 Recursos Adicionais

- [JWT.io](https://jwt.io) - Decode e debug tokens
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - Documentação oficial
- [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) - Boas práticas

---

**Implementado em**: 09 de Novembro de 2025  
**Versão do Sistema**: 0.1.0  
**Autor**: EnsinaLab Development Team
