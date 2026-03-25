"""
user_settings.py
Handles loading and saving user-specific settings such as theme choice.
"""

import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "theme": "darkly"
}


def load_user_settings():
    """
    Loads user settings from the JSON file.
    If the file does not exist, default settings are returned.
    """
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_user_settings(settings: dict):
    """
    Saves user settings to the JSON file.
    """
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)
