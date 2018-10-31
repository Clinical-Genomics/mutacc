import pytest

import pysam

from mutacc.utils.pedigree import Individual

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
