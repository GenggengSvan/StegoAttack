import json


def read_config(config_path):
    """Reads the configuration file."""
    with open(config_path, "r") as f:
        return json.load(f)
