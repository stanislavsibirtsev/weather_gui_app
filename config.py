
# API
API_KEY = "ваш_api_ключ"  # Замените на реальный ключ
POST_LIST_URL = "https://mycityair.ru/harvester/v2/Posts"
MEASUREMENTS_URL_TEMPLATE = "https://mycityair.ru/harvester/v2/Posts/{post_id}/measurements"

# MySQL
MYSQL_HOST = "localhost"
MYSQL_USER = "your_user"        # Замените на вашего пользователя MySQL
MYSQL_PASSWORD = "your_password"  # Замените на пароль
MYSQL_DATABASE = "weather_db"     # Замените на имя БД

# Временные настройки
INTERVAL = "1h"
HOURS_BACK = 1  # запрос за последний час
