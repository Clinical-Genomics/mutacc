import logging
from bson.objectid import ObjectId

from mutacc.utils.fastq_handler import fastq_extract
from mutacc.utils.bam_handler import (get_overlaping_reads, BAMContext, check_bam, get_real_padding, get_length)
from mutacc.builds.build_variant import get_variants

from mutacc.parse.path_parse import make_dir, parse_path

from mutacc.subprocessing.bam_to_fastq import bam_to_fastq

from mutacc.utils.constants import PADDING

LOG = logging.getLogger(__name__)

class CompleteCase:
    """
        Class with methods for handling case objects
    """
    def __init__(self, case):

        """
            Object is instantiated with a case, a dictionary giving all relevant information about
            the case.

            Args:

                case(dict): dictionary containing information about the variant, with three fields;
                            case, samples, and variants.
        """

        self.case = case["case"]
        self.variants = case["variants"]
        self.samples = case["samples"]

        self.sample_ids = [sample["sample_id"] for sample in self.samples]
        self.case_id = self.case["case_id"]

    def get_variants(self, padding = None):
        """
            Method that parses the vcf in the case dictionary.

            Args:

                padding(int): given in bp, extends the region for where to look for reads in the
                alignment file.
        """
        self.variants_object = [] # List to hold variant objects
        self.variants_id = [] # List to hold variant _id

        # Get padding
        padding = padding or PADDING

        for variant in get_variants(self.variants):

            # Finds the read region in the alignment file, and makes a variant object
            variant.find_region(padding=padding)
            variant.build_variant_object()
            variant_object = variant.variant_object

            variant_object["padding"] = padding # Add what padding is used in variant object

            self.variants_object.append(variant_object) # Append the variant object to the list

    def get_samples(self, read_dir, padding=None, picard_exe=None):
        """
            Method makes a list of sample objects, ready to load into a mongodb. This includes
            looking for the raw reads responsible for the variants in the vcf for each sample,
            write them to fastq files, and add the path to these files in the sample object.

            Args:

                read_dir(pathlib.Path): Path to directory where the new fastq files are to be
                stored.
        """
        out_dir = make_dir(read_dir.joinpath(self.case_id))
        self.samples_object = []
        for sample_object in self.samples:


            bam_file = sample_object["bam_file"] #Get bam file fro sample
            bam_file = parse_path(bam_file)

            # Get read length and calculate the wanted padding
            read_length = get_length(bam_file)
            real_padding = get_real_padding(read_length, padding=padding)

            sample_dir = make_dir(
                out_dir.joinpath(sample_object['sample_id'])
                )

            # Check if reads are paired
            paired = check_bam(bam_file)

            # If fastq files are given, the reads will be extracted from these.
            if sample_object.get("fastq_files"):

                read_ids = set() #Holds the read_ids from the bam file

                # For each variant, the reads spanning this genomic region in
                # the bam file are found
                for variant in self.variants_object:

                    overlapping = get_overlaping_reads(
                        start=variant["start"] - real_padding,
                        end=variant["end"] + real_padding,
                        chrom=variant["chrom"],
                        fileName=bam_file
                    )

                    read_ids = read_ids.union(overlapping)

                LOG.info("{} reads found for sample {}".format(
                    len(read_ids),
                    sample_object['sample_id']
                    )
                )

                # Given the read_ids, and the fastq files, the reads are
                # extracted from the fastq files
                LOG.info("Search in fastq file")


                variant_fastq_files = fastq_extract(
                    sample_object["fastq_files"],
                    read_ids,
                    dir_path = sample_dir
                    )

                # Add path to fastq files with the reads containing the variant
                # to the sample object
                sample_object["variant_fastq_files"] = variant_fastq_files
                sample_object["paired_reads"] = paired

            # If the fastq files is not given as input, the reads will be
            # extracted from the bam instead.
            else:

                with BAMContext(bam_file, out_dir=sample_dir, paired=paired) as bam_handle:

                    for variant in self.variants_object:

                        bam_handle.find_reads_from_region(
                            chrom=variant["chrom"],
                            start=variant["start"] - real_padding,
                            end=variant["end"] + real_padding
                        )

                    LOG.info("{} reads found for sample {}".format(
                        bam_handle.record_number,
                        sample_object['sample_id']
                        )
                    )

                    variant_bam_file = bam_handle.out_file

                    sample_object["variant_bam_file"] = variant_bam_file

                    file_name = parse_path(variant_bam_file).name

                # Convert bam to fastq
                fastq1 = str(sample_dir.joinpath(file_name.split('.')[0] + '_R1.fastq.gz'))
                fastq2=None
                if paired:
                    fastq2 = str(sample_dir.joinpath(file_name.split('.')[0] + '_R2.fastq.gz'))

                # Use picard SamToFastq to convert from bam to paired end fastqs

                bam_to_fastq(
                    variant_bam_file,
                    fastq1,
                    fastq2,
                    picard_exe=picard_exe
                    )

                sample_object["variant_fastq_files"] = [fastq1, fastq2]
                sample_object["paired_reads"] = paired
            # Append sample object to list of samples
            self.samples_object.append(sample_object)


    def get_case(self):

        """
            Completes the case object to be uploaded in mongodb
        """
        self.case_object = self.case
