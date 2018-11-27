
import logging
import yaml
import tempfile
import pickle
from shutil import rmtree

import click

from mutacc.parse.path_parse import make_dir
from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet
from mutacc.utils.vcf_writer import vcf_writer, append_gt
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
@click.option('--out-dir', type = click.Path())
@click.option('--vcf-dir', type = click.Path())
@click.option('--merge-vcf', type = click.Path())
@click.option('-p', '--proband', is_flag = True)
@click.option('-n', '--sample-name')
@click.pass_context
def export(context,
           case_query,
           variant_query,
           member,
           sex,
           out_dir,
           vcf_dir,
           merge_vcf,
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

    query = (samples, regions, variants, sample_name)

    out_dir = out_dir or context.obj.get('query_dir')
    out_dir = make_dir(out_dir)

    #pickle query
    pickle_file = out_dir.joinpath(sample_name + "_query.mutacc")

    with open(pickle_file, "wb") as pickle_handle:

        pickle.dump(query, pickle_handle)

    LOG.info("Query stored in {}".format(pickle_file))

    #sort variants
    found_variants = {str(variant['_id']): variant for variant in variants}

    all_variants = adapter.find_variants({})
    all_variants = sort_variants(all_variants)

    #WRITE VCF FILE
    if merge_vcf:
        vcf_file = parse_path(merge_vcf)
        LOG.info("appending genotype field for {} in {}".format(
            sample_name,
            str(vcf_file)
            )
        )
        append_gt(all_variants, found_variants, vcf_file, sample_name)
    else:

        vcf_dir = vcf_dir or context.obj.get('vcf_dir')
        vcf_dir = make_dir(vcf_dir)
        vcf_file = vcf_dir.joinpath("synthetic_{}.vcf".format(sample_name))
        LOG.info("creating vcf file {}".format(str(vcf_file)))

        vcf_writer(all_variants, found_variants, vcf_file, sample_name)
