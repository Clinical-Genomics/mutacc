import pytest
import pysam
from pathlib import Path
from mutacc.utils.bam_handler import BAMContext


def test_BAMContext(tmpdir, bam_path):

    with BAMContext(
        bam_file = bam_path,
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


def test_BAMContext_find_names(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region
        bam_handle.find_names_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000
        )

    #THEN the set of read names found should correspond to the the above read names
        assert set(read_ids_fixed) == bam_handle.found_reads


def test_BAMContext_find_reads_by_proximity(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region using the brute flag
        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000,
            brute = True
        )

    #THEN the set of read names found should correspond to the the above read names
        assert bam_handle.found_reads.issubset(set(read_ids_fixed))


def test_BAMContext_find_reads_without_mates(read_ids_fixed, bam_path):

    # GIVEN a list of reads names that are in the bam-file
    with BAMContext(
        bam_file = bam_path,
        ) as bam_handle:

    # WHEN extracting the reads names from region
        bam_handle.find_reads_from_region(
            chrom = "4",
            start = 1000000,
            end = 10002000,
            find_mates=False
        )

    #THEN the set of read names found should correspond to the the above read names
        assert bam_handle.found_reads.issubset(set(read_ids_fixed))
