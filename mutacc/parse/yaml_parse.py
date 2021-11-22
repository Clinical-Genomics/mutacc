import yaml
import logging

import ped_parser

from mutacc.parse.path_parse import parse_path

LOG = logging.getLogger(__name__)

SAMPLE = ["sample_id", "sex", "mother", "father", "bam_file"]


class YAMLFieldsError(Exception):
    pass


def yaml_parse(yaml_file):

    yaml_file = parse_path(yaml_file)

    with open(yaml_file, "r") as yaml_handle:

        try:
            yaml_dict = yaml.safe_load(yaml_handle)

        except yaml.YAMLError as exc:
            LOG.critical(f"Error loading yaml object: {exc}")

            raise

    if set(yaml_dict.keys()) != set(["case", "variants", "samples"]):

        raise YAMLFieldsError("Yaml object must contain 'case', 'samples', and 'variants'")

    for sample in yaml_dict["samples"]:

        if not set(SAMPLE).issubset(set(sample.keys())):

            raise YAMLFieldsError(
                "sample object must contain 'sample_id', 'mother', 'father',\
                    'bam', and 'fastq'"
            )

    # Check if valid pedigree with ped_parser classes Family and individual
    family = ped_parser.Family(family_id=yaml_dict["case"]["case_id"])
    for sample in yaml_dict["samples"]:

        if sample["sex"] == "male":
            sex = "1"
        elif sample["sex"] == "female":
            sex = "2"
        else:
            sex = "0"

        if sample["phenotype"] == "unaffected":
            phenotype = "1"
        elif sample["phenotype"] == "affected":
            phenotype = "2"
        else:
            phenotype = "0"

        individual = ped_parser.Individual(
            ind=sample["sample_id"],
            family=yaml_dict["case"]["case_id"],
            mother=str(sample["mother"]),
            father=str(sample["father"]),
            sex=sex,
            phenotype=phenotype,
        )

        family.add_individual(individual)

    try:
        family.family_check()
    except:
        LOG.info("Not valid pedigree")
        raise

    return yaml_dict
