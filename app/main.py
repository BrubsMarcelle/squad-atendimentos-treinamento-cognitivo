from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import checkin_router, ranking_router, user_router
from app.db.database import user_collection, checkin_collection, ranking_collection
from pymongo import ASCENDING

app = FastAPI(
    title="Squad Atendimentos - Treinamento Cognitivo",
    version="1.0",
    contact={"brubsmarcelle2022@gmail.com": "Brubs Marcelle"},
    description="API para gamificação de check-ins diários com ranking semanal.",
    docs_url="/swagger",
    redoc_url=None
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
    is_auth_endpoint = request.url.path in ["/login", "/users"]
    
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
    """Cria índices para otimizar performance das consultas"""
    try:
        # Índice único para username (otimiza buscas de login)
        await user_collection.create_index([("username", ASCENDING)], unique=True)
        print("✅ Índice de username criado com sucesso")
        
        # Índice para checkins por user_id e timestamp (otimiza verificações de checkin)
        await checkin_collection.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])
        print("✅ Índice de checkins criado com sucesso")
        
        # Índice para rankings por user_id e week_id
        await ranking_collection.create_index([("user_id", ASCENDING), ("week_id", ASCENDING)])
        print("✅ Índice de rankings criado com sucesso")
        
    except Exception as e:
        print(f"⚠️ Aviso ao criar índices: {e}")

app.include_router(user_router.router)
app.include_router(checkin_router.router)
app.include_router(ranking_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "API online"}


