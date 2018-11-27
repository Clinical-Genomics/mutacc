import logging
import yaml
import sys

import coloredlogs
import click
import mongo_adapter
import mongomock

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.db_adapter import MutaccAdapter

from .database import database_group as database_group
from .extract import extract_command as extract_command
from .synthesize import synthesize_command as synthesize_command



LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

@click.group()
@click.option('--loglevel', default = 'INFO', type=click.Choice(LOG_LEVELS))
@click.option('-c', '--config-file', type = click.Path())
@click.pass_context
def cli(context, loglevel, config_file):

    coloredlogs.install(level = loglevel)

    LOG.info("Running mutacc")

    cli_config = {}

    if config_file:

        with open(config_file, 'r') as in_handle:
            cli_config = yaml.load(in_handle)


    mutacc_config = {}
    mutacc_config['host'] = cli_config.get('host') or 'localhost'
    mutacc_config['port'] = cli_config.get('port') or 27017
    mutacc_config['username'] = cli_config.get('username')
    mutacc_config['password'] = cli_config.get('password')
    mutacc_config['db_name'] = cli_config.get('database') or 'mutacc'
    mutacc_config['vcf_dir'] = cli_config.get('vcf_dir')
    mutacc_config['case_dir'] = cli_config.get('case_dir')
    mutacc_config['query_dir'] = cli_config.get('query_dir')
    mutacc_config['dataset_dir'] = cli_config.get('dataset_dir')
    mutacc_config['tmp_dir'] = cli_config.get('tmp_dir')
    mutacc_config['mutacc_dir'] = cli_config.get('mutacc_dir')

    context.obj = mutacc_config

cli.add_command(extract_command)
cli.add_command(synthesize_command)

cli.add_command(database_group)
