import os
from pathlib import Path

API_KEY = os.getenv("WEATHER_API_KEY", "ваш_ключ_здесь")
DB_PATH = Path("weather_data.db")

# Параметры по умолчанию
DEFAULT_CITY = "Москва"
DEFAULT_COUNTRY = "RU"
