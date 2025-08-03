from fastapi import APIRouter, Depends
from datetime import date, datetime, timezone, timedelta
from app.db.database import ranking_collection, checkin_collection
from app.models.ranking import WeeklyRankingResponse
from app.auth import get_current_user

router = APIRouter(prefix="/ranking", tags=["Ranking"])

# Timezone de São Paulo: UTC-3
SAO_PAULO_TZ = timezone(timedelta(hours=-3))

@router.get("/weekly", response_model=WeeklyRankingResponse)
async def get_current_weekly_ranking():
    """Retorna o ranking da semana atual, ordenado por pontos."""
    today = date.today()
    week_id = f"{today.year}-W{today.isocalendar()[1]}"

    ranking_cursor = ranking_collection.find(
        {"week_id": week_id},
        {"_id": 0, "username": 1, "points": 1} # Projeção para retornar apenas campos necessários
    ).sort("points", -1).limit(100) # Ordena e limita o resultado

    ranking_list = await ranking_cursor.to_list(length=100)
    
    return {"week_id": week_id, "ranking": ranking_list}

@router.get("/my-status", summary="Status simplificado do usuário - checkin e última data")
async def get_my_ranking_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações essenciais para o frontend:
    - Boolean se pode fazer checkin hoje
    - Data do último checkin do usuário
    """
    try:
        now_in_sao_paulo = datetime.now(SAO_PAULO_TZ)
        today = now_in_sao_paulo.date()
        user_id = current_user["_id"]
        username = current_user["username"]
        
        print(f"\n📊 STATUS SIMPLIFICADO - USUÁRIO: {username}")
        
        # Verificar se é fim de semana
        is_weekend = today.weekday() > 4  # 0-4 = Segunda a Sexta, 5-6 = Sábado e Domingo
        
        # Buscar checkin de hoje
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=SAO_PAULO_TZ)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=SAO_PAULO_TZ)
        
        today_checkin = await checkin_collection.find_one({
            "user_id": user_id,
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        })
        
        # Buscar último checkin geral (qualquer dia)
        last_checkin = await checkin_collection.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        # Determinar se pode fazer checkin
        can_checkin = not is_weekend and not today_checkin
        
        # Preparar data do último checkin
        last_checkin_date = None
        last_checkin_formatted = None
        
        if last_checkin:
            last_checkin_date = last_checkin["timestamp"].date().isoformat()  # Formato: 2025-08-03
            last_checkin_formatted = last_checkin["timestamp"].strftime("%d/%m/%Y")  # Formato: 03/08/2025
        
        result = {
            "can_checkin": can_checkin,
            "last_checkin_date": last_checkin_date,  # ISO format para processamento
            "last_checkin_formatted": last_checkin_formatted,  # Formato brasileiro para exibição
            "is_weekend": is_weekend,
            "already_checked_today": bool(today_checkin)
        }
        
        print(f"   ✅ Pode fazer checkin: {can_checkin}")
        print(f"   � Último checkin: {last_checkin_formatted or 'Nunca'}")
        print(f"   🏖️ É fim de semana: {is_weekend}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar status: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user status: {str(e)}"
        )