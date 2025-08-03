from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import checkin_router, ranking_router, user_router
from app.routers import checkin_router, ranking_router
from app.db.database import user_collection
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

# Middleware avançado para debugging detalhado
@app.middleware("http")
async def detailed_logging_middleware(request, call_next):
    import time
    from datetime import datetime
    
    # Timestamp do início da requisição
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Informações da requisição
    print(f"\n{'='*80}")
    print(f"🕐 [{timestamp}] NOVA REQUISIÇÃO")
    print(f"{'='*80}")
    print(f"🌐 Método: {request.method}")
    print(f"� URL: {request.url}")
    print(f"📍 Path: {request.url.path}")
    print(f"❓ Query Params: {dict(request.query_params)}")
    print(f"🌍 Origin: {request.headers.get('origin', 'N/A')}")
    print(f"👤 User-Agent: {request.headers.get('user-agent', 'N/A')[:100]}...")
    print(f"📱 Client IP: {request.client.host if request.client else 'N/A'}")
    
    # Headers detalhados
    print(f"\n� HEADERS DA REQUISIÇÃO:")
    for name, value in request.headers.items():
        # Mascarar valores sensíveis
        if name.lower() in ['authorization', 'cookie']:
            masked_value = f"{value[:10]}..." if len(value) > 10 else "***"
            print(f"   {name}: {masked_value}")
        else:
            print(f"   {name}: {value}")
    
    # Body da requisição (se houver)
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                content_type = request.headers.get("content-type", "")
                print(f"\n📦 BODY DA REQUISIÇÃO ({len(body)} bytes):")
                
                if "application/json" in content_type:
                    try:
                        import json
                        json_body = json.loads(body.decode())
                        # Mascarar passwords
                        if isinstance(json_body, dict) and 'password' in json_body:
                            json_body['password'] = '***'
                        print(f"   JSON: {json.dumps(json_body, indent=2)}")
                    except:
                        print(f"   Raw: {body.decode()[:200]}...")
                elif "application/x-www-form-urlencoded" in content_type:
                    form_data = body.decode()
                    # Mascarar passwords
                    if 'password=' in form_data:
                        form_data = form_data.replace(form_data.split('password=')[1].split('&')[0], '***')
                    print(f"   Form: {form_data}")
                else:
                    print(f"   Raw: {body.decode()[:200]}...")
        except Exception as e:
            print(f"   ❌ Erro ao ler body: {e}")
    
    print(f"\n⚙️  PROCESSANDO REQUISIÇÃO...")
    
    # Executar a requisição
    try:
        response = await call_next(request)
        
        # Calcular tempo de resposta
        process_time = time.time() - start_time
        
        # Informações da resposta
        print(f"\n✅ RESPOSTA ENVIADA:")
        print(f"   📊 Status: {response.status_code}")
        print(f"   ⏱️  Tempo: {process_time:.3f}s")
        print(f"   � Headers da Resposta:")
        
        # Headers da resposta
        for name, value in response.headers.items():
            print(f"      {name}: {value}")
        
        # Determinar cor do status
        status_emoji = "✅" if response.status_code < 400 else "⚠️" if response.status_code < 500 else "❌"
        
        print(f"\n{status_emoji} FINALIZADO: {request.method} {request.url.path} → {response.status_code} ({process_time:.3f}s)")
        print(f"{'='*80}\n")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        print(f"\n❌ ERRO NO PROCESSAMENTO:")
        print(f"   🚨 Exceção: {type(e).__name__}: {str(e)}")
        print(f"   ⏱️  Tempo até erro: {process_time:.3f}s")
        print(f"{'='*80}\n")
        raise

@app.on_event("startup")
async def startup_db_client():
    await user_collection.create_index([("username", ASCENDING)], unique=True)

app.include_router(user_router.router)
app.include_router(checkin_router.router)
app.include_router(ranking_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "API online"}


