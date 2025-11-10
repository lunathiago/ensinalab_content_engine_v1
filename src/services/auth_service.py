"""
Serviço de autenticação com JWT
Gerencia tokens, hashing de senhas e verificação de usuários
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Configurações JWT (da env ou defaults)
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se senha em texto corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash bcrypt da senha
    
    Returns:
        True se senha correta, False caso contrário
    """
    # bcrypt trunca automaticamente em 72 bytes, fazemos explicitamente
    password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash bcrypt da senha
    
    Args:
        password: Senha em texto plano
    
    Returns:
        Hash bcrypt da senha
    
    Note:
        bcrypt limita senhas a 72 bytes. Senhas maiores são truncadas.
    """
    # bcrypt limita a 72 bytes - truncamos explicitamente para evitar erro
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria token JWT
    
    Args:
        data: Dados a incluir no token (ex: {"sub": user_id})
        expires_delta: Tempo de expiração customizado
    
    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT
    
    Returns:
        Payload do token
    
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obter usuário autenticado atual
    
    Uso:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    
    Args:
        credentials: Credenciais HTTP Bearer automáticas
        db: Sessão do banco de dados
    
    Returns:
        Usuário autenticado
    
    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
    except HTTPException as e:
        print(f"❌ Token decode failed: {e.detail}")
        raise
    
    user_id: int = payload.get("sub")
    if user_id is None:
        print(f"❌ Token payload missing 'sub': {payload}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: sub não encontrado",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"❌ User not found for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )
    
    if not user.is_active:
        print(f"❌ User inactive: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    print(f"✅ Authenticated: {user.email} (ID: {user.id})")
    return user
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency que garante usuário está ativo
    Redundante com get_current_user (que já verifica), mas mantido para compatibilidade
    """
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency que requer usuário admin
    
    Uso:
        @router.delete("/admin/users/{user_id}")
        def delete_user(
            user_id: int,
            admin: User = Depends(require_admin)
        ):
            ...
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente: requer admin"
        )
    return current_user
