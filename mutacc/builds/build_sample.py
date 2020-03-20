"""
    Module for building samples
"""

import logging

from mutacc.utils.bam_handler import BAMContext
from mutacc.parse.path_parse import make_dir, parse_path
from mutacc.utils.fastq_handler import fastq_extract
from mutacc.subprocessing.bam_to_fastq import bam_to_fastq

LOG = logging.getLogger(__name__)

class Sample(dict):

    """
        Class to represent sample
    """

    def __init__(self, input_sample, variants, padding, picard_exe, case_dir):

        super(Sample, self).__init__(**input_sample)

        self.input_sample = input_sample
        self.variants = variants
        self.padding = padding
        self.picard_exe = picard_exe
        self.case_dir = case_dir
        self.bam_file = parse_path(self.input_sample['bam_file'])

        # Build sample
        self._build_sample()

    def _build_sample(self):

        sample_dir = make_dir(
            self.case_dir.joinpath(self.input_sample['sample_id'])
        )

        if self.input_sample.get('fastq_files'):
            self._extract_fastq(sample_dir)
        else:
            self._extract_bam(sample_dir)

    def _extract_fastq(self, sample_dir):


        # For each variant, the reads spanning this genomic region in
        # the bam file are found

        with BAMContext(bam_file=self.bam_file) as bam_handle:
            for variant in self.variants:

                bam_handle.find_names_from_region(
                    chrom=variant["chrom"],
                    start=variant["start"],
                    end=variant["end"],
                    padding=variant["padding"])

                read_ids = bam_handle.found_reads

        log_msg = f"{len(read_ids)} reads found for sample {self.input_sample['sample_id']}"
        LOG.info(log_msg)

        # Given the read_ids, and the fastq files, the reads are
        # extracted from the fastq files
        LOG.info("Search in fastq file")

        variant_fastq_files = fastq_extract(
            self.input_sample['fastq_files'],
            read_ids,
            dir_path=sample_dir
            )

        # Add path to fastq files with the reads containing the variant
        # to the sample object

        self['variant_fastq_files'] = variant_fastq_files


    def _extract_bam(self, sample_dir):

        with BAMContext(self.bam_file, out_dir=sample_dir) as bam_handle:

            for variant in self.variants:

                bam_handle.find_reads_from_region(
                    chrom=variant["chrom"],
                    start=variant["start"],
                    end=variant["end"],
                    padding=variant["padding"]
                )

            log_msg = "{} reads found for sample {}".format(
                bam_handle.record_number,
                self.input_sample['sample_id']
            )
            LOG.info(log_msg)
            variant_bam_file = bam_handle.out_file
            self.input_sample["variant_bam_file"] = variant_bam_file
            file_name = parse_path(variant_bam_file).name
            paired = bam_handle.paired

        # Convert bam to fastq
        fastq1 = str(sample_dir.joinpath(file_name.split('.')[0] + '_R1.fastq.gz'))
        fastq2 = None
        if paired:
            fastq2 = str(sample_dir.joinpath(file_name.split('.')[0] + '_R2.fastq.gz'))

        # Use picard SamToFastq to convert from bam to paired end fastqs

        bam_to_fastq(
            variant_bam_file,
            fastq1,
            fastq2,
            picard_exe=self.picard_exe
        )

        self["variant_fastq_files"] = [fastq1, fastq2]
        self["paired_reads"] = paired

def get_samples(samples, variants, padding, picard_exe, case_dir):

    """
        Parse a list of samples, given as input to importable sample objects

        Args:
            samples (list(dict)): list of samples
            variants (list(mutacc.builds.build_variant.Variant)): list of variants
            padding (int): padding to be used
            picard_exe (str): path to picard binary
            case_dir (Path): path to dir where reads for case are to be stored

    """

    for sample in samples:

        yield Sample(sample, variants, padding, picard_exe, case_dir)
