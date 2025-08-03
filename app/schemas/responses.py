"""
Schemas para respostas da API - garante consistência e documentação automática.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CheckinStatusResponse(BaseModel):
    """Schema para resposta do status de checkin."""
    can_checkin: bool
    last_checkin_date: Optional[str] = None
    last_checkin_formatted: Optional[str] = None
    is_weekend: bool = False
    already_checked_today: bool = False
    reason: Optional[str] = None
    message: Optional[str] = None
    today: Optional[str] = None


class CheckinResponse(BaseModel):
    """Schema para resposta do checkin."""
    success: bool
    message: str
    can_checkin: bool
    reason: str
    points_awarded: Optional[int] = None
    username: Optional[str] = None
    checkin_time: Optional[str] = None
    checkin_date: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Schema para resposta do health check."""
    status: str
    timestamp: str
    current_date: str
    current_week: str
    database: dict
    timezone: str


class ApiResponse(BaseModel):
    """Schema genérico para respostas da API."""
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""
    detail: str
    error_code: Optional[str] = None
