"""
Service layer para lógica de checkin - Boas práticas Python aplicadas.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId

from app.db.database import user_collection, checkin_collection, ranking_collection
from app.utils.constants import POINTS, MESSAGES
from app.utils.datetime_utils import (
    get_current_datetime, get_current_date, get_start_of_day, 
    is_weekend, get_week_id, format_time_brazilian
)
from app.utils.exceptions import (
    WeekendCheckinError, DuplicateCheckinError, DatabaseError
)
from app.utils.decorators import handle_checkin_exceptions, log_checkin_operation
from app.utils.logging import checkin_logger


class CheckinService:
    """Serviço responsável pela lógica de checkin."""
    
    @staticmethod
    # @handle_checkin_exceptions  # Temporariamente desabilitado para permitir tratamento no router
    # @log_checkin_operation("verificacao_checkin")  # Temporariamente desabilitado
    async def can_user_checkin(user_id: ObjectId) -> Dict:
        """
        Verifica se o usuário pode fazer checkin hoje.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com status e informações relevantes
            
        Raises:
            WeekendCheckinError: Se for fim de semana
            DuplicateCheckinError: Se já fez checkin hoje
        """
        current_date = get_current_date()
        
        # Verificar fim de semana
        if is_weekend(current_date):
            raise WeekendCheckinError(current_date.isoformat())
        
        # Verificar se já fez checkin hoje
        start_of_day = get_start_of_day(current_date)
        
        try:
            existing_checkin = await checkin_collection.find_one({
                "user_id": user_id,
                "timestamp": {"$gte": start_of_day}
            })
        except Exception as e:
            raise DatabaseError(
                message="Erro ao verificar checkin existente",
                error_code="DB_CHECKIN_QUERY_ERROR",
                details={"user_id": str(user_id), "date": current_date.isoformat()}
            ) from e
        
        if existing_checkin:
            checkin_time = format_time_brazilian(existing_checkin["timestamp"])
            username = existing_checkin.get("username", "Unknown")
            raise DuplicateCheckinError(username, checkin_time)
        
        return {
            "can_checkin": True,
            "reason": "available",
            "message": "Pode realizar checkin"
        }
    
    @staticmethod
    @handle_checkin_exceptions
    @log_checkin_operation("busca_ultimo_checkin")  
    async def get_user_last_checkin(user_id: ObjectId) -> Optional[datetime]:
        """
        Busca o último checkin do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Datetime do último checkin ou None se não houver
            
        Raises:
            DatabaseError: Erro na consulta ao banco
        """
        try:
            last_checkin = await checkin_collection.find_one(
                {"user_id": user_id},
                sort=[("timestamp", -1)]
            )
            return last_checkin["timestamp"] if last_checkin else None
        except Exception as e:
            raise DatabaseError(
                message="Erro ao buscar último checkin",
                error_code="DB_LAST_CHECKIN_ERROR",
                details={"user_id": str(user_id)}
            ) from e
    
    @staticmethod
    @handle_checkin_exceptions
    @log_checkin_operation("calculo_pontos")
    async def calculate_points(user_id: ObjectId) -> int:
        """
        Calcula os pontos que o usuário deve receber.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Quantidade de pontos a ser atribuída
            
        Raises:
            DatabaseError: Erro nas consultas ao banco
        """
        current_date = get_current_date()
        start_of_day = get_start_of_day(current_date)
        
        try:
            # Verificar se é o primeiro checkin do dia
            first_checkin_today = await checkin_collection.find_one({
                "timestamp": {"$gte": start_of_day}
            })
            
            base_points = (POINTS['FIRST_CHECKIN_OF_DAY'] 
                          if not first_checkin_today 
                          else POINTS['REGULAR_CHECKIN'])
            
            # Calcular streak bonus
            streak_bonus = await CheckinService._calculate_streak_bonus(user_id)
            total_points = base_points + streak_bonus
            
            # Log detalhado do cálculo
            checkin_logger.points_calculation(
                username="user_" + str(user_id)[-6:],  # Últimos 6 chars do ID
                base_points=base_points,
                streak_bonus=streak_bonus,
                total=total_points
            )
            
            return total_points
            
        except Exception as e:
            if not isinstance(e, DatabaseError):
                raise DatabaseError(
                    message="Erro no cálculo de pontos",
                    error_code="POINTS_CALCULATION_ERROR",
                    details={"user_id": str(user_id)}
                ) from e
            raise
    
    @staticmethod
    async def _calculate_streak_bonus(user_id: ObjectId) -> int:
        """
        Calcula bônus de streak.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Pontos de bônus por streak
        """
        current_date = get_current_date()
        week_id = get_week_id(current_date)
        
        try:
            user_ranking = await ranking_collection.find_one({
                "user_id": user_id, 
                "week_id": week_id
            })
            
            if not user_ranking:
                return 0
            
            last_checkin_db = user_ranking.get("last_checkin_date")
            if not last_checkin_db:
                return 0
            
            # Converter string para date se necessário
            if isinstance(last_checkin_db, str):
                last_checkin_date = datetime.strptime(last_checkin_db, "%Y-%m-%d").date()
            else:
                last_checkin_date = last_checkin_db
            
            # Calcular dia anterior esperado
            expected_previous_day = current_date - timedelta(days=1)
            if current_date.weekday() == 0:  # Segunda-feira
                expected_previous_day = current_date - timedelta(days=3)  # Sexta anterior
            
            if last_checkin_date == expected_previous_day:
                checkin_logger.info(
                    "🔥 Streak bonus aplicado",
                    {
                        "user_id": str(user_id),
                        "last_checkin": last_checkin_date.isoformat(),
                        "expected": expected_previous_day.isoformat()
                    }
                )
                return POINTS['STREAK_BONUS']
            
            return 0
            
        except Exception as e:
            checkin_logger.error(
                "Erro no cálculo de streak bonus",
                error=e,
                context={"user_id": str(user_id)}
            )
            return 0  # Em caso de erro, não aplicar bonus
    
    @staticmethod
    @handle_checkin_exceptions
    @log_checkin_operation("processo_checkin")
    async def process_checkin(user: Dict) -> Dict:
        """
        Processa o checkin do usuário.
        
        Args:
            user: Dados do usuário autenticado
            
        Returns:
            Dict com resultado do checkin
            
        Raises:
            WeekendCheckinError: Se for fim de semana
            DuplicateCheckinError: Se já fez checkin hoje
            DatabaseError: Erro nas operações de banco
        """
        user_id = user["_id"]
        username = user["username"]
        current_datetime = get_current_datetime()
        current_date = current_datetime.date()
        
        checkin_logger.checkin_attempt(username, str(user_id))
        
        start_time = time.time()
        
        try:
            # Verificar se pode fazer checkin (já lança exceções apropriadas)
            await CheckinService.can_user_checkin(user_id)
            
            # Calcular pontos
            points_awarded = await CheckinService.calculate_points(user_id)
            
            # Salvar checkin
            checkin_data = {
                "user_id": user_id,
                "username": username,
                "timestamp": current_datetime
            }
            
            checkin_result = await checkin_collection.insert_one(checkin_data)
            
            checkin_logger.database_operation(
                operation="insert_checkin",
                collection="checkins",
                success=bool(checkin_result.inserted_id)
            )
            
            # Atualizar ranking
            week_id = get_week_id(current_date)
            ranking_update = {
                "$inc": {"points": points_awarded},
                "$set": {
                    "last_checkin_date": current_date.strftime("%Y-%m-%d"),
                    "username": username,
                    "updated_at": current_datetime
                }
            }
            
            ranking_result = await ranking_collection.update_one(
                {"user_id": user_id, "week_id": week_id},
                ranking_update,
                upsert=True
            )
            
            checkin_logger.database_operation(
                operation="update_ranking",
                collection="rankings",
                success=bool(ranking_result.acknowledged)
            )
            
            # Log de sucesso
            duration = (time.time() - start_time) * 1000
            checkin_logger.checkin_success(username, points_awarded, duration)
            
            return {
                "success": True,
                "message": MESSAGES['CHECKIN_SUCCESS'],
                "username": username,
                "points_awarded": points_awarded,
                "can_checkin": False,
                "reason": "checkin_completed"
            }
            
        except (WeekendCheckinError, DuplicateCheckinError):
            # Re-raise exceções de negócio
            raise
        except Exception as e:
            # Converter outros erros em DatabaseError
            raise DatabaseError(
                message="Erro no processamento do checkin",
                error_code="CHECKIN_PROCESS_ERROR",
                details={
                    "username": username,
                    "user_id": str(user_id)
                }
            ) from e
