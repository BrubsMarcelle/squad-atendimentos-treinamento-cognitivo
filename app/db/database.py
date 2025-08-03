import motor.motor_asyncio
from app.core import config

# Configuração do cliente MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
db = client[config.DATABASE_NAME]

# Acesso às coleções
user_collection = db.get_collection("users")
checkin_collection = db.get_collection("checkins")
ranking_collection = db.get_collection("weekly_rankings")

async def check_database_health():
    """Verifica a saúde do banco de dados e retorna estatísticas básicas"""
    try:
        # Contar documentos em cada coleção
        user_count = await user_collection.count_documents({})
        checkin_count = await checkin_collection.count_documents({})
        ranking_count = await ranking_collection.count_documents({})
        
        print(f"📊 Database Health Check:")
        print(f"   👥 Usuários: {user_count}")
        print(f"   ✅ Checkins: {checkin_count}")
        print(f"   🏆 Rankings: {ranking_count}")
        
        return {
            "users": user_count,
            "checkins": checkin_count,
            "rankings": ranking_count,
            "status": "healthy"
        }
    except Exception as e:
        print(f"❌ Database Health Check Failed: {e}")
        return {"status": "error", "error": str(e)}

async def fix_username_inconsistencies():
    """Corrige inconsistências de username entre coleções"""
    print("🔧 Verificando consistência de usernames...")
    
    corrections_made = 0
    
    # Corrigir checkins
    async for checkin in checkin_collection.find({}):
        user = await user_collection.find_one({"_id": checkin["user_id"]})
        if user and checkin.get("username") != user.get("username"):
            await checkin_collection.update_one(
                {"_id": checkin["_id"]},
                {"$set": {"username": user["username"]}}
            )
            corrections_made += 1
            print(f"   🔧 Corrigido username no checkin: {checkin.get('username')} → {user['username']}")
    
    # Corrigir rankings
    async for ranking in ranking_collection.find({}):
        user = await user_collection.find_one({"_id": ranking["user_id"]})
        if user and ranking.get("username") != user.get("username"):
            await ranking_collection.update_one(
                {"_id": ranking["_id"]},
                {"$set": {"username": user["username"]}}
            )
            corrections_made += 1
            print(f"   🔧 Corrigido username no ranking: {ranking.get('username')} → {user['username']}")
    
    if corrections_made == 0:
        print("   ✅ Todos os usernames estão consistentes")
    else:
        print(f"   ✅ {corrections_made} correções realizadas")
    
    return corrections_made