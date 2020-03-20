"""
    Module to build synthetic dataset
"""

import logging
import os

from mutacc.utils.bam_handler import BAMContext
from mutacc.subprocessing.exclude_from_fastq import exclude_from_fastq
from mutacc.subprocessing.merge_fastqs import merge_fastqs as merge_fastqs_sub
from mutacc.parse.path_parse import parse_path

LOG = logging.getLogger(__name__)

class Dataset():

    """
        class with methods for constructing a synthetic bam file, enriched with
        variants from the mutacc DB.
    """

    def __init__(self, samples, variants, tmp_dir, background, member, out_dir,
                 seqkit_exe=None, save_background=True):
        """
            Args:
                samples (mutacc.utils.pedigree.Individual): list of samples. sample
                    is parsed with the Individual class
                regions (list(dict)): list of regions. Each region is
                    represented as a dictionary with keys 'chrom', 'start', 'end'
        """
        self.samples = samples
        self.variants = variants
        self.tmp_dir = tmp_dir
        self.background = background
        self.member = member

        self.excluded_backgrounds = self.exclude_from_background(seqkit_exe=seqkit_exe)
        self.synthetic_fastqs = self.merge_fastqs(out_dir=out_dir,
                                                  save_background=save_background)

    def exclude_from_background(self, seqkit_exe=None):

        """
            for each background fastq file exclude the reads overlapping with
            any region in self.regions by finding the names of the reads, and
             writing new fastq files excluding these reads.

            Args:
                tmp_dir (str): path to directory where fastq_files with excluded
                               reads, i.e. the 'background' reads.
                backgrounds (list): list of paths to the 'background' bam files
                member (str): synthetic family member for synthetic dataset.
                    choices: 'child', 'father', 'mother', 'affected'
        """

        bam_file = parse_path(self.background["bam_file"])
        fastq_files = [parse_path(fastq) for fastq in self.background["fastq_files"]]

        with BAMContext(bam_file=bam_file) as bam_handle:
            #for each region, find the reads overlapping
            for variant in self.variants:
                bam_handle.find_names_from_region(chrom=variant["chrom"],
                                                  start=variant["start"],
                                                  end=variant["end"],
                                                  padding=variant["padding"])

            log_msg = f"{bam_handle.record_number} reads to be excluded from {fastq_files}"
            LOG.info(log_msg)

            name_file = bam_handle.make_names_temp(self.tmp_dir)
            excluded_backgrounds = []
            for fastq_file in fastq_files:

                fastq_path = str(fastq_file)
                out_name = str(self.member) + "_" + str(fastq_file.name)
                out_path = str(self.tmp_dir.joinpath(out_name))

                #Here command line tool seqkit grep is used
                exclude_from_fastq(name_file,
                                   out_path,
                                   fastq_path,
                                   seqkit_exe=seqkit_exe)

                excluded_backgrounds.append(out_path)

        return excluded_backgrounds



    def merge_fastqs(self, out_dir, save_background=True):
        """
            Merge the background file with the fastq_files Holding
            the reads supporting the variants

            Args:
                out_dir (path): Path to directory where synthetic fastqs are stored
                save_background (bool): If true, the backgrounds with excluded
                                        reads are not removed.
        """
        synthetic_fastqs = []

        out_dir = parse_path(out_dir, file_type='dir')

        reads = len(self.excluded_backgrounds)

        #For each fastq file given as background (two if paired end)
        for i in range(reads):

            fastq_list = [self.excluded_backgrounds[i]]

            for sample in self.samples:

                if len(sample['variant_fastq_files']) != reads:
                    continue

                fastq_list.append(sample['variant_fastq_files'][i])

            file_name = parse_path(self.excluded_backgrounds[i]).name
            out_path = out_dir.joinpath("synthetic_"+file_name)

            LOG.info("Merging fastq files")

            try:
                merge_fastqs_sub(fastq_list, out_path)

            except:

                log_msg = f"Files were not merged, background files in {out_dir} not removed"
                LOG.critical(log_msg)
                raise

            synthetic_fastqs.append(out_path)

        #Remove background fastqs
        if not save_background:
            for background in self.excluded_backgrounds:
                log_msg = f"Removing file from disk: {background}"
                LOG.info(log_msg)
                os.remove(background)

        for fastq in synthetic_fastqs:
            log_msg = f"Created {fastq}"
            LOG.info(log_msg)

        return synthetic_fastqs
