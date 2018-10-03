import pytest

import pysam

@pytest.fixture
def read_ids_fixed(request):

    sam = pysam.AlignmentFile("tests/fixtures/reduced_ref_4_1000000_10002000.bam", "rb")

    ids = set([read.query_name for read in sam])

    sam.close()

    return ids



