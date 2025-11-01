import requests
from datetime import datetime
from models.weather_model import WeatherData

class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_current_weather(self, city, country):
        params = {
            "q": f"{city},{country}",
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru"
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return self._parse_response(response.json())

    def _parse_response(self, data):
        return WeatherData(
            city=data["name"],
            country=data["sys"]["country"],
            timestamp=data["dt"],
            temp=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            pressure=data["main"]["pressure"],
            humidity=data["main"]["humidity"],
            dew_point=data.get("dew_point"),
            uvi=data.get("uvi"),
            clouds=data["clouds"]["all"],
            visibility=data.get("visibility"),
            wind_speed=data["wind"]["speed"],
            wind_deg=data["wind"].get("deg"),
            rain=data.get("rain", {}).get("1h"),
            snow=data.get("snow", {}).get("1h"),
            description=data["weather"][0]["description"],
            icon=data["weather"][0]["icon"]
        )
