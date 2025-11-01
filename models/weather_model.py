from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherData:
    city: str
    country: str
    timestamp: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float | None = None
    uvi: float | None = None
    clouds: int | None = None
    visibility: int | None = None
    wind_speed: float | None = None
    wind_deg: int | None = None
    rain: float | None = None
    snow: float | None = None
    description: str | None = None
    icon: str | None = None

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)
