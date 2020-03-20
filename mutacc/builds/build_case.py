"""
    Module for building case
"""

import logging
import time

from mutacc.builds.build_variant import get_variants
from mutacc.builds.build_sample import get_samples
from mutacc.parse.path_parse import make_dir
from mutacc.utils.constants import PADDING

LOG = logging.getLogger(__name__)


class Case(dict):
    """
        Class with methods for handling case objects
    """

    def __init__(
        self, input_case, read_dir, padding=None, sv_padding=None, picard_exe=None, vcf_parse=None
    ):

        """
            Object is instantiated with a case, a dictionary giving all relevant information about
            the case.

            Args:
                input_case(dict): dictionary containing information about the variant, with three fields;
                                  case, samples, and variants.
                read_dir(str): Directory fastq-files are placed
                padding(int): given in bp, extends the region for where to look for reads in the
                               alignment file.
                picard_exe(str): path to picard executable
                vcf_parse(str): path to yaml file with vcf parsing information
        """

        super(Case, self).__init__()

        self.input_case = input_case
        self.case_id = input_case["case"]["case_id"]

        # Build variants
        self["variants"] = self._build_variants(padding=padding, sv_padding=sv_padding, vcf_parse=vcf_parse)

        # Build samples
        self["samples"] = self._build_samples(
            read_dir=read_dir, padding=padding, picard_exe=picard_exe
        )
        # Build case
        self["case"] = self.input_case["case"]

    def _build_variants(self, padding=None, sv_padding=None, vcf_parse=None):
        """
            Method that parses the vcf in the case dictionary.

            Args:

                padding(int): given in bp, extends the region for where to look for reads in the
                              alignment file.
                vcf_parse(str): path to yaml file with vcf parsing information

        """

        # Get padding
        padding = padding or PADDING

        variant_objects = []

        for variant_object in get_variants(
                vcf_file=self.input_case["variants"],
                padding=padding,
                sv_padding=sv_padding,
                vcf_parse=vcf_parse
        ):

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

        date_str = time.strftime("%Y-%m-%d")
        sub_dir = f"{self.input_case['case']['case_id']}/{date_str}"

        case_dir = make_dir(read_dir.joinpath(sub_dir))
        sample_objects = []
        for sample in get_samples(
            samples=self.input_case["samples"],
            variants=self["variants"],
            padding=padding,
            picard_exe=picard_exe,
            case_dir=case_dir,
        ):

            sample_objects.append(sample)

        return sample_objects
