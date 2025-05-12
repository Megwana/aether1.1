import json
import requests
import random
import datetime
from django.http import JsonResponse
from paho.mqtt.client import Client
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# MQTT CONFIG
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "aesternet/sensor"
mqtt_client = Client()

# Weather API (OpenWeatherMap) Config
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?q=Newcastle,UK&appid=YOUR_API_KEY&units=metric"

# MQTT Message Handling
def handle_mqtt_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print("Received MQTT Sensor Data:", payload)  # Debugging output
        if "tank_level" not in payload:
            print("Warning: 'tank_level' is missing in MQTT payload!")
    except Exception as e:
        print("Error processing MQTT data:", e)

mqtt_client.on_message = handle_mqtt_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe(MQTT_TOPIC)

# Simulated Sensor Data for Testing
def generate_fake_sensor_data():
    temperature = round(random.uniform(15, 30), 1)
    humidity = round(random.uniform(50, 100), 1)
    rainfall = bool(random.choice([True, True, False, False])) 
    
    # ✅ Ensure tank level increases ONLY when rainfall is True
    tank_level = round(random.uniform(50, 100), 1) if rainfall else round(random.uniform(0, 50), 1)
    
    hvac_load = round(random.uniform(10, 100), 1)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "tank_level": tank_level,
        "hvac_load": hvac_load
    }


# HVAC & Rainwater Automation Logic
def evaluate_hvac_decision(data):
    if data["humidity"] > 80 and data["rainfall"]:
        return "Reduce HVAC cooling & store rainwater"
    elif data["temperature"] < 15:
        return "Increase heating for comfort"
    elif data["rainfall"] and data.get("tank_level", 100) > 90:
        return "Redirect excess rainwater to irrigation"
    return "Maintain normal HVAC operation"

# API Routes
def get_sensor_data(request):
    data = generate_fake_sensor_data()
    decision = evaluate_hvac_decision(data)
    return render(request, "home.html", {"sensor_data": {"sensor_data": data, "decision": decision}})
    
    # print("API Response:", response_data)  # Debugging output
    # return JsonResponse({"sensor_data": data, "decision": decision})


def get_live_weather(request):
    """Fetches real-time Newcastle weather data."""
    response = requests.get(WEATHER_API_URL)
    if response.status_code == 200:
        weather_data = response.json()
        return JsonResponse({
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "wind_speed": weather_data["wind"]["speed"],
            "weather": weather_data["weather"][0]["description"]
        })
    return JsonResponse({"error": "Failed to fetch weather data"}, status=500)

@csrf_exempt 
def get_sensor_data(request):
    data = generate_fake_sensor_data()
    return JsonResponse({"sensor_data": data, "decision": evaluate_hvac_decision(data)})
