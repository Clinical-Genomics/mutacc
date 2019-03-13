import pytest

from click.testing import CliRunner

from mutacc.cli.root import cli

def test_export(tmpdir):

    root_dir = str(tmpdir.mkdir("mutacc_root_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
            '--root-dir', root_dir,
            'db',
            'export',
            '--help'
        ]
    )

    assert result.exit_code == 0
