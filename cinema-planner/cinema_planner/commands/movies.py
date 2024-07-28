import click
import random
from ..models import Movie
from sqlalchemy.orm import sessionmaker, Session
from .fetch import fetch
from datetime import datetime, timedelta


@click.group()
def movies():
    """Manage movies"""
    pass


movies.add_command(fetch)


@movies.command()
@click.pass_obj
def list(obj: dict):
    """List movies in database"""
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    try:
        movies = session.query(Movie).all()
        for movie in movies:
            click.echo(f"{movie.id}::{movie.title}::{movie.overview}")
    except Exception as e:
        click.echo(e, err=True)
        click.echo("Error finding movies")
        pass
    finally:
        session.close()


def _generate_schedule(start_time=8, end_time=22, runtime=90):
    times = []
    noise_table = [x for x in range(0, 30, 5)]
    today = datetime.today()
    current = datetime.combine(
        today, datetime.strptime(f"{start_time}:00", "%H:%M").time()
    )
    final = datetime.combine(today, datetime.strptime(f"{end_time}:00", "%H:%M").time())
    current += timedelta(minutes=random.choice(noise_table))

    while current < final:
        times.append(current)
        noise = random.choice(noise_table)
        current += timedelta(minutes=(noise + runtime))

    return times


def _generate_movie_schedule(session: Session, movie_id: int):
    try:
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if not movie:
            click.echo("Movie not found")
            return

        showtimes = _generate_schedule(runtime=int(movie.runtime))
        return showtimes
    except Exception as e:
        click.echo(e)
        click.echo(f"Error finding movie with id {movie_id}")
    pass


@movies.command()
@click.argument("movie_id", type=click.INT)
@click.pass_obj
def showtimes(obj: dict, movie_id: int):
    """Generate movie showtimes"""
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    times = _generate_movie_schedule(session, movie_id)
    if not times:
        click.echo("Error building schedule")
        return
    for time in times:
        click.echo(time)
