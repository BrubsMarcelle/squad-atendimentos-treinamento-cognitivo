from datetime import datetime, timedelta, date
from app.db.database import user_collection, checkin_collection, ranking_collection

async def process_user_checkin(username: str):
    now = datetime.utcnow()
    today = now.date() # <--- today é um datetime.date

    # Regra: Ranking é de Segunda (0) a Sexta (4)
    # Para testes coloquei para até domingo
    if today.weekday() > 6: # Isso só seria True se weekday() retornasse 7, o que não acontece. Max é 6 (domingo).
        return {"message": "Check-ins são permitidos apenas de Segunda a Sexta."}

    # 1. Obter ou criar o usuário
    user = await user_collection.find_one_and_update(
        {"username": username},
        {"$setOnInsert": {"username": username, "created_at": now}},
        upsert=True,
        return_document=True
    )
    user_id = user["_id"]

    # 2. Verificar se já fez check-in hoje
    start_of_day = datetime.combine(today, datetime.min.time()) 
    if await checkin_collection.find_one({"user_id": user_id, "timestamp": {"$gte": start_of_day}}):
        return {"message": f"Usuário {username} já realizou o check-in hoje."}

    # 3. Calcular pontos
    points_awarded = 0

    # 3.1 Ponto base (Primeiro do dia ou não)
    if not await checkin_collection.find_one({"timestamp": {"$gte": start_of_day}}):
        points_awarded = 10  # Primeiro do dia
    else:
        points_awarded = 5   # Demais

    # 3.2 Bônus por dias consecutivos
    week_id = f"{today.year}-W{today.isocalendar()[1]}"
    user_ranking = await ranking_collection.find_one({"user_id": user_id, "week_id": week_id})

    if user_ranking:
        # Ao recuperar, last_checkin_date será um datetime.datetime.
        # Converta para date para a comparação consistente com 'expected_previous_day'
        last_checkin = user_ranking["last_checkin_date"].date() # <--- Adicione .date() aqui
        
        # Define o "dia anterior válido"
        expected_previous_day = today - timedelta(days=1)
        if today.weekday() == 0:  # Se hoje é segunda, o anterior válido é sexta
            expected_previous_day = today - timedelta(days=3)
        
        if last_checkin == expected_previous_day:
            points_awarded += 2

    # 4. Salvar o log do check-in
    await checkin_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "timestamp": now 
    })

    # 5. Atualizar o ranking semanal (a operação mais importante)
    await ranking_collection.update_one(
        {"user_id": user_id, "week_id": week_id},
        {
            "$inc": {"points": points_awarded},
            "$set": {
                "last_checkin_date": datetime.combine(today, datetime.min.time()), 
                "username": username,
                "updated_at": now 
            }
        },
        upsert=True
    )

    return {
        "message": "Check-in realizado com sucesso!",
        "username": username,
        "points_awarded": points_awarded
    }