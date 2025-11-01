import sqlite3
from contextlib import contextmanager
from datetime import datetime

class WeatherDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    temp REAL,
                    feels_like REAL,
                    pressure INTEGER,
                    humidity INTEGER,
                    dew_point REAL,
                    uvi REAL,
                    clouds INTEGER,
                    visibility INTEGER,
                    wind_speed REAL,
                    wind_deg INTEGER,
                    rain REAL,
                    snow REAL
                )
            "")
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def save_weather(self, city, country, data):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO weather (...) VALUES (...)", ...)
            conn.commit()

    def get_data_for_plot(self, city, country, start_date, end_date):
        # Возвращает данные для построения графика
        pass
