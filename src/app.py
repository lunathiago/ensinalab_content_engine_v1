"""
Configuração principal da aplicação FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.config.settings import settings
from src.config.rate_limit import limiter
from src.api.routes import auth, briefings, options, videos, health

# Importar models para registrá-los no SQLAlchemy Base
from src.models.user import User
from src.models.briefing import Briefing
from src.models.option import Option
from src.models.video import Video

app = FastAPI(
    title="EnsinaLab Content Engine API",
    description="Motor de conteúdos para gestores escolares - gera vídeos de treinamento/capacitação de professores personalizados",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - permite requisições de outros domínios
cors_origins = settings.get_cors_origins()
print(f"🌐 CORS configurado para: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
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
