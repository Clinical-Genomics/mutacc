
import logging
import yaml

import click

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet

LOG = logging.getLogger(__name__)

@click.command()
@click.option('--case_query')
@click.option('--variant_query')
@click.option('--background')
@click.option('--out_dir', default = './')
@click.option('--threads', type = int)
@click.option('--temp_dir',
              default = './',
              help = "Dir to hold temporary files")
@click.pass_context
def export(context, case_query, variant_query, background, out_dir, threads, temp_dir):

    """
        exports dataset from DB
    """

    #Get mongo adapter from context
    adapter = context.obj['adapter']

    #Query the cases in mutaccDB
    cases = mutacc_query(adapter, case_query, variant_query)

    #Abort if no cases correspond to query
    num_cases = len(cases["cases"])
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    LOG.info("{} cases found, with a total of {} variants.".format(
                num_cases,
                len(cases["regions"])
            )
        )

    #make object make_set from MakeSet class
    make_set = MakeSet(**cases)

    #load background files given in yaml file as dictionary
    with open(background, "r") as in_handle:
        background = yaml.load(in_handle)

    #Exclude reads from the background bam files
    make_set.exclude_from_background(out_dir = temp_dir,
                                     backgrounds = background)
    #Merge the background files with excluded reads with the bam Files
    #Holding the reads for the regions of the variants to be included in
    #validation set
    out_dir = make_dir(out_dir)
    synthetics = make_set.merge_files(
        out_dir = out_dir,
        threads = threads
        )

    for synthetic in synthetics:
        LOG.info("Synthetic datasets created in {}".format(synthetic))
