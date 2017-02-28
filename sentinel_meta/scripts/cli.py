import click

from .filesearch import filesearch

@click.group()
@click.option('--debug/--no-debug', default=False, help='Log debug messages')
def cli(debug):
    from ..logs import set_cli_logger
    set_cli_logger(debug=debug)


cli.add_command(filesearch)
