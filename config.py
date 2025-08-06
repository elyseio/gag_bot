import json

CONFIG_PATH = "config.json"
with open(CONFIG_PATH, "r") as config_file:
    CONFIG = json.load(config_file)
