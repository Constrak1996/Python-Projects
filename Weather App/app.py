"""
app.py
This is the main entry point for the Weather App.
It sets up the graphical user interface, connects to the weather API,
and displays the results with icons.
"""

import ttkbootstrap as ttkbootstrap
from ttkbootstrap.constants import PRIMARY
from settings import (
    APPLICATION_THEME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DANISH_CITIES,
)
from weather_api import fetch_weather_for_city, fetch_five_day_forecast
from icons import load_weather_icons, choose_icon_for_description
from utils import convert_degrees_to_compass_direction, convert_unix_to_time_string


def get_weather_and_update_interface():
    """
    Fetches weather data for the selected city and updates the user interface
    with the weather information and the appropriate icon.
    """
    selected_city_name = city_combobox.get()

    if not selected_city_name or selected_city_name == "Select a city":
        weather_result_label.config(text="Please select a city.")
        weather_icon_label.config(image="")
        return

    response_data, status_code = fetch_weather_for_city(selected_city_name)

    if status_code != 200:
        error_message = response_data.get("message", "Unknown error")
        weather_result_label.config(text=f"Error: {error_message}")
        weather_icon_label.config(image="")
        return

    # Extract weather information
    weather_description = response_data["weather"][0]["description"]
    temperature = response_data["main"]["temp"]
    feels_like_temperature = response_data["main"]["feels_like"]
    humidity_percentage = response_data["main"]["humidity"]
    wind_speed_meters_per_second = response_data["wind"]["speed"]
    wind_direction_degrees = response_data["wind"].get("deg", 0)
    wind_direction_text = convert_degrees_to_compass_direction(wind_direction_degrees)
    wind_gust_speed = response_data["wind"].get("gust", None)
    pressure_hpa = response_data["main"]["pressure"]

    sunrise_unix = response_data["sys"]["sunrise"]
    sunset_unix = response_data["sys"]["sunset"]
    sunrise_time = convert_unix_to_time_string(sunrise_unix)
    sunset_time = convert_unix_to_time_string(sunset_unix)

    # Build weather text
    weather_text = (
        f"{selected_city_name}\n"
        f"{weather_description.capitalize()}\n"
        f"Temperature: {temperature}°C\n"
        f"Feels like: {feels_like_temperature}°C\n"
        f"Humidity: {humidity_percentage}%\n"
        f"Wind: {wind_speed_meters_per_second} m/s {wind_direction_text}\n"
        f"Pressure: {pressure_hpa} hPa\n"
        f"Sunrise: {sunrise_time}\n"
        f"Sunset: {sunset_time}\n"
    )

    if wind_gust_speed is not None:
        weather_text += f"Gusts: {wind_gust_speed} m/s\n"

    weather_result_label.config(text=weather_text)

    chosen_icon = choose_icon_for_description(weather_description, weather_icon_dictionary)
    weather_icon_label.config(image=chosen_icon)
    weather_icon_label.image = chosen_icon


def update_five_day_forecast():
    """
    Loads and displays the 5-day forecast for the selected city.
    """
    selected_city_name = city_combobox.get()

    if not selected_city_name or selected_city_name == "Select a city":
        forecast_label.config(text="Please select a city.")
        return

    response_data, status_code = fetch_five_day_forecast(selected_city_name)

    if status_code != 200:
        forecast_label.config(text="Could not load forecast.")
        return

    forecast_text = ""

    for entry in response_data["list"]:
        if "12:00" in entry["dt_txt"]:
            date = entry["dt_txt"].split(" ")[0]
            description = entry["weather"][0]["description"]
            temperature = entry["main"]["temp"]

            forecast_text += f"{date} - {description.capitalize()}, {temperature}°C\n"

    forecast_label.config(text=forecast_text)


# -----------------------------
# APPLICATION SETUP
# -----------------------------
application_window = ttkbootstrap.Window(themename=APPLICATION_THEME)
application_window.title("Weather App")
application_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Notebook (tabs)
notebook = ttkbootstrap.Notebook(application_window)
notebook.pack(fill="both", expand=True)

current_weather_tab = ttkbootstrap.Frame(notebook)
forecast_tab = ttkbootstrap.Frame(notebook)

notebook.add(current_weather_tab, text="Current Weather")
notebook.add(forecast_tab, text="5-Day Forecast")

# Load icons
weather_icon_dictionary = load_weather_icons()

# CURRENT WEATHER TAB UI
title_label = ttkbootstrap.Label(
    master=current_weather_tab,
    text="Weather App",
    font=("Arial", 18)
)
title_label.pack(pady=10)

city_combobox = ttkbootstrap.Combobox(
    master=current_weather_tab,
    values=DANISH_CITIES,
    state="readonly",
    width=27
)
city_combobox.pack(pady=5)
city_combobox.set("Select a city")

get_weather_button = ttkbootstrap.Button(
    master=current_weather_tab,
    text="Get Weather",
    bootstyle=PRIMARY,
    command=get_weather_and_update_interface
)
get_weather_button.pack(pady=10)

weather_icon_label = ttkbootstrap.Label(master=current_weather_tab)
weather_icon_label.pack(pady=5)

weather_result_label = ttkbootstrap.Label(
    master=current_weather_tab,
    text="",
    font=("Arial", 12),
    justify="center"
)
weather_result_label.pack(pady=10)

# FORECAST TAB UI
forecast_button = ttkbootstrap.Button(
    master=forecast_tab,
    text="Load Forecast",
    bootstyle=PRIMARY,
    command=update_five_day_forecast
)
forecast_button.pack(pady=10)

forecast_label = ttkbootstrap.Label(
    master=forecast_tab,
    text="",
    font=("Arial", 12),
    justify="left"
)
forecast_label.pack(pady=10)

# Start the application
application_window.mainloop()
