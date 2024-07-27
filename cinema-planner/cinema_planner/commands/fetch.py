import requests
import click

BASE_URL = "https://api.themoviedb.org/3"


@click.command()
@click.pass_obj
def fetch(obj: dict):
    config = obj["config"]
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }
    url = BASE_URL + "/movie/now_playing"

    response = requests.get(
        url, params={"language": "pt-BR", "page": 1}, headers=headers
    )

    click.echo(response.json())
