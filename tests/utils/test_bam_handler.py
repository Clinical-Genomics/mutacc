import pytest

import pysam

from pathlib import Path

from mutacc.utils.bam_handler import BAMContext


def test_BAMContext(tmpdir):

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

        temp_names = bam_handle.make_names_temp(Path(tmpdir.mkdir("names_dir")))

        assert Path(temp_names).exists()


    assert not Path(temp_names).exists()


def test_BAMContext_find_read_names(read_ids_fixed):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = "tests/fixtures/reduced_ref_4_1000000_10002000.bam",
        ) as bam_handle:

    # WHEN extracting the reads names from region
        bam_handle.find_read_names_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000
        )

    #THEN the set of read names found should correspond to the the above read names
        assert set(read_ids_fixed) == bam_handle.found_reads
