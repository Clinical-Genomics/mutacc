"""
    Tests for build_case.py
"""

from pathlib import Path

from mutacc.builds.build_case import Case
from mutacc.parse.yaml_parse import yaml_parse
from mutacc.resources import path_vcf_info_def

CASE = yaml_parse("tests/fixtures/case.yaml")
CASE_FASTQ = yaml_parse("tests/fixtures/case_fastq.yaml")

def test_case(tmpdir):

    """
        Test Case class
    """

    tmp_dir = Path(tmpdir.mkdir("build_case_test"))
    case = Case(input_case=CASE,
                read_dir=tmp_dir,
                padding=100,
                vcf_parse=path_vcf_info_def)


    for sample in case['samples']:

        for fastq_file in sample["variant_fastq_files"]:

            assert Path(fastq_file).exists()

    case = Case(input_case=CASE_FASTQ,
                read_dir=tmp_dir,
                padding=100,
                vcf_parse=path_vcf_info_def)

    for sample in case['samples']:

        for fastq_file in sample["variant_fastq_files"]:

            assert Path(fastq_file).exists()
