import click
import random
import heapq
import json
import os
from ..models import Movie, ShowTime
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


def interval_partitioning(show_times):
    show_times.sort(key=lambda x: x["start"])
    heap = []
    room_count = 0

    for show in show_times:
        if heap and heap[0][0] <= show["start"]:
            _, room_number = heapq.heappop(heap)
            heapq.heappush(heap, (show["end"], room_number))
            show["room"] = room_number
        else:
            room_count += 1
            heapq.heappush(heap, (show["end"], room_count))
            show["room"] = room_count

    return show_times


@movies.command()
@click.pass_obj
def plan(obj: dict):
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    movies = session.query(Movie).all()
    schedule = []
    for movie in movies:
        times = _generate_movie_schedule(session, movie.id)
        for time in times:
            schedule.append(
                {
                    "movie_id": movie.id,
                    "title": movie.title,
                    "start": time,
                    "end": time + timedelta(minutes=int(movie.runtime)),
                }
            )
    result = interval_partitioning(schedule)
    final_schedule = {}
    for item in result:
        key = f"room#{item['room']}"
        entry = {
            "title": item["title"],
            "movie_id": item["movie_id"],
            "start": item["start"].strftime("%H:%M"),
            "end": item["end"].strftime("%H:%M"),
        }
        if key in final_schedule.keys():
            final_schedule[key].append(entry)
        else:
            final_schedule[key] = [entry]
    json_schedule = json.dumps(final_schedule, indent=4, ensure_ascii=False)

    config = obj["config"]
    data_dir = config["data_dir"]
    filename = "schedule" + str(datetime.now().timestamp()) + ".json"
    click.echo("Saving schedule to file...")
    with open(os.path.join(data_dir, filename), "w", encoding="utf-8") as file:
        file.write(json_schedule)

    click.echo(f"Schedule saved to: {os.path.join(data_dir, filename)}")


@movies.command()
@click.pass_obj
def schedule(obj: dict):
    """Generate schedule for all movies in database"""
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    movies = session.query(Movie).all()
    click.echo("Generating movies schedules")
    try:
        for movie in movies:
            times = _generate_movie_schedule(session, movie.id)
            for time in times:
                showtime = ShowTime(movie_id=movie.id, time=time.time())
                session.add(showtime)
            session.commit()
    except Exception as e:
        click.echo("Error saving schedule")
        click.echo(e)
    finally:
        session.close()


@movies.command()
@click.argument("movie_id", type=click.INT)
@click.pass_obj
def showtimes(obj: dict, movie_id: int):
    """Generate movie showtimes"""
    SessionLocal: sessionmaker[Session] = obj["session"]
    session = SessionLocal()
    times = session.query(ShowTime).filter_by(movie_id=movie_id).all()
    for time in times:
        click.echo(time.time)
