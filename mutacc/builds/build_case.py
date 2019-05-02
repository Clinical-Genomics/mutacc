"""
    Module for building case
"""

import logging

from mutacc.builds.build_variant import get_variants
from mutacc.builds.build_sample import get_samples
from mutacc.parse.path_parse import make_dir
from mutacc.utils.constants import PADDING

LOG = logging.getLogger(__name__)

class Case(dict):
    """
        Class with methods for handling case objects
    """
    def __init__(self, input_case, read_dir, padding=None, picard_exe=None):

        """
            Object is instantiated with a case, a dictionary giving all relevant information about
            the case.

            Args:

                case(dict): dictionary containing information about the variant, with three fields;
                            case, samples, and variants.
        """

        super(Case, self).__init__()

        self.input_case = input_case
        self.case_id = input_case['case']['case_id']

        # Build variants
        rank_model_version = self.input_case['case'].get('rank_model_version')
        self['variants'] = self._build_variants(padding=padding,
                                                rank_model_version=rank_model_version)

        # Build samples
        self['samples'] = self._build_samples(read_dir=read_dir,
                                              padding=padding,
                                              picard_exe=picard_exe)
        # Build case
        self['case'] = self.input_case['case']

    def _build_variants(self, padding=None, rank_model_version=None):
        """
            Method that parses the vcf in the case dictionary.

            Args:

                padding(int): given in bp, extends the region for where to look for reads in the
                alignment file.
        """

        # Get padding
        padding = padding or PADDING

        variant_objects = []

        for variant_object in get_variants(self.input_case["variants"],
                                           padding=padding,
                                           rank_model_version=rank_model_version):

            # Append the variant object to the list
            variant_objects.append(variant_object)

        return variant_objects

    def _build_samples(self, read_dir, padding=None, picard_exe=None):
        """
            Method makes a list of sample objects, ready to load into a mongodb. This includes
            looking for the raw reads responsible for the variants in the vcf for each sample,
            write them to fastq files, and add the path to these files in the sample object.

            Args:

                read_dir(pathlib.Path): Path to directory where the new fastq files are to be
                stored.
        """



        case_dir = make_dir(read_dir.joinpath(self.input_case['case']['case_id']))
        sample_objects = []
        for sample in get_samples(samples=self.input_case["samples"],
                                  variants=self['variants'],
                                  padding=padding,
                                  picard_exe=picard_exe,
                                  case_dir=case_dir):

            sample_objects.append(sample)

        return sample_objects
