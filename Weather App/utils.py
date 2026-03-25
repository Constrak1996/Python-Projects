from datetime import datetime

def convert_degrees_to_compass_direction(degrees: float) -> str:
    """
    Converts wind direction in degrees to a compass direction.
    Example: 0° = North, 90° = East, etc.
    """
    compass_directions = [
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West"
    ]

    # Each direction covers 45 degrees.
    index = int((degrees + 22.5) // 45) % 8
    return compass_directions[index]

def convert_unix_to_time_string(unix_timestamp: int) -> str:
    """
    Converts a UNIX timestamp to a human-readable HH:MM time string.
    """
    return datetime.fromtimestamp(unix_timestamp).strftime("%H:%M")
