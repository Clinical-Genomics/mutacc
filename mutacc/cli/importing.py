import click

from mongo_adapter import get_client

from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import CompleteCase
from mutacc.mutaccDB.db_adapter import MutaccAdapter
from mutacc.mutaccDB.insert import insert_entire_case


@click.command('import')
@click.option('-c', '--case', type = click.Path(exists = True), help = " .yaml file for case. See README.md for information on what to include or example .yaml file in data/data.yaml")
@click.option('--padding', type = click.IntRange(0, 5000), default = 300)
@click.pass_context
def importing(context, case, padding):

    """
        Import cases to the database
    """
            
    case = yaml_parse(case)
    
    case = CompleteCase(case)

    case.get_variants(padding = padding)
    case.get_samples()
    case.get_case()

    client = get_client(host = context.obj["host"], port = context.obj["port"])

    adapter = MutaccAdapter(client = client, db_name = "mutacc")

    insert_entire_case(adapter, case)


