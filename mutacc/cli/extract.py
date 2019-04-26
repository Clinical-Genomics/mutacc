"""
    CLI command to extract reads from case, and make an importable object
"""

import logging
import pickle

import click

from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import Case



LOG = logging.getLogger(__name__)

@click.command('extract')
@click.option('-c', '--case',
              type=click.Path(exists=True),
              help=(".yaml file for case. See README.md for information on what "
                    "to include or example .yaml file in data/data.yaml")
             )
@click.option('--padding', type=int, default=1000)
@click.option('--picard-executable', type=click.Path(exists=True))
@click.pass_context
def extract_command(context, case, padding, picard_executable):

    """
        extract reads from case
    """
    log_msg = f"extracting reads from case {case}"
    LOG.info(log_msg)

    read_dir = context.obj.get('read_dir')

    case = yaml_parse(case)

    picard_executable = context.obj['binaries'].get('picard') or picard_executable
    case = Case(input_case=case,
                read_dir=read_dir,
                padding=padding,
                picard_exe=picard_executable)

    import_dir = context.obj.get('import_dir')

    pickle_file = import_dir.joinpath(case.case_id + "_import"+ ".mutacc")

    #Serialize case object to file for later import
    with open(pickle_file, "wb") as pickle_handle:

        pickle.dump(case, pickle_handle)


    log_msg = f"to import reads into mutaccDB, do:\n    mutacc db import {pickle_file}"
    LOG.info(log_msg)
