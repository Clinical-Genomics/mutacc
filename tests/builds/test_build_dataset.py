import pytest
from pathlib import Path

from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import MakeSet


BAM = "tests/fixtures/reduced_ref_4_1000000_10002000.bam"
FASTQ1 = "tests/fixtures/fastq1.fastq"
FASTQ2 = "tests/fixtures/fastq2.fastq"
def test_MakeSet(mock_adapter, tmpdir):

    samples, regions, variants = mutacc_query(
        mock_adapter,
        case_query = '{}',
        variant_query = None
        )

    make_set = MakeSet(samples, regions)

    background = {"bam_file": BAM,
                  "fastq_files": [FASTQ1, FASTQ2]}

    temp_dir = Path(str(tmpdir.mkdir("export_tmp_test")))
    make_set.exclude_from_background(tmp_dir = temp_dir,
                                     background = background,
                                     member = 'affected')


    #Merge the background files with excluded reads with the bam Files
    #Holding the reads for the regions of the variants to be included in
    #validation set
    out_dir = Path(str(tmpdir.mkdir("export_out_test")))
    synthetics = make_set.merge_fastqs(
        out_dir = out_dir
        )
    for synthetic in synthetics:
        assert Path(synthetic).exists()
