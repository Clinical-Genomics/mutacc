import pytest
from pathlib import Path
import random
import string

import pysam
import mongomock

from mutacc.utils.pedigree import Individual
from mutacc.mutaccDB.db_adapter import MutaccAdapter
from mutacc.parse.yaml_parse import yaml_parse
from mutacc.builds.build_case import CompleteCase
from mutacc.mutaccDB.insert import insert_entire_case

from .random_case import random_trio




@pytest.fixture
def read_ids_fixed(request):

    sam = pysam.AlignmentFile("tests/fixtures/reduced_ref_4_1000000_10002000.bam", "rb")

    ids = set([read.query_name for read in sam])

    sam.close()

    return ids

@pytest.fixture
def individuals_fixed(request):

    BAM = "/path/to/bam"
    FASTQS = ["/path/to/fastq1", "/path/to/fastq2"]

    child = Individual(
        ind = "child",
        family = "family",
        mother = "mother",
        father = "father",
        sex = '1',
        phenotype = '2',
        variant_bam_file = BAM,
        variant_fastq_files = FASTQS
    )

    father = Individual(
        ind = "father",
        family = "family",
        mother = "0",
        father = "0",
        sex = '1',
        phenotype = '1',
        variant_bam_file = BAM,
        variant_fastq_files = FASTQS
    )

    mother = Individual(
        ind = "mother",
        family = "family",
        mother = "0",
        father = "0",
        sex = '2',
        phenotype = '2',
        variant_bam_file = BAM,
        variant_fastq_files = FASTQS
    )

    return [child, father, mother]

CASE_YAML = "tests/fixtures/case.yaml"
CASES_NO = 5
@pytest.fixture
def mock_adapter(request):

    client = mongomock.MongoClient(port = 27017, host = 'localhost')
    adapter = MutaccAdapter(client = client, db_name = 'test')

    random.seed(1)
    for i in range(CASES_NO):

        case, variant = random_trio()

        variant_id = adapter.add_variants([variant])

        case['variants'] = variant_id

        adapter.add_case(case)

    random.seed(1)
    overlapping_case, overlapping_variant = random_trio()

    overlapping_case['case_id'] = 'overlapping'
    overlapping_variant['display_name'] = 'overlapping'

    variant_id = adapter.add_variants([overlapping_variant])
    overlapping_case['variants'] = variant_id
    adapter.add_case(overlapping_case)

    return adapter


@pytest.fixture
def mock_real_adapter(request, tmpdir):

    mutacc_dir = Path(str(tmpdir.mkdir("mutacc_test")))

    client = mongomock.MongoClient(port = 27017, host = 'localhost')
    adapter = MutaccAdapter(client = client, db_name = 'test')

    case = yaml_parse(CASE_YAML)
    case["case"]["case_id"] = "1111"
    case = CompleteCase(case)

    case.get_variants(padding = 200)
    case.get_samples(mutacc_dir)
    case.get_case()

    insert_entire_case(adapter, case)

    return adapter
