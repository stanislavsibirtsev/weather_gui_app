from datetime import datetime, timedelta

def none_to_zero(value):
    """Преобразует None в 0, иначе возвращает значение"""
    return 0 if value is None else value

def parse_datetime_to_iso(date_str: str) -> str:
    """
    Преобразует ISO-строку с Z в локальное время (+7 часов) и возвращает ISO
    """
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    dt += timedelta(hours=7)
    return dt.isoformat()

def get_time_range() -> tuple:
    """
    Возвращает start и end в ISO-формате за указанный период
    """
    end = datetime.utcnow()
    start = end - timedelta(hours=HOURS_BACK)
    return start.isoformat(), end.isoformat()
