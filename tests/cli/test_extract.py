"""
    Test extract command
"""

from pathlib import Path
import time

from click.testing import CliRunner

from mutacc.cli.root import cli


CASE_PATH = "tests/fixtures/case.yaml"
CONFIG_PATH = "tests/fixtures/config.yaml"

def test_extract(tmpdir):
    """
        test extract command
    """

    root_dir = str(tmpdir.mkdir("mutacc_root_test"))

    runner = CliRunner()
    result = runner.invoke(cli, [
        '--root-dir', root_dir,
        'extract',
        '--padding', '1500',
        '--case', CASE_PATH
        ])

    assert result.exit_code == 0

    date_str = time.strftime('%Y-%m-%d')

    for i in [1, 2, 3]:

        assert Path(root_dir).joinpath(
            "reads/12345/{}/{}/mutacc_reduced_ref_4_1000000_10002000.bam".format(
                date_str,
                i
                )
            ).exists()

        assert Path(root_dir).joinpath(
            "reads/12345/{}/{}/mutacc_reduced_ref_4_1000000_10002000_R1.fastq.gz".format(
                date_str,
                i
                )
            ).exists()

        assert Path(root_dir).joinpath(
            "reads/12345/{}/{}/mutacc_reduced_ref_4_1000000_10002000_R2.fastq.gz".format(
                date_str,
                i
                )
            ).exists()


def test_extract_reference(tmpdir, monkeypatch):
    """
        test that the reference from option and config is given to Case
    """

    import mutacc.cli.extract as extract_module

    given = []

    class FakeCase(dict):
        case_id = "fake"

        def __init__(self, **kwargs):
            super().__init__()
            given.append(kwargs.get("reference"))

    monkeypatch.setattr(extract_module, "Case", FakeCase)

    root_dir = str(tmpdir.mkdir("mutacc_root_ref_test"))
    option_ref = str(tmpdir.join("option.fa"))
    config_ref = str(tmpdir.join("config.fa"))
    for path in (option_ref, config_ref):
        open(path, "w").close()
    config_file = str(tmpdir.join("config.yaml"))
    with open(config_file, "w") as handle:
        handle.write(f"root_dir: {root_dir}\nreference: {config_ref}\n")

    no_ref_config_file = str(tmpdir.join("config_no_reference.yaml"))
    with open(no_ref_config_file, "w") as handle:
        handle.write(f"root_dir: {root_dir}\n")

    runner = CliRunner()
    # WHEN no reference is given anywhere THEN Case gets None
    result = runner.invoke(cli, ["-c", no_ref_config_file, "extract", "--case", CASE_PATH])
    assert result.exit_code == 0, result.output
    # WHEN no option is given THEN the config value is used
    result = runner.invoke(cli, ["-c", config_file, "extract", "--case", CASE_PATH])
    assert result.exit_code == 0, result.output
    # WHEN the option is given THEN it takes precedence
    result = runner.invoke(
        cli, ["-c", config_file, "extract", "--case", CASE_PATH, "--reference", option_ref]
    )
    assert result.exit_code == 0, result.output

    assert given == [None, config_ref, option_ref]
