"""
    CLI command to import case into database
"""

import logging
import json

import click
from pymongo.errors import WriteError as MongoWriteError

from mutacc.mutaccDB.insert import insert_entire_case


LOG = logging.getLogger(__name__)

@click.command('import')
@click.argument('case', type=click.Path(exists=True))
@click.pass_context
def importing(context, case):

    """
        Import cases to the database
    """
    log_msg = f"Inserting case from {case} into mutaccDB"
    LOG.info(log_msg)

    with open(case, "r") as json_handle:
        case = json.load(json_handle)

    adapter = context.obj['adapter']

    #Check if case_id already exists in collection
    if adapter.case_exists(case['case']['case_id']):
        LOG.warning("case_id not unique")
        error_msg = f"Case {case['case']['case_id']} already exists"
        raise MongoWriteError(error_msg)

    insert_entire_case(adapter, case)
