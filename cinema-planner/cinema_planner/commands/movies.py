import click
import random
import heapq
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
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


def create_pdf(rooms: dict, out_path: str | None = None):
    out = "show_times.pdf"
    if out_path:
        out = out_path
    doc = SimpleDocTemplate(out, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for room, shows in rooms.items():
        story.append(Paragraph(f"Room {room}", styles["Heading2"]))

        table_data = [["Title", "Start Time", "End Time"]]
        for show in shows:
            table_data.append(
                [
                    show["title"],
                    show["start"],
                    show["end"],
                ]
            )

        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 12))

    doc.build(story)


@movies.command()
@click.pass_obj
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    type=click.STRING,
    help="Schedule output path",
)
def plan(obj: dict, output_path: str):
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
        key = item["room"]
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

    click.echo(f"Schedule saved to: {output_path}")
    create_pdf(final_schedule, output_path)


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
