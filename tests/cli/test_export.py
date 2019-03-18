import pytest

from click.testing import CliRunner
from unittest.mock import patch

from mutacc.cli.root import cli
from mutacc.mutaccDB.db_adapter import MutaccAdapter
import mongo_adapter

@patch('mutacc.cli.database.mongo_adapter.get_client')
@patch('mutacc.cli.database.MutaccAdapter')
def test_export(mock_mutacc_adapter, mock_get_client, mock_adapter, tmpdir):

    mock_mutacc_adapter.return_value = mock_adapter

    root_dir = str(tmpdir.mkdir("mutacc_root_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
            '--root-dir', root_dir,
            'db',
            'export',
            '-c', '{}',
            '-m', 'child',
            '-p',
            '-n', 'test_sample'
        ]
    )

    assert result.exit_code == 0
