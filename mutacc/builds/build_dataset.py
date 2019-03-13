import logging
import tempfile
import subprocess
import os

from mutacc.utils.bam_handler import BAMContext

from mutacc.subprocessing.exclude_from_fastq import exclude_from_fastq
from mutacc.subprocessing.merge_fastqs import merge_fastqs as merge_fastqs_sub

from mutacc.parse.path_parse import make_dir, parse_path

LOG = logging.getLogger(__name__)

class MakeSet():

    """
        class with methods for constructing a synthetic bam file, enriched with
        variants from the mutacc DB.
    """

    def __init__(self, samples, regions):
        """
            Args:
                samples (mutacc.utils.pedigree.Individual): list of samples. sample
                    is parsed with the Individual class
                regions (list(dict)): list of regions. Each region is
                    represented as a dictionary with keys 'chrom', 'start', 'end'
        """
        self.samples = samples
        self.regions = regions

    def exclude_from_background(self, tmp_dir, background, member):

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

        bam_file = parse_path(background["bam_file"])
        fastq_files = [parse_path(fastq) for fastq in background["fastq_files"]]

        with BAMContext(bam_file = bam_file) as bam_handle:
            #for each region, find the reads overlapping
            for region in self.regions:

                bam_handle.find_read_names_from_region(**region)

            LOG.info("{} reads to be excluded from {}".format(
                    bam_handle.record_number,
                    fastq_files
                )
            )

            name_file = bam_handle.make_names_temp(tmp_dir)
            self.excluded_backgrounds = []
            for fastq_file in fastq_files:

                fastq_path = str(fastq_file)
                out_name = str(member) + "_" + str(fastq_file.name)
                out_path = str(tmp_dir.joinpath(out_name))

                #Here command line tool seqkit grep is used
                exclude_from_fastq(name_file, out_path, fastq_path)

                self.excluded_backgrounds.append(out_path)



    def merge_fastqs(self, out_dir, save_background = True):
        """
            Merge the background file with the fastq_files Holding
            the reads supporting the variants
        """
        synthetic_fastqs = []

        out_dir = parse_path(out_dir, file_type = 'dir')

        #For each fastq file given as background (two if paired end)
        for i in range(len(self.excluded_backgrounds)):

            #Simply use 'cat' command to merge files

            fastq_list = [self.excluded_backgrounds[i]]

            for sample in self.samples:

                fastq_list.append(sample.variant_fastq_files[i])

            file_name = parse_path(self.excluded_backgrounds[i]).name
            out_path = out_dir.joinpath("synthetic_"+file_name)

            LOG.info("Merging fastq files")

            try:
                 merge_fastqs_sub(fastq_list, out_path)

            except:
                LOG.critical(
                        "Files were not merged, background files in {} not removed".format(
                            str(out_dir)
                    )
                )

                raise

            synthetic_fastqs.append(out_path)

        #Remove background fastqs
        if not save_background:
            for background in self.excluded_backgrounds:
                LOG.info("Removing file from disk: {}".format(background))
                os.remove(background)

        for fastq in synthetic_fastqs:
            LOG.info("Created {}".format(fastq))

        return synthetic_fastqs
