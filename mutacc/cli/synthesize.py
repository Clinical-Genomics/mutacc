"""
    Command to make synthetic dataset
"""

import logging
import pickle
import click

from mutacc.parse.path_parse import make_dir
from mutacc.builds.build_dataset import Dataset

LOG = logging.getLogger(__name__)

@click.command('synthesize')
@click.pass_context
@click.option('-b', '--background-bam', type=click.Path())
@click.option('-f', '--background-fastq', type=click.Path())
@click.option('-f2', '--background-fastq2', type=click.Path())
@click.option('--dataset-dir', type=click.Path())
@click.option('-q', '--query', type=click.Path(exists=True))
@click.option('-s', '--save-background', is_flag=True)
def synthesize_command(context,
                       background_bam,
                       background_fastq,
                       background_fastq2,
                       dataset_dir,
                       query,
                       save_background):

    """
        Command to make synthetic dataset
    """

    # unpickle query
    with open(query, "rb") as pickle_handle:

        samples, _, variants, sample_name = pickle.load(pickle_handle)

    #Abort if no cases correspond to query
    num_cases = len(samples)
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    num_variants = len(variants)

    log_msg = f"{num_cases} cases found, with a total of {num_variants} variants."
    LOG.info(log_msg)

    background = {"bam_file": background_bam,
                  "fastq_files": [background_fastq]}
    if background_fastq2:
        background["fastq_files"].append(background_fastq2)

    #Create temporary directory
    temp_dir = context.obj.get('temp_dir')

    log_msg = f"Temporay files stored in {temp_dir}"
    LOG.info(log_msg)

    seqkit_executable = context.obj['binaries'].get('seqkit')
    dataset_dir = dataset_dir or context.obj.get('dataset_dir')
    dataset_dir = make_dir(dataset_dir)

    #make object make_set from Dataset class
    dataset = Dataset(samples=samples,
                      variants=variants,
                      tmp_dir=temp_dir,
                      background=background,
                      member=sample_name,
                      out_dir=dataset_dir,
                      seqkit_exe=seqkit_executable,
                      save_background=save_background)

    synthetics = dataset.synthetic_fastqs

    for synthetic in synthetics:
        log_msg = f"Synthetic datasets created in {synthetic}"
        LOG.info(log_msg)
