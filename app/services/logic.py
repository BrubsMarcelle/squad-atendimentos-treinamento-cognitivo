from datetime import datetime, timedelta
import pytz  # Usando pytz que está instalado
from app.db.database import user_collection, checkin_collection, ranking_collection

SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")

async def process_user_checkin(user: dict):

    now_in_sao_paulo = datetime.now(SAO_PAULO_TZ)
    today = now_in_sao_paulo.date()

    username = user["username"]
    user_id = user["_id"]

    if today.weekday() > 6:
        return {"message": "Check-ins são permitidos apenas de Segunda a Sexta."}

    start_of_day = SAO_PAULO_TZ.localize(datetime.combine(today, datetime.min.time()))
    
    if await checkin_collection.find_one({"user_id": user_id, "timestamp": {"$gte": start_of_day}}):
        return {"message": f"Usuário {username} já realizou o check-in hoje."}

    points_awarded = 0
    if not await checkin_collection.find_one({"timestamp": {"$gte": start_of_day}}):
        points_awarded = 10
    else:
        points_awarded = 5
        
    week_id = f"{today.year}-W{today.isocalendar()[1]}"
    user_ranking = await ranking_collection.find_one({"user_id": user_id, "week_id": week_id})

    if user_ranking:
        last_checkin_db = user_ranking["last_checkin_date"]
        last_checkin_date = datetime.strptime(last_checkin_db, "%Y-%m-%d").date() if isinstance(last_checkin_db, str) else last_checkin_db

        expected_previous_day = today - timedelta(days=1)
        if today.weekday() == 0:
            expected_previous_day = today - timedelta(days=3)
        
        if last_checkin_date == expected_previous_day:
            points_awarded += 2

    await checkin_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "timestamp": now_in_sao_paulo 
    })

    await ranking_collection.update_one(
        {"user_id": user_id, "week_id": week_id},
        {
            "$inc": {"points": points_awarded},
            "$set": {
                "last_checkin_date": today.strftime("%Y-%m-%d"),
                "username": username,
                "updated_at": now_in_sao_paulo
            }
        },
        upsert=True
    )

    return {
        "message": "Check-in realizado com sucesso!",
        "username": username,
        "points_awarded": points_awarded
    }