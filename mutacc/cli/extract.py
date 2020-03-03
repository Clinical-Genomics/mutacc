"""
    CLI command to extract reads from case, and make an importable object
"""

import logging
import json

import click

from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import Case
from mutacc.cli.constants import PADDING, SV_PADDING

from mutacc.resources import DEMO_CASE

LOG = logging.getLogger(__name__)


@click.command("extract")
@click.option(
    "-c",
    "--case",
    type=click.Path(exists=True),
    help=(
        ".yaml file for case. See README.md for information on what "
        "to include or example .yaml file in data/data.yaml"
    ),
)
@click.option("--padding", type=int, help="padding around SNVs and indels")
@click.option("--sv-padding", type=int, help="padding around SVs")
@click.option("--picard-executable", type=click.Path(exists=True))
@click.pass_context
def extract_command(context, case, padding, sv_padding, picard_executable):

    """
        extract reads from case
    """
    log_msg = f"extracting reads from case {case}"
    LOG.info(log_msg)

    read_dir = context.obj.get("read_dir")

    if context.obj.get("demo", False):
        input_case = DEMO_CASE
    else:
        input_case = yaml_parse(case)

    picard_executable = context.obj["binaries"].get("picard") or picard_executable
    padding = padding or context.obj.get("padding") or PADDING
    sv_padding = sv_padding or context.obj.get("sv_padding") or SV_PADDING
    case_obj = Case(
        input_case=input_case,
        read_dir=read_dir,
        padding=padding,
        sv_padding=sv_padding,
        picard_exe=picard_executable,
        vcf_parse=context.obj.get("vcf_parser_import"),
    )

    import_dir = context.obj.get("import_dir")

    json_file = import_dir.joinpath(case_obj.case_id + "_import_mutacc" + ".json")

    # Serialize case object to file for later import
    with open(json_file, "w") as json_handle:

        json.dump(case_obj, json_handle)

    log_msg = f"to import reads into mutaccDB, do:\n    mutacc db import {json_file}"
    LOG.info(log_msg)
