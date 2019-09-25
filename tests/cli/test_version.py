"""
    Test export command
"""

from unittest.mock import patch

from click.testing import CliRunner

from mutacc.cli.root import cli

@patch('mutacc.cli.database.mongo_adapter.get_client')
@patch('mutacc.cli.database.MutaccAdapter')
@patch('mutacc.builds.build_version.get_md5')
def test_export(mock_md5, mock_mutacc_adapter, mock_get_client, mock_adapter, dataset_dir, tmpdir):

    """
        Test export command
    """

    mock_mutacc_adapter.return_value = mock_adapter
    mock_md5.return_value = 'md5hash'
    root_dir = str(tmpdir.mkdir("mutacc_root_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
        '--root-dir', root_dir,
        'db',
        'version',
        '-d', dataset_dir,
        '-c', 'comment',
        '-m'
        ])

    assert result.exit_code == 0

    
