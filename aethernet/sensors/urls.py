from django.urls import path
from .views import get_sensor_data, get_live_weather

urlpatterns = [
    path("api/sensor-data/", get_sensor_data, name="sensor_data"),
    path("api/weather/", get_live_weather, name="weather_data"),
]
