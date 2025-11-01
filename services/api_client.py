import requests
from utils.helpers import none_to_zero, parse_datetime_to_iso, get_time_range
from config import API_KEY, POST_LIST_URL, MEASUREMENTS_URL_TEMPLATE

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def get_latest_post(self) -> dict:
        """Получает последний пост (станцию) из API"""
        response = requests.get(POST_LIST_URL, headers=self.headers)
        response.raise_for_status()
        posts = response.json()
        if not posts:
            raise ValueError("Нет доступных постов")
        return posts[0]  # берём первый (самый свежий)

    def get_measurements(self, post_id: str) -> list:
        """Получает измерения за указанный период"""
        start, end = get_time_range()

        url = MEASUREMENTS_URL_TEMPLATE.format(post_id=post_id)
        params = {
            "interval": INTERVAL,
            "date__gt": start,
            "date__lt": end,
            "with_aqi": "true"
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
