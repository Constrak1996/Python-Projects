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
from weather_api import fetch_weather_for_city
from icons import load_weather_icons, choose_icon_for_description


def get_weather_and_update_interface():
    """
    Fetches weather data for the selected city and updates the user interface
    with the weather information and the appropriate icon.
    """
    # Get the selected city from the dropdown.
    selected_city_name = city_combobox.get()

    # If no city is selected, show a message and clear the icon.
    if not selected_city_name or selected_city_name == "Select a city":
        weather_result_label.config(text="Please select a city.")
        weather_icon_label.config(image="")
        return

    # Fetch weather data from the API.
    response_data, status_code = fetch_weather_for_city(selected_city_name)

    # If the API returns an error, show the error message.
    if status_code != 200:
        error_message = response_data.get("message", "Unknown error")
        weather_result_label.config(text=f"Error: {error_message}")
        weather_icon_label.config(image="")
        return

    # Extract relevant weather information from the response.
    weather_description = response_data["weather"][0]["description"]
    temperature = response_data["main"]["temp"]
    feels_like_temperature = response_data["main"]["feels_like"]
    humidity_percentage = response_data["main"]["humidity"]

    # Build a readable text block for the weather information.
    weather_text = (
        f"{selected_city_name}\n"
        f"{weather_description.capitalize()}\n"
        f"Temperature: {temperature}°C\n"
        f"Feels like: {feels_like_temperature}°C\n"
        f"Humidity: {humidity_percentage}%"
    )

    # Update the label with the weather text.
    weather_result_label.config(text=weather_text)

    # Choose the correct icon based on the weather description.
    chosen_icon = choose_icon_for_description(weather_description, weather_icon_dictionary)

    # Update the icon label with the chosen icon.
    weather_icon_label.config(image=chosen_icon)
    weather_icon_label.image = chosen_icon  # Prevent garbage collection.


# -----------------------------
# APPLICATION SETUP
# -----------------------------

# Create the main application window with the chosen theme.
application_window = ttkbootstrap.Window(themename=APPLICATION_THEME)
application_window.title("Weather App")

# Set the window size using the settings.
application_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Load all weather icons once at startup.
weather_icon_dictionary = load_weather_icons()

# Title label at the top of the window.
title_label = ttkbootstrap.Label(
    master=application_window,
    text="Weather App",
    font=("Arial", 18)
)
title_label.pack(pady=10)

# Dropdown (combobox) for selecting a city.
city_combobox = ttkbootstrap.Combobox(
    master=application_window,
    values=DANISH_CITIES,
    state="readonly",
    width=27
)
city_combobox.pack(pady=5)
city_combobox.set("Select a city")

# Button to trigger the weather fetch.
get_weather_button = ttkbootstrap.Button(
    master=application_window,
    text="Get Weather",
    bootstyle=PRIMARY,
    command=get_weather_and_update_interface
)
get_weather_button.pack(pady=10)

# Label to display the weather icon.
weather_icon_label = ttkbootstrap.Label(master=application_window)
weather_icon_label.pack(pady=5)

# Label to display the weather text.
weather_result_label = ttkbootstrap.Label(
    master=application_window,
    text="",
    font=("Arial", 12),
    justify="center"
)
weather_result_label.pack(pady=10)

# Start the main event loop for the application.
application_window.mainloop()
