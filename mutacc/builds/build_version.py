import logging
import os
from pathlib import Path
import datetime


import ped_parser

from mutacc.subprocessing.get_md5 import get_md5
from mutacc.parse.path_parse import parse_path, list_files, list_dirs
from mutacc.parse.parse_ped import parse_ped


LOG = logging.getLogger(__name__)


class VersionedDataset(dict):

    def __init__(self, dataset_dir):

        super(VersionedDataset, self).__init__()
        self.dataset_dir = parse_path(dataset_dir, file_type='dir')

    def build_dataset(self, md5=False, comment=None):

        ped_file = self._find_file(self.dataset_dir, '.ped')
        family = self._parse_ped(ped_file)

        self['dataset_id'] = family['family_id']
        self['samples'] = list()

        for sample in family['samples']:
            sample_id = sample['sample_id']
            sample_dir = self.find_sample_dir(sample_id)
            sample_files = list_files(sample_dir)
            files = [{'path': str(file),
                      'md5': self._get_md5(file) if md5 else None}
                     for file in sample_files]

            self['samples'].append(
                {'sample_id': sample_id,
                 'mother': sample['mother'],
                 'father': sample['father'],
                 'files': files}
            )

        vcf_path = self._find_file(self.dataset_dir, '.vcf')
        self['vcf'] = {'path': str(vcf_path), 'md5': self._get_md5(vcf_path)}

        if comment is not None:
            self['comment'] = comment

    def find_sample_dir(self, sample_id):

        for dir in list_dirs(self.dataset_dir):
            if str(dir).split('/')[-1] == sample_id:
                return dir

        log_msg = f"directory {sample_id} not found"
        LOG.warning(log_msg)
        raise FileNotFoundError

    @staticmethod
    def _find_file(dir_path, includes):
        for file in list_files(dir_path):
            if includes in str(file).split('/')[-1]:
                return file

        log_msg = f"File with '{includes}' not found"
        LOG.warning(log_msg)
        raise FileNotFoundError

    @staticmethod
    def _parse_ped(ped_file):
        family = parse_ped(ped_file)
        return family


    @staticmethod
    def _get_md5(file_path):
        return get_md5(file_path)
