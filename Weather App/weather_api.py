"""
weather_api.py
This file contains functions for communicating with the OpenWeatherMap API.
It is responsible only for fetching and returning weather data.
"""

import requests
from settings import API_KEY, WEATHER_API_URL, FORECAST_API_URL

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

def fetch_five_day_forecast(city_name: str):
    """
    Fetches 5-day forecast data for a given city.
    Returns (response_data, status_code).
    """
    parameters = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(FORECAST_API_URL, params=parameters)
    return response.json(), response.status_code

def extract_daily_forecasts(forecast_data: dict):
    """
    Extracts one forecast per day (the 12:00 entry) from the 5-day forecast data.
    Returns a list of dictionaries with date, description, temperature, and icon code.
    """
    daily_entries = []

    for entry in forecast_data["list"]:
        if "12:00" in entry["dt_txt"]:
            daily_entries.append({
                "date": entry["dt_txt"].split(" ")[0],
                "description": entry["weather"][0]["description"],
                "temperature": entry["main"]["temp"],
                "icon_code": entry["weather"][0]["icon"]
            })

    return daily_entries
