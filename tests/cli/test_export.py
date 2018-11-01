import pytest

from click.testing import CliRunner

from mutacc.cli.root import cli

def test_export():

    runner = CliRunner()
    result = runner.invoke(cli, [
            'export',
            '--help'
        ]
    )

    assert result.exit_code == 0
