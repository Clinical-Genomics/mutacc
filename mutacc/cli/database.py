import logging
import yaml
import sys

import click
import mongo_adapter
import mongomock

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.db_adapter import MutaccAdapter

from .export import export as export_command
from .importing import importing as import_command
from .remove_command import remove_command as remove_command
from .view_command import view_cases, view_variants
from .version_command import version_command as version_command

LOG = logging.getLogger(__name__)

@click.group('db')
@click.option('--username')
@click.option('--password')
@click.option('-h', '--host')
@click.option('-p', '--port')
@click.option('-u', '--uri')
@click.option('-d', '--database')
@click.pass_context
def database_group(context, username, password, host, port, uri, database):

    db_config = {}
    db_config['host'] = host or context.obj.get('host') or 'localhost'
    db_config['port'] = port or context.obj.get('port') or 27017
    db_config['uri'] = uri or context.obj.get('uri')
    db_config['username'] = username or context.obj.get('username')
    db_config['password'] = password or context.obj.get('password')

    if uri:
        LOG.info("Establishing connection with uri {}".format(
            db_config['uri']
            )
        )
    else:
        LOG.info("Establishing connection with host {}, on port {}".format(
            db_config['host'], db_config['port']
            )
        )

    mutacc_client = mongo_adapter.get_client(**db_config)

    if not mongo_adapter.check_connection(mutacc_client):

        LOG.warning("Connection could not be established")
        context.abort()

    context.obj['client'] = mutacc_client
    context.obj['adapter'] = MutaccAdapter(
        client = mutacc_client,
        db_name = context.obj['db_name']
    )

database_group.add_command(export_command)
database_group.add_command(import_command)
database_group.add_command(remove_command)
database_group.add_command(version_command)
database_group.add_command(view_cases)
database_group.add_command(view_variants)
