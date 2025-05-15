import requests
from datetime import datetime

class WeatherService:
    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.geo_cache = {}

    def get_weather(self, location: str, date: str = None) -> dict:
        date = date or datetime.now().strftime("%Y-%m-%d")
        latlon = self._get_latlon(location)

        if not latlon:
            return self._empty_weather_response(location, date)

        if date == datetime.now().strftime("%Y-%m-%d"):
            return self._get_current_weather(location, latlon)
        else:
            return self._get_forecast_weather(location, latlon, date)

    def _get_latlon(self, location: str):
        if location in self.geo_cache:
            return self.geo_cache[location]

        params = {'name': location, 'count': 1}
        response = requests.get(self.GEOCODE_URL, params=params)
        if response.status_code != 200:
            return None

        data = response.json()
        if 'results' not in data or not data['results']:
            return None

        latlon = (data['results'][0]['latitude'], data['results'][0]['longitude'])
        self.geo_cache[location] = latlon
        return latlon

    def _get_current_weather(self, location, latlon):
        lat, lon = latlon
        params = {'latitude': lat, 'longitude': lon, 'current_weather': True}
        response = requests.get(self.FORECAST_URL, params=params)
        data = response.json()

        current = data.get('current_weather')
        if not current:
            return self._empty_weather_response(location, datetime.now().strftime("%Y-%m-%d"))

        return {
            "location": location,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "temperature": current.get('temperature'),
            "description": f"Windspeed {current.get('windspeed')} km/h" if current.get('windspeed') else None,
            "temperature_max": None,
            "temperature_min": None
        }

    def _get_forecast_weather(self, location, latlon, date):
        lat, lon = latlon
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min',
            'timezone': 'auto'
        }
        response = requests.get(self.FORECAST_URL, params=params)
        data = response.json()

        daily = data.get('daily', {})
        available_dates = daily.get('time', [])

        if date not in available_dates:
            return self._empty_weather_response(location, date)

        index = available_dates.index(date)
        temp_max = daily['temperature_2m_max'][index]
        temp_min = daily['temperature_2m_min'][index]

        return {
            "location": location,
            "date": date,
            "temperature": None,
            "description": None,
            "temperature_max": temp_max,
            "temperature_min": temp_min
        }

    def _empty_weather_response(self, location, date):
        return {
            "location": location,
            "date": date,
            "temperature": None,
            "description": None,
            "temperature_max": None,
            "temperature_min": None
        }

# Example Usage
# if __name__ == "__main__":
#     ws = WeatherService()
#     print(ws.get_weather("Tel Aviv"))
#     print(ws.get_weather("Tel Aviv", "2025-05-16"))
#     print(ws.get_weather("Tel Aviv", "2026-01-01"))
