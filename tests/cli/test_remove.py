import pytest

from click.testing import CliRunner

from mutacc.cli.root import cli

def test_remove():

    runner = CliRunner()
    result = runner.invoke(cli, [
            'db',
            'remove',
            '--help'
        ]
    )

    assert result.exit_code == 0
