from fastapi import APIRouter
from datetime import date
from app.db.database import ranking_collection
from app.models.ranking import WeeklyRankingResponse

router = APIRouter(prefix="/ranking", tags=["Ranking"])

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