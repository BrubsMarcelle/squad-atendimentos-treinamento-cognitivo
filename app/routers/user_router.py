from datetime import timedelta
from typing import Union
from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.models.user import Token, UserCreate
from app.db.database import user_collection
from app.auth import get_password_hash, verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.decorators import handle_exceptions, log_execution_time
from app.utils.logging import auth_logger, system_logger, checkin_logger
from app.utils.exceptions import UserNotFoundError, DatabaseError


# Modelos de request/response
class LoginRequest(BaseModel):
    """Modelo para login via JSON."""
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    """Modelo para reset de senha."""
    username: str
    new_password: str


class UserResponse(BaseModel):
    """Modelo de resposta para usuário (sem senha)."""
    username: str


router = APIRouter(tags=["Authentication"])


@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Criar novo usuário")
async def create_user(user: UserCreate):
    """
    Cria um novo usuário no sistema.
    
    Args:
        user: Dados do usuário a ser criado
        
    Returns:
        dict: Confirmação de criação
        
    Raises:
        HTTPException: Usuário já existe ou erro interno
    """
    auth_logger.info(
        "👤 Criando novo usuário",
        {"username": user.username}
    )
    
    try:
        # Verificar se o usuário já existe
        existing_user = await user_collection.find_one({"username": user.username})
        if existing_user:
            auth_logger.warning(
                "Tentativa de criar usuário já existente",
                {"username": user.username}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        # Hash da senha e criação do usuário
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict()
        user_dict["password"] = hashed_password
        
        result = await user_collection.insert_one(user_dict)
        
        if not result.inserted_id:
            raise DatabaseError("Falha ao inserir usuário no banco de dados")
        
        auth_logger.info(
            "🎉 Usuário criado com sucesso",
            {"username": user.username, "user_id": str(result.inserted_id)}
        )
        
        return {"message": "User created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        system_logger.error(
            "Erro ao criar usuário",
            error=e,
            context={"username": user.username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.post("/login", response_model=Token, summary="Login")
async def login_json_primary(login_data: LoginRequest):
    """
    Endpoint principal de login que aceita dados JSON.
    
    Args:
        login_data: Credenciais de login em JSON
        
    Returns:
        Token: Token de acesso JWT
        
    Raises:
        HTTPException: Credenciais inválidas ou erro interno
    """
    username = login_data.username
    password = login_data.password
    
    try:
        auth_logger.info(
            "🔑 Tentativa de login JSON",
            {"username": username, "login_type": "JSON"}
        )
        
        # Busca otimizada com projeção para retornar apenas campos necessários
        user = await user_collection.find_one(
            {"username": username},
            {"username": 1, "password": 1}
        )
        
        if not user:
            # Simula tempo de verificação de senha para evitar timing attacks
            verify_password("dummy", "$2b$12$dummy.hash.to.prevent.timing.attacks")
            auth_logger.warning(
                "Login JSON negado - usuário não encontrado",
                {"username": username, "login_type": "JSON"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificação de senha
        if not verify_password(password, user["password"]):
            auth_logger.warning(
                "Login JSON negado - senha incorreta",
                {"username": username, "login_type": "JSON"}
            )
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
        
        auth_logger.info(
            "✅ Login JSON realizado com sucesso",
            {"username": user['username'], "login_type": "JSON"}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(
            "Erro interno no login JSON",
            error=e,
            context={"username": username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/token", response_model=Token, summary="Token OAuth2")
async def login_oauth2_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de token compatível com OAuth2 (form data).
    Usado para autenticação via form data, especialmente para integração OAuth2.
    
    Args:
        form_data: Dados do formulário OAuth2
        
    Returns:
        Token: Token de acesso JWT
        
    Raises:
        HTTPException: Credenciais inválidas ou erro interno
    """
    username = form_data.username
    password = form_data.password
    
    try:
        auth_logger.info(
            "🔑 Tentativa de login OAuth2",
            {"username": username, "login_type": "OAuth2"}
        )
        
        # Busca otimizada com projeção para retornar apenas campos necessários
        user = await user_collection.find_one(
            {"username": username},
            {"username": 1, "password": 1}
        )
        
        if not user:
            # Simula tempo de verificação de senha para evitar timing attacks
            verify_password("dummy", "$2b$12$dummy.hash.to.prevent.timing.attacks")
            auth_logger.warning(
                "Login OAuth2 negado - usuário não encontrado",
                {"username": username, "login_type": "OAuth2"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificação de senha
        if not verify_password(password, user["password"]):
            auth_logger.warning(
                "Login OAuth2 negado - senha incorreta",
                {"username": username, "login_type": "OAuth2"}
            )
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
        
        auth_logger.info(
            "✅ Login OAuth2 realizado com sucesso",
            {"username": user['username'], "login_type": "OAuth2"}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(
            "Erro interno no login OAuth2",
            error=e,
            context={"username": username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users", response_model=list[UserResponse], summary="Listar todos os usuários")
async def list_users():
    """
    Lista todos os usuários cadastrados (sem mostrar as senhas).
    
    Returns:
        list[UserResponse]: Lista de usuários
        
    Raises:
        DatabaseError: Erro ao consultar banco de dados
    """
    auth_logger.info("📋 Listando usuários")
    
    try:
        # Buscar todos os usuários, excluindo o campo password
        users_cursor = user_collection.find({}, {"password": 0})
        users = await users_cursor.to_list(length=None)
        
        # Converter para o modelo de resposta
        user_responses = []
        for user in users:
            user_responses.append({
                "username": user.get("username", "")
            })
        
        auth_logger.info(
            "✅ Usuários listados com sucesso",
            {
                "count": len(user_responses),
                "usernames": [u['username'] for u in user_responses]
            }
        )
        
        return user_responses
        
    except Exception as e:
        system_logger.error("Erro ao buscar usuários", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )


@router.put("/users/reset-password", summary="Reset de senha")
async def reset_password(reset_data: PasswordResetRequest):
    """
    Reseta a senha de um usuário específico.
    
    Args:
        reset_data: Dados para reset de senha
        
    Returns:
        dict: Confirmação do reset
        
    Raises:
        UserNotFoundError: Usuário não encontrado
        DatabaseError: Erro ao atualizar no banco
    """
    auth_logger.info(
        "🔐 Solicitação de reset de senha",
        {"username": reset_data.username}
    )
    
    try:
        # Verificar se o usuário existe
        user = await user_collection.find_one({"username": reset_data.username})
        if not user:
            auth_logger.warning(
                "Reset negado - usuário não encontrado",
                {"username": reset_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash da nova senha
        new_hashed_password = get_password_hash(reset_data.new_password)
        
        # Atualizar a senha no banco
        result = await user_collection.update_one(
            {"username": reset_data.username},
            {"$set": {"password": new_hashed_password}}
        )
        
        if result.modified_count != 1:
            raise DatabaseError("Falha ao atualizar senha no banco")
        
        auth_logger.info(
            "✅ Senha resetada com sucesso",
            {"username": reset_data.username}
        )
        
        return {
            "message": f"Password successfully reset for user '{reset_data.username}'",
            "username": reset_data.username
        }
            
    except HTTPException:
        raise
    except Exception as e:
        system_logger.error(
            "Erro inesperado no reset de senha",
            error=e,
            context={"username": reset_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/admin/fix-data", summary="Corrigir inconsistências de dados")
async def fix_data_inconsistencies():
    """
    Endpoint administrativo para corrigir inconsistências de dados manualmente.
    
    Returns:
        dict: Resultado da correção
        
    Raises:
        DatabaseError: Erro na correção dos dados
    """
    system_logger.info("🔧 Iniciando correção de inconsistências")
    
    try:
        from app.services.logic import fix_data_inconsistencies
        
        result = await fix_data_inconsistencies()
        
        system_logger.info(
            "✅ Inconsistências corrigidas com sucesso",
            {"corrections": result}
        )
        
        return {
            "message": "Data inconsistencies fixed successfully",
            "details": result
        }
        
    except Exception as e:
        system_logger.error("Erro na correção de dados", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fix data failed: {str(e)}"
        )