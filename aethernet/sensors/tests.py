from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import json
from sensors.views import evaluate_hvac_decision


class SensorDataTests(TestCase):

    @patch('requests.get')
    def test_get_sensor_data_with_live_weather(self, mock_get):
        # Mocking the response from the Weather API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {"temp": 25, "humidity": 60},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 5}
        }

        # Mock the random.uniform to have consistent tank volume changes
        with patch('random.uniform', return_value=3):
            response = self.client.get(reverse('get_sensor_data'))

        # Check if the response status is OK
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = json.loads(response.content)

        # Check if sensor data contains expected keys
        self.assertIn('sensor_data', data)
        self.assertIn('decision', data)

        # Check the tank level is updated correctly
        sensor_data = data['sensor_data']
        self.assertGreaterEqual(sensor_data['tank_level'], 0)
        self.assertLessEqual(sensor_data['tank_level'], 100)

    @patch('requests.get')
    def test_get_sensor_data_with_mock_data(self, mock_get):
        # Simulate failure of the weather API
        mock_get.side_effect = Exception("Weather API failed")

        # Mock the random.uniform to have consistent tank volume changes
        with patch('random.uniform', return_value=3):
            response = self.client.get(reverse('get_sensor_data'))

        # Check if the response status is OK
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = json.loads(response.content)

        # Check if the fallback data is used
        self.assertIn('sensor_data', data)
        self.assertIn('decision', data)

        # Check the tank level is updated correctly with fake data
        sensor_data = data['sensor_data']
        self.assertGreaterEqual(sensor_data['tank_level'], 0)
        self.assertLessEqual(sensor_data['tank_level'], 100)

    def test_hvac_decision_rain_and_full_tank(self):
        sensor_data = {
            "temperature": 22,
            "humidity": 50,
            "rainfall": True,
            "tank_level": 95,
            "hvac_load": 50
        }

        decision = evaluate_hvac_decision(sensor_data)
        self.assertEqual(decision, "Redirect excess rainwater to irrigation")

    def test_hvac_decision_high_humidity_and_rain(self):
        sensor_data = {
            "temperature": 25,
            "humidity": 85,
            "rainfall": True,
            "tank_level": 50,
            "hvac_load": 50
        }

        decision = evaluate_hvac_decision(sensor_data)
        self.assertEqual(decision, "Reduce HVAC cooling & store rainwater")

    def test_hvac_decision_low_temperature(self):
        sensor_data = {
            "temperature": 5,
            "humidity": 50,
            "rainfall": False,
            "tank_level": 50,
            "hvac_load": 50
        }

        decision = evaluate_hvac_decision(sensor_data)
        self.assertEqual(decision, "Increase heating for comfort")

    def test_hvac_decision_normal(self):
        sensor_data = {
            "temperature": 22,
            "humidity": 60,
            "rainfall": False,
            "tank_level": 50,
            "hvac_load": 50
        }

        decision = evaluate_hvac_decision(sensor_data)
        self.assertEqual(decision, "Maintain normal HVAC operation")

    @patch('requests.get')
    def test_manual_override_on(self, mock_get):
        # Mocking the response from the Weather API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {"temp": 25, "humidity": 60},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 5}
        }

        response = self.client.post(reverse('manual_override'))

        # Check if the redirection status is updated
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(
            data['new_decision'], "Redirecting excess rainwater to irrigation"
            )

    @patch('requests.get')
    def test_manual_override_off(self, mock_get):
        # Mocking the response from the Weather API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "main": {"temp": 25, "humidity": 60},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 5}
        }

        # First, turn it on
        self.client.post(reverse('manual_override'))

        # Now turn it off
        response = self.client.post(reverse('manual_override'))

        # Check if the redirection status is updated
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(
            data['new_decision'], "Stop redirecting rainwater to avoid overuse"
            )
