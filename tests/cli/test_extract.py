import pytest
from pathlib import Path

from click.testing import CliRunner
import mongomock

from mutacc.cli.root import cli


CASE_PATH = "tests/fixtures/case.yaml"
CONFIG_PATH = "tests/fixtures/config.yaml"

def test_extract(tmpdir):

    root_dir = str(tmpdir.mkdir("mutacc_root_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
            '--root-dir', root_dir,
            'extract',
            '--padding', '1500',
            '--case', CASE_PATH
        ]
    )

    assert result.exit_code == 0

    for i in [1,2,3]:

        assert Path(root_dir).joinpath(
            "reads/12345/{}/mutacc_reduced_ref_4_1000000_10002000.bam".format(
                    i
                )
            ).exists()

        assert Path(root_dir).joinpath(
            "reads/12345/{}/mutacc_reduced_ref_4_1000000_10002000_R1.fastq.gz".format(
                    i
                )
            ).exists()

        assert Path(root_dir).joinpath(
            "reads/12345/{}/mutacc_reduced_ref_4_1000000_10002000_R2.fastq.gz".format(
                    i
                )
            ).exists()
