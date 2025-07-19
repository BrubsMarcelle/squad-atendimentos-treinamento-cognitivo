import motor.motor_asyncio
from app.core import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
db = client[config.DATABASE_NAME]

# Acesso às coleções
user_collection = db.get_collection("users")
checkin_collection = db.get_collection("checkins")
ranking_collection = db.get_collection("weekly_rankings")