"""
    Tests for build_dataset.py
"""

from pathlib import Path

from mutacc.mutaccDB.query import mutacc_query
from mutacc.builds.build_dataset import Dataset


BAM = "tests/fixtures/reduced_ref_4_1000000_10002000.bam"
FASTQ1 = "tests/fixtures/fastq1.fastq"
FASTQ2 = "tests/fixtures/fastq2.fastq"
def test_makeset(mock_real_adapter, tmpdir):

    """
        Test building dataset
    """

    samples, _, variants = mutacc_query(
        mock_real_adapter,
        case_query={},
        variant_query=None
        )

    background = {"bam_file": BAM,
                  "fastq_files": [FASTQ1, FASTQ2]}

    temp_dir = Path(str(tmpdir.mkdir("export_tmp_test")))

    out_dir = Path(str(tmpdir.mkdir("export_out_test")))

    dataset = Dataset(samples=samples,
                      variants=variants,
                      tmp_dir=temp_dir,
                      background=background,
                      member='affected',
                      out_dir=out_dir)

    synthetics = dataset.synthetic_fastqs
    for synthetic in synthetics:
        assert Path(synthetic).exists()
