import pytest
from pathlib import Path

from click.testing import CliRunner
import mongomock

from mutacc.cli.root import cli


CASE_PATH = "tests/fixtures/case.yaml"
CONFIG_PATH = "tests/fixtures/config.yaml"

def test_extract(tmpdir):

    mutacc_dir = str(tmpdir.mkdir("mutacc_reads_test"))
    case_dir = str(tmpdir.mkdir("mutacc_cases_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
            'extract',
            '--mutacc-dir', mutacc_dir,
            '--out-dir', case_dir,
            '--padding', '1500',
            '--case', CASE_PATH
        ]
    )

    assert result.exit_code == 0

    for i in [1,2,3]:

        assert Path(mutacc_dir).joinpath(
            "12345/{}/mutacc_reduced_ref_4_1000000_10002000.bam".format(
                    i
                )
            ).exists()

        assert Path(mutacc_dir).joinpath(
            "12345/{}/mutacc_reduced_ref_4_1000000_10002000_R1.fastq.gz".format(
                    i
                )
            ).exists()

        assert Path(mutacc_dir).joinpath(
            "12345/{}/mutacc_reduced_ref_4_1000000_10002000_R2.fastq.gz".format(
                    i
                )
            ).exists()

    #Test with config file
    runner = CliRunner()
    result = runner.invoke(cli, [
            '--config-file', CONFIG_PATH,
            'extract',
            '--mutacc-dir', mutacc_dir,
            '--out-dir', case_dir,
            '--padding', '1500',
            '--case', CASE_PATH
        ]
    )

    assert result.exit_code == 0
