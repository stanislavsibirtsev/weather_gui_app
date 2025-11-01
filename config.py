"""Конфигурационные параметры приложения"""
import os
from dotenv import load_dotenv
load_dotenv()

# API-ключ OpenWeatherMap
API_KEY = os.getenv("API_KEY")

# Настройки логирования
LOG_FILE = "app.log"
LOG_LEVEL = "INFO"

# Параметры интерфейса
WINDOW_TITLE = "Погода — OpenWeatherMap"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
