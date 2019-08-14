"""
    Test export command
"""

from unittest.mock import patch

from click.testing import CliRunner

from mutacc.cli.root import cli

@patch('mutacc.cli.database.mongo_adapter.get_client')
@patch('mutacc.cli.database.MutaccAdapter')
def test_export(mock_mutacc_adapter, mock_get_client, mock_adapter, tmpdir):

    """
        Test export command
    """

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
        ])

    assert result.exit_code == 0
