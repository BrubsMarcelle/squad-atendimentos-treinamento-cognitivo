"""
Utilitários para manipulação de datas e tempo.
"""
from datetime import datetime, date
from app.utils.constants import SAO_PAULO_TZ, WEEKDAYS


def get_current_datetime() -> datetime:
    """Retorna datetime atual em São Paulo."""
    return datetime.now(SAO_PAULO_TZ)


def get_current_date() -> date:
    """Retorna data atual em São Paulo."""
    return get_current_datetime().date()


def get_start_of_day(target_date: date = None) -> datetime:
    """Retorna o início do dia (00:00:00) para a data especificada."""
    if target_date is None:
        target_date = get_current_date()
    
    return datetime.combine(target_date, datetime.min.time()).replace(tzinfo=SAO_PAULO_TZ)


def get_end_of_day(target_date: date = None) -> datetime:
    """Retorna o fim do dia (23:59:59) para a data especificada."""
    if target_date is None:
        target_date = get_current_date()
    
    return datetime.combine(target_date, datetime.max.time()).replace(tzinfo=SAO_PAULO_TZ)


def is_weekend(target_date: date = None) -> bool:
    """Verifica se a data é fim de semana."""
    if target_date is None:
        target_date = get_current_date()
    
    return target_date.weekday() in WEEKDAYS['WEEKEND']


def is_workday(target_date: date = None) -> bool:
    """Verifica se a data é dia útil."""
    return not is_weekend(target_date)


def get_week_id(target_date: date = None) -> str:
    """Retorna o ID da semana no formato YYYY-WNN."""
    if target_date is None:
        target_date = get_current_date()
    
    year, week, _ = target_date.isocalendar()
    return f"{year}-W{week:02d}"


def format_time_brazilian(dt: datetime) -> str:
    """Formata datetime para o padrão brasileiro de hora."""
    return dt.strftime("%H:%M:%S")


def format_date_brazilian(dt: datetime) -> str:
    """Formata datetime para o padrão brasileiro de data."""
    return dt.strftime("%d/%m/%Y")
