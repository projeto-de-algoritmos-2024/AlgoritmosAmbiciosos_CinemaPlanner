import requests
import click
import time
from sqlalchemy.orm import Session
from cinema_planner.models import Movie

BASE_URL = "https://api.themoviedb.org/3"


@click.command()
@click.pass_obj
def fetch(obj: dict):
    config = obj["config"]
    session: Session = obj["session"]()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }
    url = BASE_URL + "/movie/now_playing"

    response = requests.get(
        url, params={"language": "pt-BR", "page": 1}, headers=headers
    )

    data = response.json()
    results = data["results"]
    click.echo(f"There are {len(results)} movies displaying now!")
    with click.progressbar(results, label="Downloading movies to database") as bar:
        try:
            for item in bar:
                url = BASE_URL + f"/movie/{item['id']}"
                response = requests.get(
                    url=url, headers=headers, params={"language": "pt-BR"}
                )
                data = response.json()
                movie = Movie(
                    id=data["id"],
                    title=data["title"],
                    overview=data["overview"],
                    release_date=data["release_date"],
                    runtime=data["runtime"],
                )
                session.merge(movie)
                time.sleep(0.2)
            session.commit()
        except Exception:
            session.rollback()
            click.echo("Download failed")
            return
        finally:
            session.close()
        click.echo("Done.")
