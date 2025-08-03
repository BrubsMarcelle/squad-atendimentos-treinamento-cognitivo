"""
Decorators para tratamento de erros - Boas práticas Python.
Centraliza o tratamento de exceções e logging de erros.
"""
import functools
import time
from typing import Callable, Type, Dict, Any, Optional
from fastapi import HTTPException, status

from app.utils.exceptions import (
    CheckinBaseException, 
    WeekendCheckinError,
    DuplicateCheckinError,
    UserNotFoundError,
    DatabaseError,
    AuthenticationError,
    ValidationError
)
from app.utils.logging import checkin_logger, auth_logger


def handle_exceptions(
    logger=None,
    custom_mappings: Optional[Dict[Type[Exception], int]] = None
):
    """
    Decorator para tratar exceções de forma padronizada.
    
    Args:
        logger: Logger a ser usado
        custom_mappings: Mapeamento customizado de exceção para status HTTP
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Mapeamento padrão de exceções para status HTTP
            exception_mappings = {
                WeekendCheckinError: status.HTTP_400_BAD_REQUEST,
                DuplicateCheckinError: status.HTTP_409_CONFLICT,
                UserNotFoundError: status.HTTP_404_NOT_FOUND,
                AuthenticationError: status.HTTP_401_UNAUTHORIZED,
                ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
                DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            
            # Aplicar mapeamentos customizados se fornecidos
            if custom_mappings:
                exception_mappings.update(custom_mappings)
            
            try:
                result = await func(*args, **kwargs)
                
                # Log de sucesso se logger fornecido
                if logger:
                    duration = (time.time() - start_time) * 1000
                    logger.info(
                        f"Operação {func.__name__} concluída com sucesso",
                        {"duration_ms": f"{duration:.2f}"}
                    )
                
                return result
                
            except CheckinBaseException as e:
                # Tratar exceções customizadas
                if logger:
                    logger.error(
                        f"Erro de negócio em {func.__name__}: {e.message}",
                        error=e,
                        context=e.details
                    )
                
                http_status = exception_mappings.get(type(e), status.HTTP_400_BAD_REQUEST)
                raise HTTPException(
                    status_code=http_status,
                    detail=e.to_dict()
                )
                
            except HTTPException:
                # Re-raise HTTPException sem modificação
                raise
                
            except (ValueError, TypeError, AttributeError) as e:
                # Re-raise exceções de validação/tipo para não interferir com FastAPI
                raise
                
            except Exception as e:
                # Verificar se é uma exceção do Pydantic/FastAPI
                if 'pydantic' in str(type(e)).lower() or 'validation' in str(type(e)).lower():
                    raise
                
                # Tratar exceções não previstas
                if logger:
                    logger.error(
                        f"Erro inesperado em {func.__name__}",
                        error=e,
                        context={"function": func.__name__}
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "message": "Erro interno do servidor",
                        "details": {}
                    }
                )
        
        return wrapper
    return decorator


def log_execution_time(logger=None, operation_name: str = None):
    """
    Decorator para medir e logar tempo de execução.
    
    Args:
        logger: Logger a ser usado
        operation_name: Nome da operação para o log
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                if logger:
                    logger.info(
                        f"⏱️ {op_name} executado",
                        {"duration_ms": f"{duration:.2f}"}
                    )
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                if logger:
                    logger.error(
                        f"⏱️ {op_name} falhou após {duration:.2f}ms",
                        error=e
                    )
                
                raise
        
        return wrapper
    return decorator


def validate_input(validator_func: Callable):
    """
    Decorator para validação de entrada.
    
    Args:
        validator_func: Função que valida os argumentos
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Executar validação
            validation_result = validator_func(*args, **kwargs)
            
            if validation_result is not True:
                raise ValidationError(
                    message=validation_result,
                    error_code="VALIDATION_FAILED"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Decorators específicos para cada contexto
def handle_checkin_exceptions(func: Callable):
    """Decorator específico para operações de checkin."""
    return handle_exceptions(logger=checkin_logger)(func)


def handle_auth_exceptions(func: Callable):
    """Decorator específico para operações de autenticação."""
    return handle_exceptions(logger=auth_logger)(func)


def log_checkin_operation(operation_name: str = None):
    """Decorator para logar operações de checkin."""
    return log_execution_time(logger=checkin_logger, operation_name=operation_name)


def log_auth_operation(operation_name: str = None):
    """Decorator para logar operações de autenticação."""
    return log_execution_time(logger=auth_logger, operation_name=operation_name)
