import pytest

import pysam

from pathlib import Path

from mutacc.utils.bam_handler import get_overlaping_reads, BAMContext

def test_get_overlaping_reads(read_ids_fixed):

    read_ids = get_overlaping_reads(
        "tests/fixtures/reduced_ref_4_1000000_10002000.bam",
        chrom = "4",
        start = 1000000,
        end = 10002000
    )

    assert isinstance(read_ids, set)
    assert len(read_ids) == len(read_ids_fixed)
    assert read_ids == read_ids_fixed

def test_BAMContext(tmpdir, read_ids_fixed):

    with BAMContext(
        bam_file = "tests/fixtures/reduced_ref_4_1000000_10002000.bam",
        out_dir = Path(tmpdir.mkdir("bam_test"))
        ) as bam_handle:

        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000
        )

        assert bam_handle.out_name.exists()

        assert len(bam_handle.found_reads) + \
               len(bam_handle.reads) == \
               len(read_ids_fixed)

        temp_names = bam_handle.make_names_temp()

        assert Path(temp_names).exists()

    assert not Path(temp_names).exists()
