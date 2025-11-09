"""
Rotas de Autenticação
Gerencia registro, login e informações do usuário
"""
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from src.services.auth_service import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar novo usuário
    
    - **email**: Email válido (único)
    - **username**: Nome de usuário (único, 3-50 chars)
    - **password**: Senha (mínimo 8 caracteres)
    - **full_name**: Nome completo (opcional)
    
    Returns:
        Informações do usuário criado (sem senha)
    """
    # Verificar se email já existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Verificar se username já existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    
    # Criar usuário
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ Usuário registrado: {new_user.email} (ID: {new_user.id})")
    
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login e obter token JWT
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    
    Returns:
        Token JWT válido por 1 hora
    
    Example:
        ```bash
        curl -X POST http://localhost:8000/api/v1/auth/login \\
          -H "Content-Type: application/json" \\
          -d '{"email":"user@example.com","password":"senha123"}'
        ```
    """
    # Buscar usuário
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo. Entre em contato com o administrador."
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Atualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    print(f"✅ Login: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # em segundos
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obter informações do usuário autenticado
    
    Requer header: `Authorization: Bearer {token}`
    
    Returns:
        Informações completas do usuário logado
    
    Example:
        ```bash
        curl http://localhost:8000/api/v1/auth/me \\
          -H "Authorization: Bearer eyJhbGci..."
        ```
    """
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (opcional - JWT é stateless)
    
    Este endpoint existe para compatibilidade, mas JWT é stateless.
    O token continua válido até expirar.
    Para invalidar, o cliente deve deletar o token localmente.
    
    Para logout real, implementar blacklist de tokens (Redis).
    """
    print(f"ℹ️  Logout: {current_user.email} (token continua válido até expirar)")
    
    return {
        "message": "Logout realizado. Token será inválido em breve.",
        "note": "Delete o token localmente para logout imediato."
    }
