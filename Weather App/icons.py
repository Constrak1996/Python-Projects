"""
icons.py
This file handles loading weather icons and choosing the correct icon
based on the weather description.
"""

import os
from PIL import Image, ImageTk
from settings import ASSETS_DIRECTORY


def load_weather_icons():
    """
    Loads weather icons from the assets folder and resizes them.
    Returns a dictionary of PhotoImage objects keyed by icon type.
    """
    # Build full paths to each icon file.
    sun_icon_path = os.path.join(ASSETS_DIRECTORY, "sun.png")
    cloud_icon_path = os.path.join(ASSETS_DIRECTORY, "cloud.png")
    rain_icon_path = os.path.join(ASSETS_DIRECTORY, "rain.png")
    snow_icon_path = os.path.join(ASSETS_DIRECTORY, "snow.png")
    mist_icon_path = os.path.join(ASSETS_DIRECTORY, "mist.png")

    # Load and resize each image.
    sun_icon = ImageTk.PhotoImage(Image.open(sun_icon_path).resize((50, 50)))
    cloud_icon = ImageTk.PhotoImage(Image.open(cloud_icon_path).resize((50, 50)))
    rain_icon = ImageTk.PhotoImage(Image.open(rain_icon_path).resize((50, 50)))
    snow_icon = ImageTk.PhotoImage(Image.open(snow_icon_path).resize((50, 50)))
    mist_icon = ImageTk.PhotoImage(Image.open(mist_icon_path).resize((50, 50)))

    # Return a dictionary of icons.
    return {
        "sun": sun_icon,
        "cloud": cloud_icon,
        "rain": rain_icon,
        "snow": snow_icon,
        "mist": mist_icon,
    }


def choose_icon_for_description(weather_description: str, icon_dictionary: dict):
    """
    Chooses the correct icon based on the weather description.

    :param weather_description: Text description from the API (e.g. "clear sky").
    :param icon_dictionary: Dictionary of loaded icons from load_weather_icons().
    :return: A PhotoImage object representing the chosen icon.
    """
    description_lowercase = weather_description.lower()

    if "clear" in description_lowercase:
        return icon_dictionary["sun"]
    if "cloud" in description_lowercase:
        return icon_dictionary["cloud"]
    if "rain" in description_lowercase or "drizzle" in description_lowercase:
        return icon_dictionary["rain"]
    if "snow" in description_lowercase:
        return icon_dictionary["snow"]
    if "mist" in description_lowercase or "fog" in description_lowercase:
        return icon_dictionary["mist"]

    # Fallback icon if nothing else matches.
    return icon_dictionary["cloud"]
