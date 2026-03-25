"""
weather_api.py
This file contains functions for communicating with the OpenWeatherMap API.
It is responsible only for fetching and returning weather data.
"""

import requests
from settings import API_KEY, WEATHER_API_URL


def fetch_weather_for_city(city_name: str):
    """
    Fetches weather data for a given city name from the OpenWeatherMap API.

    :param city_name: Name of the city to fetch weather for.
    :return: A tuple of (response_data, status_code).
             response_data is a dictionary with the JSON response.
             status_code is the HTTP status code from the API.
    """
    # Parameters sent to the API.
    parameters = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    # Send the request to the API.
    response = requests.get(WEATHER_API_URL, params=parameters)

    # Return both the JSON data and the status code.
    return response.json(), response.status_code
