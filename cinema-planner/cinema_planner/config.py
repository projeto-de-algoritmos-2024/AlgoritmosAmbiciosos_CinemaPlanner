import click
import json
from pathlib import Path

ROOT = Path(click.get_app_dir("cinema"))
CONFIG_FILENAME = "config.json"
DATA_DIR = ROOT / "data"
DEFAULT_CONFIG = {"api_key": "this is an api key!", "data_dir": DATA_DIR.as_posix()}


def load_config():
    path = ROOT / "config.json"
    for item in [ROOT, DATA_DIR]:
        if not item.exists():
            item.mkdir()

    apikey_path = ROOT / "api.key"
    if apikey_path.exists():
        with open(apikey_path, "r") as file:
            DEFAULT_CONFIG["api_key"] = file.read().strip()

    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(path, "r") as file:
        return json.load(file)


def save_config(config: dict[str, any]):
    path = ROOT / CONFIG_FILENAME
    with open(path, "w") as file:
        json.dump(config, file)
