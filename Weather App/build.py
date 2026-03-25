import subprocess

command = [
    "python",
    "-m",
    "PyInstaller",
    "--onefile",
    "--noconsole",
    "--add-data", "assets;assets",
    "--add-data", "settings.json;.",
    "app.py"
]

print("Building Weather App executable...")
subprocess.run(command)
print("Done!")
