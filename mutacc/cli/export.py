
import logging
import yaml

import click

from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet

LOG = logging.getLogger(__name__)

@click.command()
@click.option('--case_query')
@click.option('--variant_query')
@click.option('--background')
@click.pass_context
def export(context, case_query, variant_query, background):

    """
        exports dataset from DB
    """

    adapter = context.obj['adapter']

    cases = mutacc_query(adapter, case_query, variant_query)

    num_cases = len(cases["cases"])
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    LOG.info("{} cases found, with a total of {} variants.".format(
                num_cases,
                len(cases["regions"])
            )
        )

    make_set = MakeSet(**cases)

    with open(background, "r") as in_handle:
        background = yaml.load(in_handle)

    make_set.exclude_from_background(out_dir = "/Users/adam.rosenbaum/Desktop",
                                     backgrounds = background)


    #for case in cases["cases"]:

    #    click.echo(organize_samples(case["samples"]))

    #for variant in cases["variants"]:

    #    click.echo(variant)

    #for region in cases["regions"]:

    #    click.echo(region)
