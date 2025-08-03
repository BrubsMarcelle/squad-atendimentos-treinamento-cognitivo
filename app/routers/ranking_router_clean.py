"""
Router para endpoints de ranking - Clean Code aplicado.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.db.database import ranking_collection
from app.models.ranking import WeeklyRankingResponse
from app.services.checkin_service import CheckinService
from app.schemas.responses import CheckinStatusResponse
from app.utils.datetime_utils import get_current_date, get_week_id, format_date_brazilian

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/weekly", response_model=WeeklyRankingResponse)
async def get_current_weekly_ranking():
    """
    Retorna o ranking da semana atual, ordenado por pontos.
    
    Returns:
        WeeklyRankingResponse: Ranking da semana atual
    """
    current_date = get_current_date()
    week_id = get_week_id(current_date)

    ranking_cursor = ranking_collection.find(
        {"week_id": week_id},
        {"_id": 0, "username": 1, "points": 1}  # Projeção otimizada
    ).sort("points", -1).limit(100)

    ranking_list = await ranking_cursor.to_list(length=100)
    
    return {"week_id": week_id, "ranking": ranking_list}


@router.get("/my-status", 
           response_model=CheckinStatusResponse,
           summary="Status simplificado do usuário")
async def get_my_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações essenciais para o frontend:
    - Boolean se pode fazer checkin hoje
    - Data do último checkin do usuário
    
    Returns:
        CheckinStatusResponse: Status simplificado do usuário
    """
    try:
        user_id = current_user["_id"]
        username = current_user["username"]
        
        print(f"\n📊 STATUS SIMPLIFICADO - USUÁRIO: {username}")
        
        # Verificar se pode fazer checkin
        can_checkin_result = await CheckinService.can_user_checkin(user_id)
        
        # Buscar último checkin
        last_checkin = await CheckinService.get_user_last_checkin(user_id)
        
        response_data = {
            "can_checkin": can_checkin_result["can_checkin"],
            "last_checkin_date": last_checkin.date().isoformat() if last_checkin else None,
            "last_checkin_formatted": format_date_brazilian(last_checkin) if last_checkin else None,
            "is_weekend": can_checkin_result.get("reason") == "weekend",
            "already_checked_today": can_checkin_result.get("reason") == "already_checked_in"
        }
        
        print(f"   ✅ Pode fazer checkin: {response_data['can_checkin']}")
        print(f"   📅 Último checkin: {response_data['last_checkin_formatted'] or 'Nunca'}")
        
        return response_data
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user status: {str(e)}"
        )
