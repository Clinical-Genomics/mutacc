
import logging
import yaml
import tempfile
import pickle
from shutil import rmtree

import click

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet
from mutacc.parse.path_parse import parse_path
from mutacc.utils.sort_variants import sort_variants



LOG = logging.getLogger(__name__)

@click.command('synthesize')

@click.pass_context
@click.option('-b','--background-bam', type = click.Path())
@click.option('-f','--background-fastq', type = click.Path())
@click.option('-f2','--background-fastq2', type = click.Path())
@click.option('--out-dir', type = click.Path())
@click.option('--tmp-dir', type = click.Path())
@click.option('-q', '--query', type = click.Path(exists=True))
@click.option('-s', '--save-background', is_flag = True)
def synthesize_command(context,
                       background_bam,
                       background_fastq,
                       background_fastq2,
                       out_dir,
                       tmp_dir,
                       query,
                       save_background):

    #unpickle query
    with open(query, "rb") as pickle_handle:

        samples, regions, variants, sample_name = pickle.load(pickle_handle)

    #Abort if no cases correspond to query
    num_cases = len(samples)
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    num_variants = len(variants)

    LOG.info("{} cases found, with a total of {} variants.".format(
                num_cases,
                num_variants)
            )

    #make object make_set from MakeSet class
    make_set = MakeSet(samples, regions)

    #Exclude reads from the background bam files
    background = {"bam_file": background_bam,
                  "fastq_files": [background_fastq]}
    if background_fastq2: background["fastq_files"].append(background_fastq2)

    #Create temporary directory
    #tmp_dir = tempfile.mkdtemp("_mutacc_tmp")

    tmp_dir = tmp_dir or context.obj.get('tmp_dir')
    tmp_dir = make_dir(tmp_dir)

    LOG.info("Temporay files stored in {}".format(tmp_dir))

    make_set.exclude_from_background(out_dir = tmp_dir,
                                     background = background,
                                     member = sample_name)


    #Merge the background files with excluded reads with the bam Files
    #Holding the reads for the regions of the variants to be included in
    #validation set
    out_dir = out_dir or context.obj.get('dataset_dir')
    out_dir = make_dir(out_dir)
    synthetics = make_set.merge_fastqs(
            out_dir = out_dir,
            save_background = save_background
        )

    #Remove temporary directory
    #rmtree(temp_dir)

    for synthetic in synthetics:
        LOG.info("Synthetic datasets created in {}".format(synthetic))
