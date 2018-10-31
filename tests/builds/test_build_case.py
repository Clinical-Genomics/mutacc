import pytest
from pathlib import Path

from mutacc.builds.build_case import CompleteCase

from mutacc.parse.yaml_parse import yaml_parse

CASE = yaml_parse("tests/fixtures/case.yaml")

def test_CompleteCase(tmpdir):

    case = CompleteCase(CASE)

    case.get_variants(padding = 100)
    tmp_dir = Path(tmpdir.mkdir("build_case_test"))

    case.get_samples(tmp_dir)

    for sample in case.samples_object:

        for fastq_file in sample["variant_fastq_files"]:

            assert Path(fastq_file).exists()
