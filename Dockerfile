# Dockerfile para EnsinaLab Content Engine

FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretórios para uploads e vídeos
RUN mkdir -p /app/uploads /app/videos

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python", "-m", "src.app"]
