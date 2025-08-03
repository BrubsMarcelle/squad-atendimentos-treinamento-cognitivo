"""
Sistema de logging estruturado - Boas práticas Python.
Logging centralizado com níveis apropriados e formatação consistente.
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from app.utils.constants import SAO_PAULO_TZ


class StructuredLogger:
    """Logger estruturado para o sistema de checkin."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o logger com formatação estruturada."""
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Handler para console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Formatter estruturado
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def _format_context(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Formata contexto adicional para o log."""
        if not context:
            return ""
        
        formatted_items = []
        for key, value in context.items():
            formatted_items.append(f"{key}={value}")
        
        return f" | {' | '.join(formatted_items)}"
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log de informação."""
        context_str = self._format_context(context)
        self.logger.info(f"{message}{context_str}")
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log de aviso."""
        context_str = self._format_context(context)
        self.logger.warning(f"{message}{context_str}")
    
    def error(self, message: str, error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None):
        """Log de erro."""
        context_str = self._format_context(context)
        error_info = f" | error_type={type(error).__name__}" if error else ""
        self.logger.error(f"{message}{context_str}{error_info}", exc_info=error)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log de debug."""
        context_str = self._format_context(context)
        self.logger.debug(f"{message}{context_str}")


class CheckinLogger(StructuredLogger):
    """Logger específico para operações de checkin."""
    
    def __init__(self):
        super().__init__("checkin")
    
    def checkin_attempt(self, username: str, user_id: str):
        """Log para tentativa de checkin."""
        now = datetime.now(SAO_PAULO_TZ)
        self.info(
            "🔄 Tentativa de checkin iniciada",
            {
                "username": username,
                "user_id": str(user_id),
                "timestamp": now.isoformat()
            }
        )
    
    def checkin_success(self, username: str, points: int, duration_ms: float):
        """Log para checkin bem-sucedido."""
        self.info(
            "✅ Checkin realizado com sucesso",
            {
                "username": username,
                "points_awarded": points,
                "duration_ms": f"{duration_ms:.2f}"
            }
        )
    
    def checkin_denied(self, username: str, reason: str, details: Optional[Dict] = None):
        """Log para checkin negado."""
        context = {
            "username": username,
            "reason": reason
        }
        if details:
            context.update(details)
        
        self.warning("⚠️ Checkin negado", context)
    
    def points_calculation(self, username: str, base_points: int, streak_bonus: int, total: int):
        """Log para cálculo de pontos."""
        self.info(
            "🎯 Pontos calculados",
            {
                "username": username,
                "base_points": base_points,
                "streak_bonus": streak_bonus,
                "total_points": total
            }
        )
    
    def database_operation(self, operation: str, collection: str, success: bool, duration_ms: Optional[float] = None):
        """Log para operações de banco de dados."""
        context = {
            "operation": operation,
            "collection": collection,
            "success": success
        }
        if duration_ms:
            context["duration_ms"] = f"{duration_ms:.2f}"
        
        if success:
            self.info(f"💾 Operação de banco: {operation}", context)
        else:
            self.error(f"❌ Falha na operação de banco: {operation}", context=context)


class AuthLogger(StructuredLogger):
    """Logger específico para operações de autenticação."""
    
    def __init__(self):
        super().__init__("auth")
    
    def login_attempt(self, username: str, source: str = "unknown"):
        """Log para tentativa de login."""
        self.info(
            "🔐 Tentativa de login",
            {
                "username": username,
                "source": source,
                "timestamp": datetime.now(SAO_PAULO_TZ).isoformat()
            }
        )
    
    def login_success(self, username: str, duration_ms: float):
        """Log para login bem-sucedido."""
        self.info(
            "✅ Login realizado com sucesso",
            {
                "username": username,
                "duration_ms": f"{duration_ms:.2f}"
            }
        )
    
    def login_failed(self, username: str, reason: str):
        """Log para falha no login."""
        self.warning(
            "❌ Falha no login",
            {
                "username": username,
                "reason": reason
            }
        )
    
    def token_validation(self, username: str, success: bool, reason: Optional[str] = None):
        """Log para validação de token."""
        context = {"username": username}
        if not success and reason:
            context["reason"] = reason
        
        if success:
            self.info("🎫 Token validado com sucesso", context)
        else:
            self.warning("❌ Falha na validação do token", context)


class SystemLogger(StructuredLogger):
    """Logger específico para operações do sistema."""
    
    def __init__(self):
        super().__init__("system")
    
    def startup(self, component: str):
        """Log para startup de componente."""
        self.info(f"🚀 Iniciando {component}")
    
    def health_check(self, component: str, status: str, details: Optional[Dict] = None):
        """Log para health check."""
        context = {"component": component, "status": status}
        if details:
            context.update(details)
        
        emoji = "✅" if status == "healthy" else "❌"
        self.info(f"{emoji} Health check: {component}", context)
    
    def configuration_loaded(self, source: str, items_count: int):
        """Log para carregamento de configuração."""
        self.info(
            "⚙️ Configuração carregada",
            {
                "source": source,
                "items_count": items_count
            }
        )


# Instâncias globais dos loggers
checkin_logger = CheckinLogger()
auth_logger = AuthLogger()
system_logger = SystemLogger()
