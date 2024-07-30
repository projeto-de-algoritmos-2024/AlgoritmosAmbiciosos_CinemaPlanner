import sys
import termios
import tty
import click
import os
from .config import load_config, save_config
from .commands.fetch import fetch
from .commands.movies import movies
from .db import Base
from .models import Movie, ShowTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Planning your cinema rooms."""
    ctx.ensure_object(dict)
    config = load_config()
    ctx.obj["config"] = config

    engine = create_engine(f"sqlite:///{config['data_dir']}/movies.db")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    ctx.obj["session"] = session


@cli.group()
def db():
    pass


@db.command()
@click.pass_obj
def clean(obj: dict):
    """Clear movies database"""
    session: Session = obj["session"]()
    try:
        session.query(Movie).delete()
        session.commit()
        click.echo("Deleted")
    except Exception:
        session.rollback()
        click.echo("Error deleting database")


@cli.group()
def config():
    """Configuration options."""
    pass


@config.command()
@click.pass_obj
def show(obj: dict):
    """Show configuration."""
    click.echo(obj["config"])


def _prompt_token(prompt: str = "Token: "):
    print(prompt, end="", flush=True)
    password = ""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)
            if char == "\n" or char == "\r":
                print()
                break
            elif char == "\x08" or char == "\x7f":
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
            else:
                password += char
                sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


@config.command()
def set_token():
    """Set API Access Token"""
    token = _prompt_token().strip()
    with open(f"{click.get_app_dir('cinema')}/api.key", "w") as file:
        file.write(token)
    config = load_config()
    config["api_key"] = token
    save_config(config)


cli.add_command(fetch)
cli.add_command(movies)
