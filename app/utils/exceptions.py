"""
Sistema de exceções customizadas - Boas práticas Python.
Centraliza todos os tipos de erro do sistema para tratamento consistente.
"""
from typing import Optional, Dict, Any


class CheckinBaseException(Exception):
    """Exceção base para todos os erros do sistema de checkin."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a exceção para um dicionário para serialização."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(CheckinBaseException):
    """Erro de validação de dados."""
    pass


class AuthenticationError(CheckinBaseException):
    """Erro de autenticação."""
    pass


class AuthorizationError(CheckinBaseException):
    """Erro de autorização."""
    pass


class BusinessRuleError(CheckinBaseException):
    """Erro de regra de negócio."""
    pass


class WeekendCheckinError(BusinessRuleError):
    """Tentativa de checkin em fim de semana."""
    
    def __init__(self, date: str):
        super().__init__(
            message="Check-ins são permitidos apenas de Segunda a Sexta",
            error_code="WEEKEND_CHECKIN_NOT_ALLOWED",
            details={"attempted_date": date}
        )


class DuplicateCheckinError(BusinessRuleError):
    """Tentativa de checkin duplicado no mesmo dia."""
    
    def __init__(self, username: str, existing_checkin_time: str):
        super().__init__(
            message=f"Usuário {username} já realizou check-in hoje às {existing_checkin_time}",
            error_code="DUPLICATE_CHECKIN",
            details={
                "username": username,
                "existing_checkin_time": existing_checkin_time
            }
        )


class UserNotFoundError(CheckinBaseException):
    """Usuário não encontrado."""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Usuário não encontrado: {identifier}",
            error_code="USER_NOT_FOUND",
            details={"identifier": identifier}
        )


class DatabaseError(CheckinBaseException):
    """Erro de operação no banco de dados."""
    pass


class ExternalServiceError(CheckinBaseException):
    """Erro em serviço externo."""
    pass


class ConfigurationError(CheckinBaseException):
    """Erro de configuração do sistema."""
    pass
