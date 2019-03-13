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
@click.pass_context
def extract_command(context, case, padding):

    """
        extract reads from case
    """
    LOG.info("extracting reads from case {0}".format(case))

    read_dir = context.obj.get('read_dir')

    case = yaml_parse(case)

    case = CompleteCase(case)

    case.get_variants(padding = padding)
    case.get_samples(read_dir)
    case.get_case()

    import_dir = context.obj.get('import_dir')

    pickle_file = import_dir.joinpath(case.case_id + "_import"+ ".mutacc")

    #Serialize case object to file for later import
    with open(pickle_file, "wb") as pickle_handle:

        pickle.dump(case, pickle_handle)

    LOG.info("to import reads into mutaccDB, do: \n    mutacc db import {}".format(
            pickle_file
        )
    )
