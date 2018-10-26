import logging
import yaml

import coloredlogs
import click
import mongo_adapter

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.db_adapter import MutaccAdapter

from .export import export as export_command
from .importing import importing as import_command
from .delete import delete as delete_command
from .init import init as init_command


LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

@click.group()
@click.option('--loglevel', default = 'INFO', type=click.Choice(LOG_LEVELS))
@click.option('--username')
@click.option('--password')
@click.option('-h', '--host', default = 'localhost')
@click.option('-p', '--port', default = 27017)
@click.option('--mutacc-dir', help = "Directory to store reduced fastq files, will be created if not exists")
@click.option('--config_file')
@click.pass_context
def cli(context, loglevel, username, password, host, port, mutacc_dir, config_file):

    coloredlogs.install(level = loglevel)

    LOG.info("Running mutacc")

    cli_config = {}

    if config_file:

        with open(config_file, 'r') as in_handle:
            cli_config = yaml.load(in_handle)

    mutacc_config = {}
    mutacc_config['host'] = host or cli_config.get('host') or 'localhost'
    mutacc_config['port'] = port or cli_config.get('port') or 27017
    mutacc_config['username'] = username or cli_config.get('username')
    mutacc_config['password'] = password or cli_config.get('password')

    LOG.info("Establishing connection with host {}, on port {}".format(mutacc_config['host'], mutacc_config['port']))
    mutacc_client = mongo_adapter.get_client(**mutacc_config)

    if not mongo_adapter.check_connection(mutacc_client):

        LOG.warning("Connection could not be established")
        context.abort()

    mutacc_config['client'] = mutacc_client
    mutacc_config['adapter'] = MutaccAdapter(client = mutacc_client, db_name = 'mutacc')

    directory = mutacc_dir or cli_config.get('mutacc_dir') or "~/mutacc_fastqs/"
    mutacc_config['mutacc_dir'] = make_dir(directory)

    context.obj = mutacc_config

cli.add_command(export_command)
cli.add_command(import_command)
cli.add_command(delete_command)
cli.add_command(init_command)
