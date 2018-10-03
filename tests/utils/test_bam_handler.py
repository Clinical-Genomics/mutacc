import pytest

import pysam

from mutacc.utils.bam_handler import get_overlaping_reads

def test_get_overlaping_reads(read_ids_fixed):

    read_ids = get_overlaping_reads("tests/fixtures/reduced_ref_4_1000000_10002000.bam", chrom = "4", start = 1000000, end = 10002000)
    
    assert isinstance(read_ids, set)
    assert len(read_ids) == len(read_ids_fixed) 
    assert read_ids == read_ids_fixed

    
