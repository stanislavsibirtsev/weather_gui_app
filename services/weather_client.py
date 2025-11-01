import requests
import json
from datetime import datetime
from config import API_KEY

def fetch_weather_data(city: str) -> dict | None:
    """
    Запрашивает данные у OpenWeatherMap и возвращает структурированный словарь.
    Возвращает None при ошибке.
    """
    URL = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(URL, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}")
            print(response.text)
            return None

        data = response.json()

        # Структурируем данные для интерфейса
        result = {
            "city_name": data["name"],
            "country": data["sys"]["country"],
            "lat": round(data["coord"]["lat"], 4),
            "lon": round(data["coord"]["lon"], 4),
            "temp": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "temp_min": round(data["main"]["temp_min"], 1),
            "temp_max": round(data["main"]["temp_max"], 1),
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "clouds": data["clouds"]["all"],
            "weather_description": data["weather"][0]["description"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%Y-%m-%d %H:%M:%S"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%Y-%m-%d %H:%M:%S"),
            "dt": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S")
        }
        return result

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Нехватает поля в ответе API: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None
