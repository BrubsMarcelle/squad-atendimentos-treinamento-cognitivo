from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.routers import checkin_router, ranking_router, user_router
from app.db.database import user_collection, checkin_collection, ranking_collection
from pymongo import ASCENDING

app = FastAPI(
    title="Squad Atendimentos - Treinamento Cognitivo",
    version="1.0",
    contact={"brubsmarcelle2022@gmail.com": "Brubs Marcelle"},
    description="API para gamificação de check-ins diários com ranking semanal.",
    docs_url="/swagger",
    redoc_url=None,
    # Configuração OAuth2 para Swagger
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Configuração CORS - Otimizada para autenticação
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios exatos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "*",
        "Accept",
        "Accept-Language",
        "Content-Language", 
        "Content-Type",
        "Authorization",
        "WWW-Authenticate",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=[
        "WWW-Authenticate",
        "Authorization"
    ]
)

# Middleware otimizado para debugging (apenas endpoints críticos)
@app.middleware("http")
async def optimized_logging_middleware(request, call_next):
    import time
    
    # Apenas log detalhado para endpoints de auth
    is_auth_endpoint = request.url.path in ["/login", "/token", "/users"]
    
    if is_auth_endpoint:
        start_time = time.time()
        print(f"\n🔐 AUTH REQUEST: {request.method} {request.url.path}")
        
        # Headers importantes apenas
        auth_header = request.headers.get('authorization', 'None')
        content_type = request.headers.get('content-type', 'None')
        print(f"   📄 Content-Type: {content_type}")
        print(f"   🔑 Authorization: {'Present' if auth_header != 'None' else 'None'}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"   {status_emoji} Response: {response.status_code} ({process_time:.3f}s)")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            print(f"   ❌ Error: {type(e).__name__} ({process_time:.3f}s)")
            raise
    else:
        # Para outros endpoints, apenas executa sem logging detalhado
        return await call_next(request)
@app.on_event("startup")
async def startup_db_client():
    """Cria índices e verifica integridade do banco de dados no startup"""
    try:
        print("\n🚀 Iniciando configuração do banco de dados...")
        
        # Importar as funções de verificação
        from app.db.database import check_database_health, fix_username_inconsistencies
        
        # Criar índices para otimizar performance das consultas
        await user_collection.create_index([("username", ASCENDING)], unique=True)
        print("✅ Índice de username criado com sucesso")
        
        # Índice para checkins por user_id e timestamp (otimiza verificações de checkin)
        await checkin_collection.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])
        print("✅ Índice de checkins criado com sucesso")
        
        # Índice para rankings por user_id e week_id
        await ranking_collection.create_index([("user_id", ASCENDING), ("week_id", ASCENDING)])
        print("✅ Índice de rankings criado com sucesso")
        
        # Verificar saúde do banco
        health = await check_database_health()
        
        # Corrigir inconsistências se houver dados
        if health.get("users", 0) > 0:
            await fix_username_inconsistencies()
        
        print("🎉 Banco de dados configurado e verificado com sucesso!\n")
        
    except Exception as e:
        print(f"⚠️ Aviso durante configuração do banco: {e}")
        # Não falhar o startup por causa de problemas de banco
        pass

app.include_router(user_router.router)
app.include_router(checkin_router.router)
app.include_router(ranking_router.router)


@app.get("/healthcheck", summary="Verificar saúde do sistema")
async def healthcheck():
    """
    Endpoint para verificar a saúde do sistema e banco de dados.
    
    Returns:
        dict: Status de saúde do sistema
        
    Raises:
        HTTPException: Erro na verificação de saúde
    """
    from app.utils.logging import system_logger
    from app.db.database import check_database_health
    from datetime import datetime
    from app.services.logic import SAO_PAULO_TZ
    
    system_logger.info("🏥 Verificando saúde do sistema")
    
    try:
        # Verificar saúde do banco
        db_health = await check_database_health()
        
        # Informações do sistema
        current_time = datetime.now(SAO_PAULO_TZ)
        today = current_time.date()
        week_id = f"{today.year}-W{today.isocalendar()[1]}"
        
        health_data = {
            "status": "healthy",
            "timestamp": current_time.isoformat(),
            "current_date": today.isoformat(),
            "current_week": week_id,
            "database": db_health,
            "timezone": "America/Sao_Paulo (UTC-3)"
        }
        
        system_logger.info(
            "✅ Sistema saudável",
            {"database_status": db_health.get("status", "unknown")}
        )
        
        return health_data
        
    except Exception as e:
        system_logger.error("Erro na verificação de saúde", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/health", summary="Health check endpoint")
async def health():
    """
    Endpoint de health check padrão para containers Docker.
    
    Returns:
        dict: Status de saúde do sistema
    """
    return await healthcheck()

