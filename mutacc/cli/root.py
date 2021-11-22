import logging
import sys
from pathlib import Path

import click
import coloredlogs
import mongo_adapter
import yaml
from mutacc import __version__
from mutacc.mutaccDB.db_adapter import MutaccAdapter
from mutacc.parse.path_parse import make_dir, parse_path
from mutacc.resources import default_vcf_parser

from .constants import PADDING, SUB_DIRS, SV_PADDING
from .database import database_group as database_group
from .extract import extract_command as extract_command
from .synthesize import synthesize_command as synthesize_command

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.group()
@click.option("--loglevel", default="INFO", type=click.Choice(LOG_LEVELS))
@click.option("-c", "--config-file", type=click.Path(exists=True))
@click.option("-r", "--root-dir", type=click.Path(exists=True))
@click.option("-d", "--demo", is_flag=True)
@click.option("--vcf-parser", type=click.Path(exists=True))
@click.version_option(__version__)
@click.pass_context
def cli(context, loglevel, config_file, root_dir, demo, vcf_parser):

    coloredlogs.install(level=loglevel)
    LOG.info("Running mutacc")

    cli_config = {}
    if demo:
        host = "localhost"
        port = 27017
        db_name = "mutacc-demo"
        username = None
        password = None
        padding = PADDING
        sv_padding = SV_PADDING
        root_dir = make_dir(root_dir or "./mutacc_demo_root")

    else:

        if config_file:
            with open(config_file, "r") as in_handle:
                cli_config = yaml.safe_load(in_handle)

        host = cli_config.get("host") or "localhost"
        port = cli_config.get("port") or 27017
        uri = cli_config.get("uri")
        db_name = cli_config.get("database") or "mutacc"
        username = cli_config.get("username")
        password = cli_config.get("password")
        root_dir = cli_config.get("root_dir") or root_dir
        padding = cli_config.get("padding")
        sv_padding = cli_config.get("sv_padding")

        if not root_dir:
            LOG.warning(
                "Please provide a root directory, through option --root-dir or in config_file"
            )
            context.abort()

    vcf_parser = get_vcf_parser(parser_file=vcf_parser, config_dict=cli_config)

    mutacc_config = {}
    mutacc_config["host"] = host
    mutacc_config["port"] = port
    mutacc_config["uri"] = uri
    mutacc_config["username"] = username
    mutacc_config["password"] = password
    mutacc_config["db_name"] = db_name
    mutacc_config["vcf_parser_import"] = vcf_parser.get("import")
    mutacc_config["vcf_parser_export"] = vcf_parser.get("export")
    mutacc_config["root_dir"] = parse_path(root_dir, file_type="dir")
    mutacc_config["demo"] = demo
    mutacc_config["padding"] = padding
    mutacc_config["sv_padding"] = sv_padding

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


def get_vcf_parser(parser_file: str = None, config_dict: dict = None):

    """
    Finds and return vcf parser specification from file, config or default

    Args:
        from_file(str): file path to yaml formatted parser specifications
        from_config(dict): vcf
    """
    if parser_file:
        with open(parser_file, "r") as parser_handle:
            vcf_parser = yaml.safe_load(parser_handle)
    elif config_dict and config_dict.get("vcf_parser"):
        vcf_parser = config_dict["vcf_parser"]
    else:
        with open(default_vcf_parser, "r") as parser_handle:
            vcf_parser = yaml.safe_load(parser_handle)

    return vcf_parser
