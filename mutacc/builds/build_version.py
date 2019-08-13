import logging
import os
from pathlib import Path
import datetime

import ped_parser

from mutacc.subprocessing.get_md5 import get_md5

LOG = logging.getLogger(__name__)

class VersionedDataset(dict):

    """
        Versioned dataset
    """

    def __init__(self, dataset_dir, comment=None, md5=False):

        """
            Instatiate a versioned dataset

            Args:
                dataset_dir (Path): Path to directory where dataset files are found
                comment (str): optional comment to dataset
                md5 (bool): If true, the md5 hash of files will be calculated
        """

        super(VersionedDataset, self).__init__()

        self.dataset_dir = Path(dataset_dir)
        self.md5 = md5

        self._build_samples()
        vcf_file = self._find_vcf()
        self['vcf'] = {'path': str(vcf_file),
                       'md5': get_md5(vcf_file) if self.md5 else None}

        if comment is not None:
            self['comment'] = comment

        self['created'] = datetime.datetime.utcnow()

    def _build_samples(self, md5=False):

        family_name, family_obj = self._parse_pedigree()

        self['dataset_id'] = family_name
        self['samples'] = []

        for sample_id, sample in family_obj.individuals.items():

            sample_obj = {}
            sample_obj['sample_id'] = sample_id
            sample_obj['mother'] = sample.mother
            sample_obj['father'] = sample.father

            fastq_files = self._find_sample_fastqs(sample_id)
            sample_obj['fastq'] = [{'path': str(fastq),
                                    'md5': get_md5(fastq) if self.md5 else None}
                                   for fastq in fastq_files]

            self['samples'].append(sample_obj)

    def _parse_pedigree(self):

        ped_file = self._find_ped_file()

        with open(ped_file, 'r') as ped_handle:
            ped_obj = ped_parser.FamilyParser(ped_handle)

        family_name, family_obj = list(ped_obj.families.items())[0]
        sample_names = list(family_obj.individuals.keys())

        self['samples'] = [{'sample_id': sample_id} for sample_id in sample_names]


        return family_name, family_obj

    def _find_ped_file(self):

        ped_file = None
        for file in os.listdir(self.dataset_dir):
            if file.endswith('.ped'):
                ped_file = file

        if ped_file is None:
            LOG.warning('pedigree file not found in dir')
            raise FileNotFoundError

        return self.dataset_dir.joinpath(ped_file)

    def _find_sample_fastqs(self, sample_id):

        sample_dir = None

        for file in os.listdir(self.dataset_dir):
            if file == sample_id:
                if self.dataset_dir.joinpath(file).is_dir():
                    sample_dir = self.dataset_dir.joinpath(file)
                    break

        if sample_dir is None:
            log_msg = f"No directory found with name {sample_id}"
            LOG.warning(log_msg)
            raise FileNotFoundError

        fastq_files = []

        for file in os.listdir(sample_dir):
            if '.fastq' in file:
                fastq_files.append(sample_dir.joinpath(file))


        return fastq_files


    def _find_vcf(self):

        vcf_file = None
        for file in os.listdir(self.dataset_dir):
            if '.vcf' in file:
                vcf_file = file

        if vcf_file is None:
            LOG.warning('vcf file not found in dir')
            raise FileNotFoundError

        return self.dataset_dir.joinpath(vcf_file)
