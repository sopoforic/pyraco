"""Console script for pyraco."""
import sys

import click

from . import pyraco


@click.group()
@click.option('-h', '--host', default='localhost')
@click.option('-p', '--port', type=int, default=55355)
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, host, port, debug):
    ctx.ensure_object(dict)
    ctx.obj['conn'] = pyraco.Connection(host, port, debug=debug)


@main.command()
@click.pass_context
def version(ctx):
    click.echo(ctx.obj['conn'].version())


@main.command()
@click.pass_context
def status(ctx):
    click.echo(ctx.obj['conn'].get_status())


@main.command()
@click.argument('address', type=int)
@click.argument('length', type=int)
@click.pass_context
def read(ctx, address, length):
    print(ctx.obj['conn'].read_core_ram(address, length))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
