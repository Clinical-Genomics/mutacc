
import logging
import yaml

import click

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet

LOG = logging.getLogger(__name__)

@click.command()
@click.option('-c','--case-query')
@click.option('-v','--variant-query')
@click.option('-b','--background-bam')
@click.option('-f','--background-fastq')
@click.option('-f2','--background-fastq2')
@click.option('-m', '--member',
              type = click.Choice(['father','mother','child','affected']),
              default = 'single')
@click.option('--out-dir', default = './')
@click.option('--temp-dir',
              default = './',
              help = "Dir to hold temporary files")
@click.pass_context
def export(context,
           case_query,
           variant_query,
           background_bam,
           background_fastq,
           background_fastq2,
           member,
           out_dir,
           temp_dir):

    """
        exports dataset from DB
    """

    #Get mongo adapter from context
    adapter = context.obj['adapter']

    #Query the cases in mutaccDB
    cases = mutacc_query(adapter, case_query, variant_query)

    #Abort if no cases correspond to query
    num_cases = len(cases)
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    num_variants = 0
    for case in cases:
        num_variants += len(case.variants)

    LOG.info("{} cases found, with a total of {} variants.".format(
                num_cases,
                num_variants)
            )

    #make object make_set from MakeSet class
    make_set = MakeSet(cases)

    #load background files given in yaml file as dictionary
    #with open(background, "r") as in_handle:
    #    background = yaml.load(in_handle)

    #Exclude reads from the background bam files
    background = {"bam_file": background_bam,
                  "fastq_files": [background_fastq]}
    if background_fastq2: background["fastq_files"].append(background_fastq2)

    make_set.exclude_from_background(out_dir = temp_dir,
                                     background = background,
                                     member = member)


    #Merge the background files with excluded reads with the bam Files
    #Holding the reads for the regions of the variants to be included in
    #validation set
    out_dir = make_dir(out_dir)
    synthetics = make_set.merge_fastqs(
        out_dir = out_dir,
        member = member
        )

    for synthetic in synthetics:
        LOG.info("Synthetic datasets created in {}".format(synthetic))
