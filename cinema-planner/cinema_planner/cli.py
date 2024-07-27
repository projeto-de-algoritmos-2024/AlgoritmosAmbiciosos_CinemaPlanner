import click
import os
from .config import load_config
from .commands.fetch import fetch
from .commands.movies import movies
from .db import Base
from .models import Movie
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


cli.add_command(fetch)
cli.add_command(movies)
