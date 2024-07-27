import click
from .config import load_config
from .commands.fetch import fetch


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Planning your cinema rooms."""
    ctx.ensure_object(dict)
    config = load_config()
    ctx.obj["config"] = config


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
