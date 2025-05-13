from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse


# Test case for testing the `get_live_weather` view
class GetLiveWeatherTestCase(TestCase):
    # Test the success case when weather data is fetched successfully from the API
    @patch("requests.get")
    def test_get_live_weather_success(self, mock_get):
        # Mocked weather data that would be returned by the external API
        mock_response = {
            "main": {"temp": 20, "humidity": 60},
            "wind": {"speed": 5},
            "weather": [{"description": "clear sky"}]
        }

        # Simulate the mock `requests.get` call returning 
        # a status code of 200 (OK)
        mock_get.return_value.status_code = 200
        # Simulate the mock response to return the mock weather data
        mock_get.return_value.json.return_value = mock_response

        # Send a GET request to the `weather_data` URL
        # (which is mapped to `get_live_weather`)
        response = self.client.get(reverse("weather_data"))

        # Check if the response status code is 200 (successful)
        self.assertEqual(response.status_code, 200)
        # Check if the response contains the 'temperature' field from the mock data
        self.assertIn("temperature", response.json())

    # Test the failure case when the API fails to return weather data
    @patch("requests.get")  # Mocking the `requests.get` method to simulate API failure
    def test_get_live_weather_failure(self, mock_get):
        # Simulate the mock `requests.get` call returning a status code of 500 (server error)
        mock_get.return_value.status_code = 500

        # Send a GET request to the `weather_data` URL
        # (which is mapped to `get_live_weather`)
        response = self.client.get(reverse("weather_data"))

        # Check if the response status code is 500 (indicating failure)
        self.assertEqual(response.status_code, 500)
        # Check if the response contains the 'error' field
        # (as per the failure response)
        self.assertIn("error", response.json())


# Test case for testing the `get_sensor_data` view
class GetSensorDataTestCase(TestCase):
    # Test the sensor data API that generates simulated sensor data
    @patch("sensors.views.generate_fake_sensor_data")
    def test_sensor_data_api(self, mock_generate_fake_data):
        # Mocked sensor data that will be returned
        # by the fake sensor data generator
        mock_generate_fake_data.return_value = {
            "temperature": 22,  # Simulated temperature
            "humidity": 70,     # Simulated humidity
            "rainfall": True,   # Simulated rainfall
            "tank_level": 80,   # Simulated tank level
            "hvac_load": 50     # Simulated HVAC load
        }

        # Send a POST request to the `sensor_data`
        # URL (which is mapped to `get_sensor_data`)
        response = self.client.post(reverse("sensor_data"))

        # Check if the response status code is 200 (successful)
        self.assertEqual(response.status_code, 200)
        # Check if the response contains the 'sensor_data' field
        self.assertIn("sensor_data", response.json())
        # Check if the response contains the 'decision' field
        # (HVAC decision based on sensor data)
        self.assertIn("decision", response.json())
