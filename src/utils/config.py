import json
from src.utils.logger import setup_logger

logger = setup_logger()

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json file not found")
        return {}
    except json.JSONDecodeError:
        logger.error("Error decoding config.json")
        return {}

def save_config(config):
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Config saved successfully")
    except Exception as e:
        logger.error(f"Error saving config: {e}")