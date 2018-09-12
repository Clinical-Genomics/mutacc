import logging

import click
import coloredlogs

from . import export, importing, delete, init
LOG = logging.getLogger(__name__)

@click.group()
@click.option('-d', '--database', default = 'mutaccDB')
@click.pass_context
def cli(context, database):
      
   coloredlogs.install(level='INFO')

   context.obj = {}
   context.obj['database'] = database

cli.add_command(export.export)
cli.add_command(importing.importing)
cli.add_command(delete.delete)
cli.add_command(init.init)
