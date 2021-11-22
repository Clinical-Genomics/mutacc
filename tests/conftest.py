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
from mutacc.resources import default_vcf_parser
from .random_case import random_trio

DATASET_DIR = "tests/fixtures/dataset/"
PED_PATH = "tests/fixtures/dataset/dataset.ped"
CONFIG_PATH = "tests/fixtures/config.yaml"
BAM_PATH = "tests/fixtures/reduced_ref_4_1000000_10002000.bam"


@pytest.fixture
def bam_path():
    return BAM_PATH


@pytest.fixture
def read_ids_fixed(bam_path):
    """
    IDs for reads in bam file
    """

    sam = AlignmentFile(bam_path, "rb")
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
def vcf_parser():
    with open(default_vcf_parser, "r") as handle:
        _vcf_parser = yaml.safe_load(handle)
    return _vcf_parser


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
def mock_real_adapter(tmpdir, vcf_parser):

    """
    Mock adapter to populated database
    """

    mutacc_dir = Path(str(tmpdir.mkdir("mutacc_test")))

    client = mongomock.MongoClient(port=27017, host="localhost")
    adapter = MutaccAdapter(client=client, db_name="test")

    case = yaml_parse(CASE_YAML)
    case["case"]["case_id"] = "1111"
    case = Case(
        input_case=case,
        read_dir=mutacc_dir,
        padding=200,
        sv_padding=1000,
        vcf_parse=vcf_parser["import"],
    )

    insert_entire_case(adapter, case)

    return adapter


@pytest.fixture
def config_dict():
    with open(CONFIG_PATH, "r") as in_handle:
        config = yaml.safe_load(in_handle)
    return config


@pytest.fixture
def dataset_dir():
    return DATASET_DIR


@pytest.fixture
def ped_path():
    return PED_PATH


VARIANT1 = {
    "vcf_entry": "4\t65071643\t.\tT\t<INV>\t100\tPASS\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "end": 6,
    "chrom": "7",
    "genotype": {"GT": "1/0"},
    "variant_type": "snp",
    "_id": "456",
    "case": "1111",
}
VARIANT2 = {
    "vcf_entry": "6\t75071643\t.\tT\t<DUP>\t100\tPloidy\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "end": 123,
    "chrom": "X",
    "genotype": {"GT": "1/1", "DP": 30},
    "variant_type": "BND",
    "_id": "123",
    "case": "1111",
}


@pytest.fixture
def variants():

    return [VARIANT1, VARIANT2]
