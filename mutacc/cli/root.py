import logging

import click
import coloredlogs

from mutacc.utils.housekeeper_extract import findPath

LOG = logging.getLogger(__name__)

@click.command()
@click.argument('sample_id')
def cli(sample_id):
      
   coloredlogs.install(level='INFO')
   LOG.info("Finding files for id: %s", sample_id)

   paths = findPath(sample_id)

   for path in paths['paths']:

      click.echo(path)

