import logging
import pickle

import click
from pymongo.errors import WriteError as MongoWriteError
from mongo_adapter import get_client


from mutacc.parse.path_parse import make_dir
from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import CompleteCase
from mutacc.mutaccDB.insert import insert_entire_case


LOG = logging.getLogger(__name__)

@click.command('extract')
@click.option('-c', '--case',
              type = click.Path(exists = True),
              help = " .yaml file for case. See README.md for information on what to include or example .yaml file in data/data.yaml")
@click.option('--padding', default = 300)
@click.option('--mutacc-dir', type=click.Path())
@click.option('-o', '--out-dir', type=click.Path())
@click.pass_context
def extract_command(context, case, padding, mutacc_dir, out_dir):

    """
        extract reads from case
    """
    LOG.info("extracting reads from case {0}".format(case))

    mutacc_dir = mutacc_dir or context.obj.get('mutacc_dir')
    mutacc_dir = make_dir(mutacc_dir)

    case = yaml_parse(case)

    case = CompleteCase(case)

    case.get_variants(padding = padding)
    case.get_samples(mutacc_dir)
    case.get_case()

    out_dir = out_dir or context.obj.get('case_dir')
    out_dir = make_dir(out_dir)

    pickle_file = out_dir.joinpath(case.case_id + "_case"+ ".mutacc")

    #Serialize case object to file for later import
    with open(pickle_file, "wb") as pickle_handle:

        pickle.dump(case, pickle_handle)

    LOG.info("to import reads into mutaccDB, do: \n    mutacc db import {}".format(
            pickle_file
        )
    )
