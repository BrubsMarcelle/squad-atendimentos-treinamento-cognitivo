"""
Router para endpoints de ranking - Boas práticas Python aplicadas.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.db.database import ranking_collection
from app.models.ranking import WeeklyRankingResponse
from app.services.checkin_service import CheckinService
from app.schemas.responses import CheckinStatusResponse
from app.utils.datetime_utils import get_current_date, get_week_id, format_date_brazilian
from app.utils.decorators import handle_exceptions, log_execution_time
from app.utils.logging import system_logger, checkin_logger
from app.utils.exceptions import DatabaseError, WeekendCheckinError, DuplicateCheckinError

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/weekly", response_model=WeeklyRankingResponse, summary="Ranking semanal")
async def get_current_weekly_ranking():
    """
    Retorna o ranking da semana atual, ordenado por pontos.
    
    Returns:
        WeeklyRankingResponse: Ranking da semana atual com informações contextuais
        
    Raises:
        DatabaseError: Erro ao consultar dados do ranking
    """
    system_logger.info("📊 Consultando ranking semanal")
    
    try:
        current_date = get_current_date()
        week_id = get_week_id(current_date)

        # Busca otimizada com projeção e limite
        ranking_cursor = ranking_collection.find(
            {"week_id": week_id},
            {"_id": 0, "username": 1, "points": 1}
        ).sort("points", -1).limit(100)

        ranking_list = await ranking_cursor.to_list(length=100)
        
        response_data = {
            "week_id": week_id, 
            "ranking": ranking_list
        }
        
        system_logger.info(
            "✅ Ranking semanal obtido com sucesso",
            {
                "week_id": week_id,
                "participants": len(ranking_list),
                "top_scorer": ranking_list[0]["username"] if ranking_list else "N/A"
            }
        )
        
        return response_data
        
    except Exception as e:
        system_logger.error(
            "Erro ao buscar ranking semanal",
            error=e,
            context={"week_id": week_id if 'week_id' in locals() else "unknown"}
        )
        raise DatabaseError("Falha ao consultar ranking semanal") from e


@router.get("/my-status", 
            response_model=CheckinStatusResponse,
            summary="Status simplificado do usuário")
async def get_my_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações essenciais para o frontend:
    - Boolean se pode fazer checkin hoje
    - Data do último checkin do usuário
    
    Args:
        current_user: Usuário autenticado via JWT
    
    Returns:
        CheckinStatusResponse: Status simplificado do usuário
        
    Raises:
        DatabaseError: Erro ao consultar dados do usuário
    """
    user_id = current_user["_id"]
    username = current_user["username"]
    
    checkin_logger.info(
        "📊 Consultando status simplificado",
        {"username": username}
    )
    
    try:
        # Verificar se pode fazer checkin usando service layer
        try:
            can_checkin_result = await CheckinService.can_user_checkin(user_id)
            can_checkin = can_checkin_result["can_checkin"]
            is_weekend = False
            already_checked_today = False
            
        except WeekendCheckinError:
            can_checkin = False
            is_weekend = True
            already_checked_today = False
            
        except DuplicateCheckinError:
            can_checkin = False
            is_weekend = False
            already_checked_today = True
        
        # Buscar último checkin
        last_checkin = await CheckinService.get_user_last_checkin(user_id)
        
        response_data = {
            "can_checkin": can_checkin,
            "last_checkin_date": last_checkin.date().isoformat() if last_checkin else None,
            "last_checkin_formatted": format_date_brazilian(last_checkin) if last_checkin else None,
            "is_weekend": is_weekend,
            "already_checked_today": already_checked_today,
            "reason": "available" if can_checkin else ("weekend" if is_weekend else ("already_checked" if already_checked_today else "unknown")),
            "message": "Você pode fazer checkin agora" if can_checkin else ("Fim de semana" if is_weekend else ("Já fez checkin hoje" if already_checked_today else "Não pode fazer checkin")),
            "today": format_date_brazilian(get_current_date())
        }
        
        checkin_logger.info(
            "✅ Status obtido com sucesso",
            {
                "username": username,
                "can_checkin": response_data["can_checkin"],
                "last_checkin": response_data["last_checkin_formatted"] or "Nunca"
            }
        )
        
        return response_data
        
    except Exception as e:
        system_logger.error(
            "Erro ao buscar status do usuário",
            error=e,
            context={"username": username}
        )
        raise DatabaseError("Falha ao consultar status do usuário") from e


@router.get("/all-time", summary="Ranking geral de todos os tempos")
async def get_all_time_ranking(current_user: dict = Depends(get_current_user)):
    """
    Retorna o ranking geral de todos os tempos, agregando pontos por usuário.
    
    Args:
        current_user: Usuário autenticado via JWT
    
    Returns:
        dict: Ranking geral com pontuações totais
        
    Raises:
        DatabaseError: Erro ao consultar dados do ranking
    """
    username = current_user["username"]
    
    system_logger.info(
        "🏆 Consultando ranking geral",
        {"requested_by": username}
    )
    
    try:
        # Pipeline de agregação para somar pontos por usuário
        pipeline = [
            {
                "$group": {
                    "_id": "$username",
                    "total_points": {"$sum": "$points"},
                    "username": {"$first": "$username"}
                }
            },
            {
                "$sort": {"total_points": -1}
            },
            {
                "$limit": 100
            },
            {
                "$project": {
                    "_id": 0,
                    "username": 1,
                    "points": "$total_points"
                }
            }
        ]
        
        ranking_cursor = ranking_collection.aggregate(pipeline)
        ranking_list = await ranking_cursor.to_list(length=100)
        
        # Encontrar posição do usuário solicitante
        user_position = None
        for idx, entry in enumerate(ranking_list):
            if entry["username"] == username:
                user_position = idx + 1
                break
        
        response_data = {
            "type": "all_time",
            "date": get_current_date().isoformat(),
            "total_participants": len(ranking_list),
            "ranking": ranking_list,
            "user_position": user_position
        }
        
        system_logger.info(
            "✅ Ranking geral obtido com sucesso",
            {
                "requested_by": username,
                "participants": len(ranking_list),
                "user_position": user_position or "N/A",
                "top_scorer": ranking_list[0]["username"] if ranking_list else "N/A"
            }
        )
        
        return response_data
        
    except Exception as e:
        system_logger.error(
            "Erro ao buscar ranking geral",
            error=e,
            context={"requested_by": username}
        )
        raise DatabaseError("Falha ao consultar ranking geral") from e
