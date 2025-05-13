import json
import random
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from paho.mqtt.client import Client

# MQTT CONFIG
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "aesternet/sensor"
latest_sensor_data = {}

# Weather API
WEATHER_API_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
    "?q=Newcastle,UK"
    "&appid=88d566094f90a6035ce3c50a978f0ce8"
    "&units=metric"
)


# Handle MQTT messages
def handle_mqtt_message(client, userdata, message):
    global latest_sensor_data
    try:
        payload = json.loads(message.payload.decode())
        print("MQTT payload:", payload)
        latest_sensor_data = payload
    except Exception as e:
        print("MQTT Error:", e)


# Setup MQTT client
mqtt_client = Client()
mqtt_client.on_message = handle_mqtt_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()  # Needed for async MQTT listening


# Fallback: fake data generator
def generate_fake_sensor_data():
    return {
        'temperature': round(random.uniform(15, 30), 1),
        'humidity': round(random.uniform(40, 100), 1),
        'rainfall': random.choice([True, False]),
        'tank_level': round(random.uniform(0, 100), 1),
        'hvac_load': round(random.uniform(10, 100), 1),
    }


# HVAC logic
def evaluate_hvac_decision(data):
    if data["humidity"] > 80 and data["rainfall"]:
        return "Reduce HVAC cooling & store rainwater"
    elif data["temperature"] < 15:
        return "Increase heating for comfort"
    elif data["rainfall"] and data.get("tank_level", 100) > 90:
        return "Redirect excess rainwater to irrigation"
    return "Maintain normal HVAC operation"


# Weather data from OpenWeatherMap
def get_live_weather():
    try:
        response = requests.get(WEATHER_API_URL, timeout=5)
        data = response.json()

        if response.status_code == 200 and "main" in data:
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rainfall": any(word in data["weather"][0]["description"].lower() for word in ["rain", "drizzle"]),
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
            }
        else:
            print("Weather API unexpected data:", data)
            return None
    except Exception as e:
        print("Weather API failed:", e)
        return None


@csrf_exempt
def get_sensor_data(request):
    weather_data = get_live_weather()

    if weather_data:
        sensor_data = {
            'temperature': weather_data["temperature"],
            'humidity': weather_data["humidity"],
            'rainfall': weather_data["rainfall"],
            'tank_level': round(random.uniform(0, 100), 1),
            'hvac_load': round(random.uniform(10, 100), 1),
        }
        print("Using LIVE weather data")
    else:
        sensor_data = generate_fake_sensor_data()
        print("Using MOCK sensor data")

    decision = evaluate_hvac_decision(sensor_data)

    return JsonResponse({
        'sensor_data': sensor_data,
        'decision': decision
    })


@csrf_exempt
def manual_override(request):
    if request.method == 'POST':
        # Define the decision message (you can change the logic here)
        new_decision = "Redirecting excess rainwater to irrigation"  # Example decision

        return JsonResponse({
            'new_decision': new_decision
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)