import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/bootbridge")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """Loads configuration from JSON file or returns default preferences."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[BootBridge] Error loading config: {e}")
    return {"language": "id", "theme": "dark", "show_launch_guide": True}

def save_config(config):
    """Saves configuration data to JSON file."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[BootBridge] Error saving config: {e}")

def add_remote_history(entry):
    """Adds a remote connection entry (dict with host, port, proto, user) to saved history."""
    cfg = load_config()
    history = cfg.get("remote_history", [])
    # Deduplicate by host & port
    history = [h for h in history if not (h.get("host") == entry.get("host") and h.get("port") == entry.get("port"))]
    history.insert(0, entry)
    cfg["remote_history"] = history[:10]  # Keep last 10 entries
    save_config(cfg)

