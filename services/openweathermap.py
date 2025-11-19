"""OpenWeatherMap API integration for real-time weather data."""
from datetime import datetime, timedelta
import requests

# API Key for OpenWeatherMap
OPENWEATHER_API_KEY = "###################################"

def fetch_current_weather(city="Cape Town, Pinelands, ZA"):
    """Fetch current weather data from OpenWeatherMap.
    
    Args:
        city: City name (default: Cape Town, Pinelands, ZA)
    
    Returns:
        Dict with current weather data or None on failure.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # Use Celsius
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': round(float(data['main']['temp']), 1),
            'humidity': round(float(data['main']['humidity']), 1),
            'conditions': data['weather'][0]['description'].title(),
            'feels_like': round(float(data['main']['feels_like']), 1),
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'city': data['name'],
            'country': data['sys']['country']
        }
    except Exception as e:
        print(f"OpenWeatherMap fetch error: {e}")
        return None


def fetch_forecast_weather(city="Cape Town, Pinelands, ZA", hours=24):
    """Fetch hourly forecast data from OpenWeatherMap.
    
    Args:
        city: City name (default: Cape Town, Pinelands, ZA)
        hours: Number of hours to fetch (max 48)
    
    Returns:
        List of dicts with hourly weather data or None on failure.
    """
    try:
        # First get coordinates for the city
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'limit': 1
        }
        
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        if not geo_data:
            print(f"City not found: {city}")
            return None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # Now get forecast data
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',  # Use Celsius
            'cnt': min(hours // 3, 40)  # API returns 3-hour intervals, max 40 entries
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data['list'][:hours]:
            results.append({
                'timestamp': item['dt_txt'],
                'temperature': round(float(item['main']['temp']), 1),
                'humidity': round(float(item['main']['humidity']), 1),
                'conditions': item['weather'][0]['description'].title(),
                'feels_like': round(float(item['main']['feels_like']), 1),
                'pressure': item['main']['pressure'],
                'wind_speed': item['wind']['speed']
            })
        
        return results
    except Exception as e:
        print(f"OpenWeatherMap forecast fetch error: {e}")
        return None


def fetch_hourly_weather(lat, lon, hours=24):
    """Fetch hourly weather using coordinates (for compatibility with existing code).
    
    Args:
        lat: Latitude
        lon: Longitude
        hours: Number of hours to fetch
    
    Returns:
        List of dicts with hourly weather data or None on failure.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'cnt': min(hours // 3, 40)
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data['list'][:hours]:
            results.append({
                'timestamp': item['dt_txt'],
                'temperature': round(float(item['main']['temp']), 1),
                'humidity': round(float(item['main']['humidity']), 1),
                'conditions': item['weather'][0]['description'].title()
            })
        
        return results
    except Exception as e:
        print(f"OpenWeatherMap fetch error: {e}")
        return None

