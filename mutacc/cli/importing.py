import logging

import click
from pymongo.errors import WriteError as MongoWriteError
from mongo_adapter import get_client

from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import CompleteCase
from mutacc.mutaccDB.insert import insert_entire_case


LOG = logging.getLogger(__name__)

@click.command('import')
@click.option('-c', '--case',
              type = click.Path(exists = True),
              help = " .yaml file for case. See README.md for information on what to include or example .yaml file in data/data.yaml")
@click.option('--padding', default = 300)
@click.pass_context
def importing(context, case, padding):

    """
        Import cases to the database
    """
    LOG.info("Inserting case from {0} into mutaccDB".format(case))
    case = yaml_parse(case)

    case = CompleteCase(case)

    adapter = context.obj['adapter']

    #Check if case_id already exists in collection 'cases'
    if adapter.case_exists(case.case_id):
        LOG.warning("case_id not unique")
        raise MongoWriteError("Case %s already exists" % (case.case_id))

    case.get_variants(padding = padding)
    case.get_samples(context.obj['mutacc_dir'])
    case.get_case()


    insert_entire_case(adapter, case)
