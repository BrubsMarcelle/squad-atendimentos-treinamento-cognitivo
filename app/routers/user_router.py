from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import json

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

@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Endpoint flexível que aceita tanto form-data quanto JSON
    """
    print(f"\n🔐 PROCESSANDO LOGIN:")
    
    username = None
    password = None
    login_method = None
    
    # Verificar o Content-Type da requisição
    content_type = request.headers.get("content-type", "")
    print(f"   📄 Content-Type detectado: {content_type}")
    
    if "application/json" in content_type:
        # Se for JSON, ler o body diretamente
        login_method = "JSON"
        print(f"   🔄 Processando login via JSON...")
        try:
            body = await request.body()
            json_data = json.loads(body)
            username = json_data.get("username")
            password = json_data.get("password")
            print(f"   👤 Username extraído: {username}")
            print(f"   🔑 Password fornecido: {'✅' if password else '❌'}")
        except Exception as e:
            print(f"   ❌ Erro ao processar JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid JSON format"
            )
    else:
        # Se for form-data, usar o OAuth2PasswordRequestForm
        login_method = "FORM-DATA"
        print(f"   🔄 Processando login via Form-Data...")
        username = form_data.username
        password = form_data.password
        print(f"   👤 Username extraído: {username}")
        print(f"   🔑 Password fornecido: {'✅' if password else '❌'}")
    
    if not username or not password:
        print(f"   ❌ Campos obrigatórios ausentes!")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )
    
    print(f"   🔍 Buscando usuário no banco de dados...")
    user = await user_collection.find_one({"username": username})
    
    if not user:
        print(f"   ❌ Usuário '{username}' não encontrado!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"   ✅ Usuário encontrado: {user.get('username', 'N/A')}")
    print(f"   🔐 Verificando senha...")
    
    if not verify_password(password, user["password"]):
        print(f"   ❌ Senha incorreta para usuário '{username}'!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"   ✅ Senha verificada com sucesso!")
    print(f"   🎫 Gerando token de acesso...")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    print(f"   ✅ Token gerado com sucesso!")
    print(f"   ⏰ Expira em: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
    print(f"   🎉 LOGIN REALIZADO COM SUCESSO via {login_method}!")
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, summary="Login com JSON")
async def login_with_json(login_data: LoginRequest):
    """
    Endpoint de login que aceita dados JSON (para frontends modernos)
    """
    user = await user_collection.find_one({"username": login_data.username})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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