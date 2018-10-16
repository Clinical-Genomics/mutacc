import logging
import tempfile
import subprocess

from mutacc.utils.bam_handler import BAMContext

from mutacc.parse.path_parse import make_dir, parse_path

LOG = logging.getLogger(__name__)

class MakeSet():

    """
        class with methods for constructing a synthetic bam file, enriched with
        variants from the mutacc DB.
    """

    def __init__(self, cases, variants, regions):

        self.cases = cases
        self.variants = variants
        self.regions = regions


    def exclude_from_background(self, out_dir, backgrounds = None):

        #Multiprocess in future?
        for background in backgrounds:

            bam_file = parse_path(background["bam_file"])

            with BAMContext(bam_file = bam_file) as bam_handle:

                for region in self.regions:

                    bam_handle.find_reads_from_region(**region)

                LOG.info("{} reads to be excluded from {}".format(
                        bam_handle.record_number,
                        str(background)
                    )
                )

                #Create excluded bam_file
                background_file = bam_handle.dump_to_exclude_file(out_dir)
                background["excluded_bam"] = background_file

        self.backgrounds = organize_samples(backgrounds)

    def merge_files(self, out_dir):

        for key in self.backgrounds.keys():

            merge_cmd = ["samtools", "merge"]

            file_name = parse_path(self.backgrounds[key]["bam_file"]).name
            out_path = out_dir.joinpath("synthetic_"+"file_name")

            merge_cmd.append(str(out_path))
            merge_cmd.append(self.backgrounds[key]["excluded_bam"])

            for case in self.cases:

                samples = organize_samples(case["samples"])

                merge_cmd.append(samples["key"]["variant_bam_file"])

            LOG.info("Merging Files")
            subprocess.call(merge_cmd)

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
