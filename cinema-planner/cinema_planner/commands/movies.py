import click
from ..models import Movie
from sqlalchemy.orm import sessionmaker, Session


@click.group()
def movies():
    """Manage movies"""
    pass


@movies.command()
@click.pass_obj
def list(obj: dict):
    """List movies in database"""
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    try:
        movies = session.query(Movie).all()
        for movie in movies:
            click.echo(movie.title)
    except Exception:
        click.echo("Error finding movies")
        pass
    finally:
        session.close()
