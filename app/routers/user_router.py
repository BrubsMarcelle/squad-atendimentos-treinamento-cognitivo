from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.user import Token, UserCreate
from app.db.database import user_collection
from app.auth import get_password_hash, verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

# Modelo para login via JSON
class LoginRequest(BaseModel):
    username: str
    password: str

# Modelo para reset de senha
class PasswordResetRequest(BaseModel):
    username: str
    new_password: str

# Modelo de resposta para usuário (sem senha)
class UserResponse(BaseModel):
    username: str
    full_name: str
    email: str

router = APIRouter(tags=["Authentication"])

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Verifica se o usuário já existe
    if await user_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    await user_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token, summary="Login otimizado")
async def login_with_json(login_data: LoginRequest):
    """
    Endpoint de login otimizado que aceita dados JSON
    """
    import time
    start_time = time.time()
    
    try:
        # Busca otimizada com projeção para retornar apenas campos necessários
        user = await user_collection.find_one(
            {"username": login_data.username},
            {"username": 1, "password": 1}  # Projeção para buscar apenas campos necessários
        )
        
        if not user:
            # Simula tempo de verificação de senha para evitar timing attacks
            verify_password("dummy", "$2b$12$dummy.hash.to.prevent.timing.attacks")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificação de senha
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Geração do token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        end_time = time.time()
        print(f"✅ Login realizado em {(end_time - start_time):.3f}s para usuário: {user['username']}")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/users", response_model=list[UserResponse], summary="Listar todos os usuários")
async def list_users():
    """
    Lista todos os usuários cadastrados (sem mostrar as senhas)
    """
    print(f"\n👥 LISTANDO USUÁRIOS:")
    print(f"   🔍 Buscando usuários no banco de dados...")
    
    try:
        # Buscar todos os usuários, excluindo o campo password
        users_cursor = user_collection.find({}, {"password": 0})
        users = await users_cursor.to_list(length=None)
        
        print(f"   ✅ {len(users)} usuários encontrados")
        
        # Converter para o modelo de resposta
        user_responses = []
        for user in users:
            user_responses.append({
                "username": user.get("username", ""),
                "full_name": user.get("full_name", ""),
                "email": user.get("email", "")
            })
        
        print(f"   📋 Usuários: {[u['username'] for u in user_responses]}")
        return user_responses
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar usuários: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )

@router.put("/users/reset-password", summary="Reset de senha")
async def reset_password(reset_data: PasswordResetRequest):
    """
    Reseta a senha de um usuário específico
    """
    print(f"\n🔐 RESET DE SENHA:")
    print(f"   👤 Usuário: {reset_data.username}")
    
    try:
        # Verificar se o usuário existe
        user = await user_collection.find_one({"username": reset_data.username})
        if not user:
            print(f"   ❌ Usuário '{reset_data.username}' não encontrado!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print(f"   ✅ Usuário encontrado")
        print(f"   🔑 Gerando hash da nova senha...")
        
        # Hash da nova senha
        new_hashed_password = get_password_hash(reset_data.new_password)
        
        # Atualizar a senha no banco
        result = await user_collection.update_one(
            {"username": reset_data.username},
            {"$set": {"password": new_hashed_password}}
        )
        
        if result.modified_count == 1:
            print(f"   ✅ Senha resetada com sucesso para '{reset_data.username}'!")
            return {
                "message": f"Password successfully reset for user '{reset_data.username}'",
                "username": reset_data.username
            }
        else:
            print(f"   ❌ Falha ao atualizar senha no banco de dados")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )