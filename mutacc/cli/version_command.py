import click
import json
from pprint import pprint
import logging

from mutacc.parse.path_parse import parse_path
from mutacc.builds.build_version import VersionedDataset
from mutacc.mutaccDB.insert import insert_version

LOG = logging.getLogger(__name__)

@click.command('version')
@click.option('-d', '--dataset-dir',
              type=click.Path(exists=True),
              help="path to directory with dataset")
@click.option('-m', '--md5',
              is_flag=True,
              help="Get md5 sum of files")
@click.option('-c', '--comment',
              type=str,
              help="Additional comment")
@click.pass_context
def version_command(context, dataset_dir, md5, comment):
    """
        Version dataset and truth set
    """

    log_msg = f"Versioning dataset"
    LOG.info(log_msg)

    adapter = context.obj['adapter']

    dataset_dir=parse_path(dataset_dir, file_type='dir')
    dataset = VersionedDataset(dataset_dir=dataset_dir)
    dataset.build_dataset(md5=md5, comment=comment)

    insert_version(adapter, dataset)
