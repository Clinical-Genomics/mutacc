"""
    Fixtures for unittests
"""

from pathlib import Path
import random
import pytest

from pysam import AlignmentFile
import mongomock
import yaml

from mutacc.utils.pedigree import Individual
from mutacc.mutaccDB.db_adapter import MutaccAdapter
from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import Case
from mutacc.mutaccDB.insert import insert_entire_case
from mutacc.resources import path_vcf_info_def
from .random_case import random_trio

DATASET_DIR = "tests/fixtures/dataset/"
PED_PATH = "tests/fixtures/dataset/dataset.ped"
CONFIG_PATH = "tests/fixtures/config.yaml"


@pytest.fixture
def read_ids_fixed():
    """
        IDs for reads in bam file
    """

    sam = AlignmentFile("tests/fixtures/reduced_ref_4_1000000_10002000.bam", "rb")

    ids = set([read.query_name for read in sam])

    sam.close()

    return ids


@pytest.fixture
def individuals_fixed():
    """
        Generate random individuals
    """

    bam = "/path/to/bam"
    fastqs = ["/path/to/fastq1", "/path/to/fastq2"]

    child = Individual(
        ind="child",
        family="family",
        mother="mother",
        father="father",
        sex="1",
        phenotype="2",
        variant_bam_file=bam,
        variant_fastq_files=fastqs,
    )

    father = Individual(
        ind="father",
        family="family",
        mother="0",
        father="0",
        sex="1",
        phenotype="1",
        variant_bam_file=bam,
        variant_fastq_files=fastqs,
    )

    mother = Individual(
        ind="mother",
        family="family",
        mother="0",
        father="0",
        sex="2",
        phenotype="2",
        variant_bam_file=bam,
        variant_fastq_files=fastqs,
    )

    return [child, father, mother]


CASE_YAML = "tests/fixtures/case.yaml"
CASES_NO = 5


@pytest.fixture
def mock_adapter():

    """
        Mock pymongo adapter
    """

    client = mongomock.MongoClient(port=27017, host="localhost")
    adapter = MutaccAdapter(client=client, db_name="test")

    random.seed(1)
    for _ in range(CASES_NO):
        case, variant = random_trio()
        variant_id = adapter.add_variants([variant])
        case["variants"] = variant_id
        adapter.add_case(case)

    random.seed(1)
    overlapping_case, overlapping_variant = random_trio()

    overlapping_case["case_id"] = "overlapping"
    overlapping_variant["display_name"] = "overlapping"

    variant_id = adapter.add_variants([overlapping_variant])
    overlapping_case["variants"] = variant_id
    adapter.add_case(overlapping_case)

    return adapter


@pytest.fixture
def mock_real_adapter(tmpdir):

    """
        Mock adapter to populated database
    """

    mutacc_dir = Path(str(tmpdir.mkdir("mutacc_test")))

    client = mongomock.MongoClient(port=27017, host="localhost")
    adapter = MutaccAdapter(client=client, db_name="test")

    case = yaml_parse(CASE_YAML)
    case["case"]["case_id"] = "1111"
    case = Case(
        input_case=case, read_dir=mutacc_dir, padding=200, vcf_parse=path_vcf_info_def
    )

    insert_entire_case(adapter, case)

    return adapter


@pytest.fixture
def config_dict():
    with open(CONFIG_PATH, "r") as in_handle:
        config = yaml.load(in_handle, Loader=yaml.FullLoader)
    return config


@pytest.fixture
def dataset_dir():
    return DATASET_DIR


@pytest.fixture
def ped_path():
    return PED_PATH
