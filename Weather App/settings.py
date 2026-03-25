"""
settings.py
This file contains configuration values for the Weather App.
It keeps all settings in one place so the rest of the code stays clean.
"""

import os

# -----------------------------
# API SETTINGS
# -----------------------------

# Your OpenWeatherMap API key.
# Replace this with your real key.
API_KEY = "838a986f566a90a67f6791417b4c9b13"

# Base URL for the OpenWeatherMap current weather endpoint.
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"



# -----------------------------
# APPLICATION SETTINGS
# -----------------------------

# Default theme for the application.
# You can change this to other ttkbootstrap themes like:
# "darkly", "superhero", "flatly", "cyborg", etc.
APPLICATION_THEME = "darkly"

# Default window size for the application.
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500


# -----------------------------
# FILE AND PATH SETTINGS
# -----------------------------

# Base directory of the project (the folder where this file is located).
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Folder where all image files (icons) are stored.
ASSETS_DIRECTORY = os.path.join(BASE_DIRECTORY, "assets")


# -----------------------------
# CITY LIST
# -----------------------------

# List of Danish cities used in the dropdown menu.
DANISH_CITIES = [
    "Copenhagen", "Aarhus", "Odense", "Aalborg", "Esbjerg",
    "Randers", "Kolding", "Horsens", "Vejle", "Roskilde",
    "Herning", "Hørsholm", "Helsingør", "Silkeborg", "Næstved",
    "Fredericia", "Viborg", "Køge", "Holstebro", "Taastrup",
    "Slagelse", "Hillerød", "Sønderborg", "Svendborg", "Holbæk", "Ikast", "Bording"
]
