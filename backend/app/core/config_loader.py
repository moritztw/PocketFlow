import json
import os

CONFIG_PATH = os.getenv("CONFIG_FILE_PATH", "./data/config.json")
#DEFAULT_CONFIG = 

def load_config() -> dict:
    # config Datei lagen oder sie aus default erstellen
    if not os.path.exists(CONFIG_PATH):
        # Default config laden
        with open("config_default.json", "r") as f:
            default_config = json.load(f)
        
        # Default config in die config Datei schreiben
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=4)
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        # Wenn die config Datei beschädigt ist, die default config laden
        with open("config_default.json", "r") as f:
            config = json.load(f)
    return config

def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)