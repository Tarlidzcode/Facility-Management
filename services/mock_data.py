"""Functions to generate mock temperature data for testing"""
from datetime import datetime, timedelta
import random

def generate_mock_temperature_data(hours=24, interval_minutes=5):
    """Generate mock temperature and weather data for testing"""
    now = datetime.utcnow()
    data_points = []
    
    # Base temperature patterns
    indoor_base = 22.0  # Target indoor temperature
    outdoor_base = 18.0  # Base outdoor temperature
    
    for i in range(hours * 60 // interval_minutes):
        time_point = now - timedelta(minutes=i * interval_minutes)
        hour = time_point.hour
        
        # Simulate daily temperature cycle
        cycle_factor = (hour - 14) ** 2 / 50  # Peak at 2 PM
        outdoor_temp = outdoor_base + (8 - cycle_factor) + random.uniform(-0.5, 0.5)
        
        # Indoor temperature follows outdoor with delay and dampening
        indoor_temp = indoor_base + (outdoor_temp - outdoor_base) * 0.3 + random.uniform(-0.2, 0.2)
        
        # Humidity patterns
        outdoor_humidity = 60 + random.uniform(-10, 10)
        indoor_humidity = 50 + random.uniform(-5, 5)
        
        # Weather conditions based on time
        conditions = random.choice([
            'Sunny', 'Partly Cloudy', 'Cloudy', 
            'Light Rain', 'Clear'
        ])
        
        data_points.append({
            'timestamp': time_point.isoformat(),
            'indoor': {
                'temperature': round(indoor_temp, 1),
                'humidity': round(indoor_humidity, 1)
            },
            'outdoor': {
                'temperature': round(outdoor_temp, 1),
                'humidity': round(outdoor_humidity, 1),
                'conditions': conditions
            }
        })
    
    return sorted(data_points, key=lambda x: x['timestamp'])

def get_mock_office_data(office_id):
    """Get mock data for a specific office"""
    data = generate_mock_temperature_data()
    
    indoor_data = [{
        'timestamp': point['timestamp'],
        'temperature': point['indoor']['temperature'],
        'humidity': point['indoor']['humidity']
    } for point in data]
    
    outdoor_data = [{
        'timestamp': point['timestamp'],
        'temperature': point['outdoor']['temperature'],
        'humidity': point['outdoor']['humidity'],
        'description': point['outdoor']['conditions']
    } for point in data]
    
    return indoor_data, outdoor_data