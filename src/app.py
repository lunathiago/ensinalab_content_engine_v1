"""
Configuração principal da aplicação FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.api.routes import briefings, options, videos, health

app = FastAPI(
    title="EnsinaLab Content Engine API",
    description="Motor de conteúdos para gestores escolares - gera vídeos educacionais personalizados",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - permite requisições de outros domínios
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(health.router, tags=["Health"])
app.include_router(briefings.router, prefix="/api/v1", tags=["Briefings"])
app.include_router(options.router, prefix="/api/v1", tags=["Options"])
app.include_router(videos.router, prefix="/api/v1", tags=["Videos"])

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    print("🚀 EnsinaLab Content Engine iniciado!")
    print(f"📚 Documentação: http://{settings.HOST}:{settings.PORT}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação"""
    print("👋 EnsinaLab Content Engine encerrado!")
