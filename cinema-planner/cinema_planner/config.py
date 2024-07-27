import click
import json
from pathlib import Path

ROOT = Path(click.get_app_dir("cinema"))
CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {"api_key": "this is an api key!"}


def load_config():
    path = ROOT / "config.json"
    if not ROOT.exists():
        ROOT.mkdir(exist_ok=True)

    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(path, "r") as file:
        return json.load(file)


def save_config(config: dict[str, any]):
    path = ROOT / CONFIG_FILENAME
    with open(path, "w") as file:
        json.dump(config, file)
