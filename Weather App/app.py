"""
app.py
Main entry point for the Weather App.
Organized into clear sections so each tab is built in its own function.
"""

import ttkbootstrap as ttkbootstrap
from ttkbootstrap.constants import PRIMARY

from settings import (
    APPLICATION_THEME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DANISH_CITIES,
)

from weather_api import (
    fetch_weather_for_city,
    fetch_five_day_forecast,
    extract_daily_forecasts
)

from icons import load_weather_icons, choose_icon_for_description
from utils import convert_degrees_to_compass_direction, convert_unix_to_time_string
from user_settings import load_user_settings, save_user_settings


# ---------------------------------------------------------
#  FORECAST CARD CREATION
# ---------------------------------------------------------

def create_forecast_card(parent, date_text, description_text, temperature_value, icon_image):
    """
    Creates a styled forecast card containing the date, icon, description, and temperature.
    """

    card = ttkbootstrap.Frame(
        master=parent,
        padding=10,
        bootstyle="secondary"
    )
    card.pack(fill="x", pady=5)

    date_label = ttkbootstrap.Label(
        master=card,
        text=date_text,
        font=("Arial", 14, "bold")
    )
    date_label.pack(anchor="w")

    row_frame = ttkbootstrap.Frame(master=card)
    row_frame.pack(anchor="w", pady=5)

    icon_label = ttkbootstrap.Label(master=row_frame, image=icon_image)
    icon_label.image = icon_image
    icon_label.pack(side="left", padx=5)

    description_label = ttkbootstrap.Label(
        master=row_frame,
        text=description_text.capitalize(),
        font=("Arial", 12)
    )
    description_label.pack(side="left")

    temperature_label = ttkbootstrap.Label(
        master=card,
        text=f"{temperature_value}°C",
        font=("Arial", 12)
    )
    temperature_label.pack(anchor="w")

    return card


# ---------------------------------------------------------
#  CURRENT WEATHER LOGIC
# ---------------------------------------------------------

def get_weather_and_update_interface():
    """
    Fetches weather data for the selected city and updates the user interface.
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

    weather_description = response_data["weather"][0]["description"]
    temperature = response_data["main"]["temp"]
    feels_like_temperature = response_data["main"]["feels_like"]
    humidity_percentage = response_data["main"]["humidity"]
    wind_speed_meters_per_second = response_data["wind"]["speed"]
    wind_direction_degrees = response_data["wind"].get("deg", 0)
    wind_direction_text = convert_degrees_to_compass_direction(wind_direction_degrees)
    wind_gust_speed = response_data["wind"].get("gust", None)
    pressure_hpa = response_data["main"]["pressure"]

    sunrise_time = convert_unix_to_time_string(response_data["sys"]["sunrise"])
    sunset_time = convert_unix_to_time_string(response_data["sys"]["sunset"])

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


# ---------------------------------------------------------
#  FORECAST LOGIC
# ---------------------------------------------------------

def update_five_day_forecast():
    """
    Loads and displays the 5-day forecast using styled cards.
    """

    selected_city_name = city_combobox.get()

    if not selected_city_name or selected_city_name == "Select a city":
        return

    response_data, status_code = fetch_five_day_forecast(selected_city_name)

    if status_code != 200:
        return

    for widget in forecast_cards_frame.winfo_children():
        widget.destroy()

    daily_forecasts = extract_daily_forecasts(response_data)

    for day in daily_forecasts:
        icon_image = choose_icon_for_description(day["description"], weather_icon_dictionary)

        create_forecast_card(
            parent=forecast_cards_frame,
            date_text=day["date"],
            description_text=day["description"],
            temperature_value=day["temperature"],
            icon_image=icon_image
        )


# ---------------------------------------------------------
#  TAB BUILDERS
# ---------------------------------------------------------
def apply_settings():
    """
    Applies the selected settings, such as theme changes,
    and saves them permanently to the settings file.
    """

    selected_theme = theme_combobox.get()

    # Apply theme immediately
    application_window.style.theme_use(selected_theme)

    # Save settings to JSON
    user_settings["theme"] = selected_theme
    save_user_settings(user_settings)


def build_current_weather_tab(parent):
    """
    Builds the entire Current Weather tab.
    """

    global city_combobox, weather_icon_label, weather_result_label

    title_label = ttkbootstrap.Label(
        master=parent,
        text="Weather App",
        font=("Arial", 18)
    )
    title_label.pack(pady=10)

    city_combobox = ttkbootstrap.Combobox(
        master=parent,
        values=DANISH_CITIES,
        state="readonly",
        width=27
    )
    city_combobox.pack(pady=5)
    city_combobox.set("Select a city")

    get_weather_button = ttkbootstrap.Button(
        master=parent,
        text="Get Weather",
        bootstyle=PRIMARY,
        command=get_weather_and_update_interface
    )
    get_weather_button.pack(pady=10)

    weather_icon_label = ttkbootstrap.Label(master=parent)
    weather_icon_label.pack(pady=5)

    weather_result_label = ttkbootstrap.Label(
        master=parent,
        text="",
        font=("Arial", 12),
        justify="center"
    )
    weather_result_label.pack(pady=10)


def build_forecast_tab(parent):
    """
    Builds the entire 5-Day Forecast tab.
    """

    global forecast_cards_frame

    forecast_button = ttkbootstrap.Button(
        master=parent,
        text="Load Forecast",
        bootstyle=PRIMARY,
        command=update_five_day_forecast
    )
    forecast_button.pack(pady=5)

    forecast_cards_frame = ttkbootstrap.Frame(master=parent)
    forecast_cards_frame.pack(fill="both", expand=True, pady=5)

def build_settings_tab(parent):
    """
    Builds the Settings tab where the user can configure application preferences.
    """

    global theme_combobox

    settings_title_label = ttkbootstrap.Label(
        master=parent,
        text="Settings",
        font=("Arial", 18)
    )
    settings_title_label.pack(pady=10)

    theme_label = ttkbootstrap.Label(
        master=parent,
        text="Select Theme:",
        font=("Arial", 12)
    )
    theme_label.pack(anchor="w", padx=10)

    theme_combobox = ttkbootstrap.Combobox(
        master=parent,
        values=["darkly", "flatly", "superhero", "cyborg", "solar", "morph"],
        state="readonly",
        width=20
    )
    theme_combobox.pack(pady=5, padx=10)
    theme_combobox.set(user_settings["theme"])

    save_button = ttkbootstrap.Button(
        master=parent,
        text="Save Settings",
        bootstyle=PRIMARY,
        command=apply_settings
    )

    save_button.pack(pady=20)


# ---------------------------------------------------------
#  MAIN WINDOW SETUP
# ---------------------------------------------------------
user_settings = load_user_settings()

application_window = ttkbootstrap.Window(themename=user_settings["theme"])

application_window.title("Weather App")
application_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

weather_icon_dictionary = load_weather_icons()

notebook = ttkbootstrap.Notebook(application_window)
notebook.pack(fill="both", expand=True)

current_weather_tab = ttkbootstrap.Frame(notebook)
forecast_tab = ttkbootstrap.Frame(notebook)
settings_tab = ttkbootstrap.Frame(notebook)

notebook.add(current_weather_tab, text="Current Weather")
notebook.add(forecast_tab, text="5-Day Forecast")
notebook.add(settings_tab, text="Settings")

build_current_weather_tab(current_weather_tab)
build_forecast_tab(forecast_tab)
build_settings_tab(settings_tab)

application_window.mainloop()
