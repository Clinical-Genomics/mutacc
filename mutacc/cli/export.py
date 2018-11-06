
import logging
import yaml
import tempfile
from shutil import rmtree

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
              default = 'affected')
@click.option('-s','--sex',
              type = click.Choice(['male','female']))
@click.option('--out-dir', default = './')
@click.pass_context
def export(context,
           case_query,
           variant_query,
           background_bam,
           background_fastq,
           background_fastq2,
           member,
           sex,
           out_dir):

    """
        exports dataset from DB
    """

    #Get mongo adapter from context
    adapter = context.obj['adapter']

    #Query the cases in mutaccDB
    samples, regions, variants = mutacc_query(
        adapter,
        case_query,
        variant_query,
        sex=sex,
        member=member
    )

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

    #load background files given in yaml file as dictionary
    #with open(background, "r") as in_handle:
    #    background = yaml.load(in_handle)

    #Exclude reads from the background bam files
    background = {"bam_file": background_bam,
                  "fastq_files": [background_fastq]}
    if background_fastq2: background["fastq_files"].append(background_fastq2)

    #Create temporary directory
    temp_dir = tempfile.mkdtemp("_mutacc_tmp")

    LOG.info("Temporay files stored in {}".format(temp_dir))

    make_set.exclude_from_background(out_dir = temp_dir,
                                     background = background,
                                     member = member)


    #Merge the background files with excluded reads with the bam Files
    #Holding the reads for the regions of the variants to be included in
    #validation set
    out_dir = make_dir(out_dir)
    synthetics = make_set.merge_fastqs(
        out_dir = out_dir
        )

    #Remove temporary directory
    rmtree(temp_dir)

    for synthetic in synthetics:
        LOG.info("Synthetic datasets created in {}".format(synthetic))


    #WRITE VCF FILE
    vcf_file = out_dir.joinpath("synthetic_{}.vcf".format(member))
    LOG.info("creating vcf file {}".format(str(vcf_file)))
    with open(vcf_file, "w") as vcf_handle:

        vcf_handle.write("##fileformat=VCFv4.2\n")
        vcf_handle.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(member))
        for variant in variants:

            vcf_entry = variant["vcf_entry"].split("\t")
            entry = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\tGT\t{}".format(
                vcf_entry[0], vcf_entry[1], vcf_entry[2], vcf_entry[3],
                vcf_entry[4], vcf_entry[5], vcf_entry[6], vcf_entry[7],
                variant["genotype"]
            )
            vcf_handle.write(entry+"\n")
