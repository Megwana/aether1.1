import json
import random
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from paho.mqtt.client import Client

redirecting_water = False
tank_capacity_liters = 1000.0
current_tank_volume = 500.0
catchment_area_m2 = 50.0
runoff_coefficient = 0.8

# MQTT CONFIG
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "aesternet/sensor"
latest_sensor_data = {}

# Weather API
WEATHER_API_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
    "?id=2641673"
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
    tank_full = data.get("tank_level", 0) > 90
    raining = data.get("rainfall", False)

    if raining and tank_full:
        return "Redirect excess rainwater to irrigation"
    elif data["humidity"] > 80 and raining:
        return "Reduce HVAC cooling & store rainwater"
    elif data["temperature"] < 10:
        return "Increase heating for comfort"
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
    global current_tank_volume  # To modify the global tank volume

    weather_data = get_live_weather()

    if weather_data:
        # Simulate rainfall collection or depletion
        if weather_data["rainfall"]:
            # Simulate 1–5mm rainfall
            rainfall_mm = random.uniform(1, 5)
            collected_liters = rainfall_mm * catchment_area_m2 * runoff_coefficient
            current_tank_volume = min(
                tank_capacity_liters, current_tank_volume + collected_liters)
        else:
            # Simulate water usage (e.g., 10–30L)
            usage_liters = random.uniform(10, 30)
            current_tank_volume = max(0, current_tank_volume - usage_liters)

        tank_level_percent = round((
            current_tank_volume / tank_capacity_liters) * 100, 1)

        sensor_data = {
            'temperature': weather_data["temperature"],
            'humidity': weather_data["humidity"],
            'rainfall': weather_data["rainfall"],
            'tank_level': tank_level_percent,
            'hvac_load': round(random.uniform(10, 100), 1),
        }

        print("Using LIVE weather data")
    else:
        sensor_data = generate_fake_sensor_data()
        print("Using MOCK sensor data")

    # Decision logic (manual override takes priority)
    if redirecting_water:
        decision = "Redirecting excess rainwater to irrigation"
        + "(manual override)"
    else:
        decision = evaluate_hvac_decision(sensor_data)

    return JsonResponse({
        'sensor_data': sensor_data,
        'decision': decision
    })


@csrf_exempt
def manual_override(request):
    global redirecting_water

    if request.method == 'POST':
        if redirecting_water:
            # Turn off redirection
            new_decision = "Stop redirecting rainwater to avoid overuse"
            redirecting_water = False
        else:
            # Turn on redirection
            new_decision = "Redirecting excess rainwater to irrigation"
            redirecting_water = True

        return JsonResponse({'new_decision': new_decision})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
