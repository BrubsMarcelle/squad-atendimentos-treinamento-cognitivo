"""
Router para endpoints de checkin - Boas práticas Python aplicadas.
"""
from fastapi import APIRouter, Depends, status

from app.auth import get_current_user
from app.services.checkin_service import CheckinService
from app.schemas.responses import CheckinStatusResponse, CheckinResponse
from app.utils.datetime_utils import format_date_brazilian, get_current_date
from app.utils.logging import checkin_logger
from app.utils.exceptions import WeekendCheckinError, DuplicateCheckinError

router = APIRouter(prefix="/checkin", tags=["Check-in"])


@router.get("/status", 
           response_model=CheckinStatusResponse,
           summary="Verificar status do checkin de hoje")
async def get_checkin_status(current_user: dict = Depends(get_current_user)):
    """
    Verifica se o usuário pode fazer checkin hoje e retorna informações do último checkin.
    
    Args:
        current_user: Usuário autenticado via JWT
    
    Returns:
        CheckinStatusResponse: Status detalhado do checkin (sempre 200)
    """
    user_id = current_user["_id"]
    username = current_user["username"]
    
    checkin_logger.info(
        "🔍 Verificando status de checkin",
        {"username": username, "user_id": str(user_id)}
    )
    
    try:
        # Verificar se pode fazer checkin
        can_checkin_result = await CheckinService.can_user_checkin(user_id)
        can_checkin = can_checkin_result["can_checkin"]
        
        # Buscar último checkin
        last_checkin = await CheckinService.get_user_last_checkin(user_id)
        
        response_data = {
            "can_checkin": can_checkin,
            "last_checkin_date": last_checkin.date().isoformat() if last_checkin else None,
            "last_checkin_formatted": format_date_brazilian(last_checkin) if last_checkin else None,
            "is_weekend": False,
            "already_checked_today": False,
            "reason": "available",
            "message": "Você pode fazer checkin agora",
            "today": format_date_brazilian(get_current_date())
        }
        
        checkin_logger.info(
            "✅ Status verificado - pode fazer checkin",
            {
                "username": username,
                "can_checkin": can_checkin,
                "last_checkin": response_data["last_checkin_formatted"] or "Nunca"
            }
        )
        
        return response_data
        
    except WeekendCheckinError as e:
        # Retornar 200 com informação de fim de semana
        current_date = get_current_date()
        
        response_data = {
            "can_checkin": False,
            "reason": "Hoje é final de semana",
            "message": "Check-ins são permitidos apenas de Segunda a Sexta",
            "today": current_date.isoformat(),
            "is_weekend": True,
            "already_checked_today": False,
            "last_checkin_date": None,
            "last_checkin_formatted": None
        }
        
        checkin_logger.info(
            "🚫 Status verificado - fim de semana",
            {"username": username, "date": current_date.isoformat()}
        )
        
        return response_data
        
    except DuplicateCheckinError as e:
        # Retornar 200 com informação de checkin já realizado
        current_date = get_current_date()
        last_checkin = await CheckinService.get_user_last_checkin(user_id)
        
        response_data = {
            "can_checkin": False,
            "reason": "Checkin já realizado hoje",
            "message": f"Você já fez checkin hoje às {e.details.get('checkin_time', 'N/A')}",
            "today": current_date.isoformat(),
            "is_weekend": False,
            "already_checked_today": True,
            "last_checkin_date": last_checkin.date().isoformat() if last_checkin else None,
            "last_checkin_formatted": format_date_brazilian(last_checkin) if last_checkin else None
        }
        
        checkin_logger.info(
            "🚫 Status verificado - já fez checkin",
            {
                "username": username,
                "checkin_time": e.details.get('checkin_time', 'N/A')
            }
        )
        
        return response_data
        
    except Exception as e:
        # Para outros erros, retornar informação de erro
        current_date = get_current_date()
        
        checkin_logger.error(
            "Erro inesperado ao verificar status",
            error=e,
            context={"username": username}
        )
        
        response_data = {
            "can_checkin": False,
            "reason": "Erro interno",
            "message": "Ocorreu um erro ao verificar o status. Tente novamente.",
            "today": current_date.isoformat(),
            "is_weekend": False,
            "already_checked_today": False,
            "last_checkin_date": None,
            "last_checkin_formatted": None
        }
        
        return response_data


@router.post("/", 
            status_code=status.HTTP_201_CREATED,
            response_model=CheckinResponse,
            summary="Realizar checkin")
async def perform_checkin(current_user: dict = Depends(get_current_user)):
    """
    Realiza o check-in do usuário autenticado.
    
    Args:
        current_user: Usuário autenticado via JWT
    
    Returns:
        CheckinResponse: Resultado do checkin
        
    Raises:
        WeekendCheckinError: Se for fim de semana
        DuplicateCheckinError: Se já fez checkin hoje
        DatabaseError: Erro nas operações de banco
    """
    username = current_user["username"]
    
    checkin_logger.info(
        "🔄 Iniciando processo de checkin",
        {"username": username}
    )
    
    # Processar checkin usando service layer (exceções tratadas pelo decorator)
    result = await CheckinService.process_checkin(current_user)
    
    checkin_logger.info(
        "🎉 Checkin processado com sucesso",
        {
            "username": username,
            "success": result["success"],
            "points": result.get("points_awarded", 0)
        }
    )
    
    return result