import logging
import pickle

import click
from pymongo.errors import WriteError as MongoWriteError
from mongo_adapter import get_client

from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import CompleteCase
from mutacc.mutaccDB.insert import insert_entire_case


LOG = logging.getLogger(__name__)

@click.command('import')
@click.argument('case', type = click.Path(exists=True))
@click.pass_context
def importing(context, case):

    """
        Import cases to the database
    """
    LOG.info("Inserting case from {0} into mutaccDB".format(case))

    with open(case, "rb") as pickle_handle:
        case = pickle.load(pickle_handle)

    adapter = context.obj['adapter']

    #Check if case_id already exists in collection
    if adapter.case_exists(case.case_id):
        LOG.warning("case_id not unique")
        raise MongoWriteError("Case {} already exists".format(
                case.case_id
            )
        )

    insert_entire_case(adapter, case)

    
