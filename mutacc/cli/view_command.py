import click
import json
from pprint import pprint


@click.command('cases')
@click.option('-c', '--case-id')
@click.pass_context
def view_cases(context,case_id):
    """
        View cases in database
    """

    adapter = context.obj['adapter']

    if case_id is not None:
        results = adapter.find_case({'case_id': case_id})

    else:
        results = adapter.find_cases({})

    click.echo(pprint(results))

@click.command('variants')
@click.option('-v', '--variant-id')
@click.pass_context
def view_variants(context, variant_id):
    """
        View variants in database
    """
    adapter = context.obj['adapter']

    results = []
    if variant_id is not None:
        results = adapter.find_variant({'display_name': variant_id})

    else:
        results = adapter.find_variants({})

    click.echo(pprint(results))
