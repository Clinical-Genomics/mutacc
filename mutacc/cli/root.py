import click

from .export import export as export_command
from .importing import importing as import_command
from .delete import delete as delete_command
from .init import init as init_command

@click.group()
@click.option('-h', '--host', default = 'localhost')
@click.option('-p', '--port', default = 27017)
@click.pass_context
def cli(context, host, port):
      
   context.obj = {}
   context.obj['host'] = host
   context.obj['port'] = port

cli.add_command(export_command)
cli.add_command(import_command)
cli.add_command(delete_command)
cli.add_command(init_command)
