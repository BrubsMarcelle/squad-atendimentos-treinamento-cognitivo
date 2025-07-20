from fastapi import FastAPI
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

@app.on_event("startup")
async def startup_db_client():
    await user_collection.create_index([("username", ASCENDING)], unique=True)

app.include_router(user_router.router)
app.include_router(checkin_router.router)
app.include_router(ranking_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "API online"}


