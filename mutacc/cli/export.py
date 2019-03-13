
import logging
import yaml
import tempfile
import pickle
from shutil import rmtree

import click

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet
from mutacc.utils.vcf_writer import vcf_writer
from mutacc.parse.path_parse import parse_path
from mutacc.utils.sort_variants import sort_variants

LOG = logging.getLogger(__name__)

@click.command()
@click.option('-c','--case-query')
@click.option('-v','--variant-query')
@click.option('-m', '--member',
              type = click.Choice(['father','mother','child','affected']),
              default = 'affected')
@click.option('-s','--sex',
              type = click.Choice(['male','female']))
@click.option('--vcf-dir', type = click.Path(exists=True))
@click.option('-p', '--proband', is_flag = True)
@click.option('-n', '--sample-name')
@click.pass_context
def export(context,
           case_query,
           variant_query,
           member,
           sex,
           vcf_dir,
           proband,
           sample_name):

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
        member=member,
        proband=proband
    )

    sample_name = sample_name or member

    #Info to be dumped into file
    query = (samples, regions, variants, sample_name)

    query_dir = context.obj.get('query_dir')

    #pickle query
    pickle_file = query_dir.joinpath(sample_name + "_query.mutacc")

    with open(pickle_file, "wb") as pickle_handle:

        pickle.dump(query, pickle_handle)

    LOG.info("Query stored in {}".format(pickle_file))

    #sort variants
    found_variants = sort_variants(variants)

    #WRITE VCF FILE
    vcf_dir = vcf_dir or context.obj.get('vcf_dir')
    vcf_dir = make_dir(vcf_dir)
    vcf_file = vcf_dir.joinpath("{}_variants.vcf".format(sample_name))
    LOG.info("creating vcf file {}".format(str(vcf_file)))
    vcf_writer(found_variants, vcf_file, sample_name)
