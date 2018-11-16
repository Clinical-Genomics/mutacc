import click
import json
from pprint import pprint


@click.command('view')
@click.option('-c', '--case-query')
@click.option('-v', '--variant-query')
@click.pass_context
def view_command(context, case_query, variant_query):
    """
        View cases or variants in database
    """
    adapter = context.obj['adapter']

    results = []
    if case_query:
        query = json.loads(case_query)
        results = adapter.find_cases(query)

    elif variant_query:

        query = json.loads(variant_query)
        results = adapter.find_variants(query)

    click.echo(pprint(results))
