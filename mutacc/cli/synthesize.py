"""
    Command to make synthetic dataset
"""

import logging
import click
import json

from mutacc.parse.path_parse import make_dir
from mutacc.builds.build_dataset import Dataset

from mutacc.resources import (path_to_background_bam_file,
                              path_to_background_fastq1_file,
                              path_to_background_fastq2_file)

LOG = logging.getLogger(__name__)

@click.command('synthesize')
@click.option('-b', '--background-bam', type=click.Path())
@click.option('-f', '--background-fastq', type=click.Path())
@click.option('-f2', '--background-fastq2', type=click.Path())
@click.option('--dataset-dir', type=click.Path())
@click.option('-q', '--query', type=click.Path(exists=True))
@click.option('-s', '--save-background', is_flag=True)
@click.option('-j', '--json-out', is_flag=True)
@click.pass_context
def synthesize_command(context,
                       background_bam,
                       background_fastq,
                       background_fastq2,
                       dataset_dir,
                       query,
                       save_background,
                       json_out):

    """
        Command to make synthetic dataset
    """

    # load json file containing a mutacc query
    with open(query, "r") as json_handle:

        samples, _, variants, sample_name = json.load(json_handle)

    #Abort if no cases correspond to query
    num_cases = len(samples)
    if num_cases == 0:
        LOG.warning("No cases were found")
        context.abort()

    num_variants = len(variants)

    log_msg = f"{num_cases} cases found, with a total of {num_variants} variants."
    LOG.info(log_msg)

    if context.obj.get('demo', False):
        background_bam = path_to_background_bam_file
        background_fastq = path_to_background_fastq1_file
        background_fastq2 = path_to_background_fastq2_file

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

    if json_out:
        output_info = {'fastq_files': [str(synthetic) for synthetic in synthetics]}
        output_json = json.dumps(output_info)
        click.echo(output_json)
