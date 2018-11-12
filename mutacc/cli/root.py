import logging
import yaml
import sys

import coloredlogs
import click
import mongo_adapter
import mongomock

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.db_adapter import MutaccAdapter

from .export import export as export_command
from .importing import importing as import_command
from .remove_command import remove_command as remove_command



LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

@click.group()
@click.option('--loglevel', default = 'INFO', type=click.Choice(LOG_LEVELS))
@click.option('--username')
@click.option('--password')
@click.option('-h', '--host')
@click.option('-p', '--port')
@click.option('-d', '--database-name')
@click.option('--mutacc-dir', help = "Directory to store reduced fastq files, will be created if not exists")
@click.option('--config-file')
@click.pass_context
def cli(context, loglevel, username, password, host, port, database_name, mutacc_dir, config_file):

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

    LOG.info("Establishing connection with host {}, on port {}".format(
        mutacc_config['host'], mutacc_config['port']
        )
    )

    #FOR TESTING
    if "pytest" not in sys.modules:

        mutacc_client = mongo_adapter.get_client(**mutacc_config)

    else:

        mutacc_client = mongomock.MongoClient(port = 27017, host = 'localhost')


    if not mongo_adapter.check_connection(mutacc_client):

        LOG.warning("Connection could not be established")
        context.abort()

    db_name = database_name or cli_config.get('database_name') or 'mutacc'
    mutacc_config['db_name'] = db_name

    mutacc_config['client'] = mutacc_client
    mutacc_config['adapter'] = MutaccAdapter(
        client = mutacc_client,
        db_name = db_name
    )

    directory = mutacc_dir or cli_config.get('mutacc_dir')

    if not directory:
        LOG.warning("Please specify mutacc directory (option --mutacc-dir, or entry 'mutacc_dir' in config file)")
        context.abort()

    mutacc_config['mutacc_dir'] = make_dir(directory)

    context.obj = mutacc_config

cli.add_command(export_command)
cli.add_command(import_command)
cli.add_command(remove_command)
