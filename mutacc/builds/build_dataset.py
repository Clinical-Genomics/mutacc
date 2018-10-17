import logging
import tempfile
import subprocess
import os

from mutacc.utils.bam_handler import BAMContext

from mutacc.parse.path_parse import make_dir, parse_path

LOG = logging.getLogger(__name__)

class MakeSet():

    """
        class with methods for constructing a synthetic bam file, enriched with
        variants from the mutacc DB.
    """

    def __init__(self, cases, variants, regions):
        """
            Args:
                cases (list): list of cases
                variants (list): list of variants
                regions (list): list of regions
        """
        self.cases = cases
        self.variants = variants
        self.regions = regions


    def exclude_from_background(self, out_dir, backgrounds = None):

        """
            for each background bam file given (e.g. 3 in a trio) exclude the
            reads overlapping with any region in self.regions by finding the
            names of the reads, and writing a new bam excluding these reads.

            Args:
                out_dir (str): path to directory where bam file is written
                backgrounds (list): list of paths to the 'background' bam files
        """
        #Multiprocess in future?
        for background in backgrounds:

            bam_file = parse_path(background["bam_file"])

            with BAMContext(bam_file = bam_file) as bam_handle:
                #for each region, find the reads overlapping
                for region in self.regions:

                    bam_handle.find_reads_from_region(**region)

                LOG.info("{} reads to be excluded from {}".format(
                        bam_handle.record_number,
                        str(background)
                    )
                )

                #Create excluded bam_file and add to background dictionaries
                background_file = bam_handle.dump_to_exclude_file(out_dir)
                background["excluded_bam"] = background_file

        #orgainize the background files ackording their pedigree
        self.backgrounds = organize_samples(backgrounds)

    def merge_files(self, out_dir, threads = None):
        """
            Merge the background files with the bam files containing
            the variants.

            Args:
                out_dir (str): out_dir (str): path to directory where merged
                bam file is written
                threads (int or None): Number of threads to use for
                samtools merge
        """
        #list to hold the paths of the synthetic datasets
        synthetics = []
        out_dir = parse_path(out_dir, file_type = "dir")

        #for father, mother, and child key in self.backgrounds
        for key in self.backgrounds.keys():
            # store the command in merge_cmd
            merge_cmd = ["samtools", "merge"]

            if threads:
                merge_cmd.append("-@")
                merge_cmd.append(str(threads))

            file_name = parse_path(self.backgrounds[key]["bam_file"]).name
            out_path = out_dir.joinpath("synthetic_"+key+"_"+file_name)

            #Append path to output file for samtools merge
            merge_cmd.append(str(out_path))
            #Append path to background bam
            merge_cmd.append(self.backgrounds[key]["excluded_bam"])

            #Find the bam files in the cases holding the variants
            for case in self.cases:
                #Organize sample objects ackording to pedigree (father, mother, child)
                samples = organize_samples(case["samples"])
                #for the variant bam file with the same key (father, mother, child)
                #append it to the command samtools merge
                merge_cmd.append(samples[key]["variant_bam_file"])

            LOG.info("Merging Files")
            #Make subprocess for command
            subprocess.call(merge_cmd)
            #append the path to synthetic dataset to synthetics
            synthetics.append(out_path)

        #Remove the 'backround' bam files from disk
        for key in self.backgrounds.keys():
            try:
                os.remove(self.backgrounds[key]["excluded_bam"])
            except FileNotFoundError:
                LOG.warning("file {} does not exist".format(
                    self.backgrounds[key]["excluded_bam"])
                    )
        #Return list holding paths to synthetic datasets
        return synthetics


def organize_samples(samples):
    """
        Organizes list of samples in a correct pedigree structure.
    """
    if len(samples) == 1:
        return samples

    sample_ids = set(sample["sample_id"] for sample in samples)

    #Find child
    for sample in samples:

        if sample["mother"] in sample_ids \
        and sample["father"] in sample_ids:

            child = sample
            break
    try:
        child
    except NameError:
        LOG.warning("invalid pedigree")
        raise NameError

    #Find parents
    for sample in samples:

        if sample["sample_id"] == child["father"]:
            father = sample
        elif sample["sample_id"] == child["mother"]:
            mother = sample

    try:
        father
        mother
    except NameError:
        LOG.warning("invalid pedigree")
        raise NameError

    organized_samples = {"father": father,
                         "mother": mother,
                         "child": child}

    return organized_samples
