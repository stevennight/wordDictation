import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "input_mode": "鼠标",
    "max_history_size": 50,
    "theme": "System",
    "pen_size": 5,
    "pen_color": "black"
}

def load_config():
    """Loads the application configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Ensure all default keys are present
                for key, value in DEFAULT_CONFIG.items():
                    config.setdefault(key, value)
                return config
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    """Saves the configuration data to config.json."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True, "配置已保存。"
    except IOError as e:
        return False, f"保存配置失败: {e}"