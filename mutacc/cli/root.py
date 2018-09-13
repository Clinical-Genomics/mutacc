import logging

import click
import coloredlogs

from .export import export as export_command
from .importing import importing as import_command
from .delete import delete as delete_command
from .init import init as init_command

LOG = logging.getLogger(__name__)

@click.group()
@click.option('-d', '--database', default = 'mutaccDB')
@click.pass_context
def cli(context, database):
      
   coloredlogs.install(level='INFO')

   context.obj = {}
   context.obj['database'] = database

cli.add_command(export_command)
cli.add_command(import_command)
cli.add_command(delete_command)
cli.add_command(init_command)
