from django.urls import path
from . import views

urlpatterns = [
    path('api/sensor-data/', views.get_sensor_data, name='get_sensor_data'),
    path("api/weather/", views.get_live_weather, name="weather_data"),
    path('api/manual-override/', views.manual_override, name='manual_override'),
]
