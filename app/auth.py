# app/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core import config
from app.db.database import user_collection

# Contexto para Hashing de Senhas - Otimizado para performance
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Reduzido de 12 para 10 rounds para melhor performance
)

# Esquema OAuth2 - URL corrigida para o Swagger
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",  # Usando endpoint /token para OAuth2 form data
    scheme_name="JWT"
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"\n🔒 VERIFICANDO AUTENTICAÇÃO:")
    print(f"   🎫 Token recebido: {token[:20]}..." if token else "   ❌ Nenhum token fornecido")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"   🔍 Decodificando token JWT...")
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            print(f"   ❌ Username não encontrado no token!")
            raise credentials_exception
            
        print(f"   👤 Username extraído do token: {username}")
        print(f"   ⏰ Token expira em: {payload.get('exp', 'N/A')}")
        
    except JWTError as e:
        print(f"   ❌ Erro ao decodificar token: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    
    print(f"   🔍 Buscando usuário no banco de dados...")
    user = await user_collection.find_one({"username": username})
    
    if user is None:
        print(f"   ❌ Usuário '{username}' não encontrado no banco!")
        raise credentials_exception
        
    print(f"   ✅ Usuário autenticado com sucesso: {user.get('username', 'N/A')}")
    return user