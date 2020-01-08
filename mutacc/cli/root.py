import logging
import yaml
import sys
import coloredlogs
import click
import mongo_adapter
from pathlib import Path

from mutacc.parse.path_parse import parse_path, make_dir
from mutacc.mutaccDB.db_adapter import MutaccAdapter

from .database import database_group as database_group
from .extract import extract_command as extract_command
from .synthesize import synthesize_command as synthesize_command

from .root_dirs import SUB_DIRS

from mutacc import __version__


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.group()
@click.option("--loglevel", default="INFO", type=click.Choice(LOG_LEVELS))
@click.option("-c", "--config-file", type=click.Path(exists=True))
@click.option("-r", "--root-dir", type=click.Path(exists=True))
@click.option("-d", "--demo", is_flag=True)
@click.version_option(__version__)
@click.pass_context
def cli(context, loglevel, config_file, root_dir, demo):

    coloredlogs.install(level=loglevel)

    LOG.info("Running mutacc")

    cli_config = {}

    if demo:
        host = "localhost"
        port = 27017
        db_name = "mutacc-demo"
        username = None
        password = None
        root_dir = make_dir(root_dir or "./mutacc_demo_root")
        vcf_info_export = {
            "case": [{"id": "case,case", "type": "String", "description": "case"}],
            "variant": [{"id": "rank, rank", "type": "Integer", "description": "rank"}],
        }

    else:

        if config_file:
            with open(config_file, "r") as in_handle:
                cli_config = yaml.load(in_handle, Loader=yaml.FullLoader)

        host = cli_config.get("host") or "localhost"
        port = cli_config.get("port") or 27017
        db_name = cli_config.get("database") or "mutacc"
        username = cli_config.get("username")
        password = cli_config.get("password")
        vcf_info_export = cli_config.get("vcf_info_export")
        root_dir = cli_config.get("root_dir") or root_dir
        if not root_dir:
            LOG.warning(
                "Please provide a root directory, through option --root-dir or in config_file"
            )
            context.abort()

    mutacc_config = {}
    mutacc_config["host"] = host
    mutacc_config["port"] = port
    mutacc_config["username"] = username
    mutacc_config["password"] = password
    mutacc_config["db_name"] = db_name
    mutacc_config["vcf_info_export"] = vcf_info_export
    mutacc_config["root_dir"] = parse_path(root_dir, file_type="dir")
    mutacc_config["demo"] = demo

    # Create subdirectories in root, if not already created
    for dir_type in SUB_DIRS.keys():
        subdir = mutacc_config["root_dir"].joinpath(SUB_DIRS[dir_type])
        mutacc_config[dir_type] = make_dir(subdir)

    # Get binaries for picard and seqkit if specified in config
    mutacc_config["binaries"] = {}

    binaries = {}
    if cli_config.get("binaries"):
        binaries = cli_config["binaries"]

    mutacc_config["binaries"]["picard"] = binaries.get("picard")
    mutacc_config["binaries"]["seqkit"] = binaries.get("seqkit")

    context.obj = mutacc_config


cli.add_command(extract_command)
cli.add_command(synthesize_command)
cli.add_command(database_group)
