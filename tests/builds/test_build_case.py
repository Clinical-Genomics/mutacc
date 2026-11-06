"""
    Tests for build_case.py
"""

from pathlib import Path

from mutacc.builds.build_case import Case
from mutacc.parse.yaml_parse import yaml_parse

CASE = yaml_parse("tests/fixtures/case.yaml")
CASE_FASTQ = yaml_parse("tests/fixtures/case_fastq.yaml")


def test_case(tmpdir, vcf_parser):

    """
        Test Case class
    """

    tmp_dir = Path(tmpdir.mkdir("build_case_test"))
    case = Case(
        input_case=CASE, read_dir=tmp_dir, padding=100, sv_padding=300, vcf_parse=vcf_parser["import"]
    )

    for sample in case["samples"]:

        for fastq_file in sample["variant_fastq_files"]:

            assert Path(fastq_file).exists()

    case = Case(
        input_case=CASE_FASTQ,
        read_dir=tmp_dir,
        padding=100,
        sv_padding=300,
        vcf_parse=vcf_parser["import"],
    )

    for sample in case["samples"]:

        for fastq_file in sample["variant_fastq_files"]:

            assert Path(fastq_file).exists()


def test_case_reference_from_case_yaml(tmpdir, monkeypatch):
    """The reference in the case yaml is given to the samples"""

    import mutacc.builds.build_case as build_case_module

    given = []

    def fake_get_samples(**kwargs):
        given.append(kwargs["reference"])
        return []

    monkeypatch.setattr(build_case_module, "get_samples", fake_get_samples)
    monkeypatch.setattr(build_case_module, "get_variants", lambda **kwargs: [])

    case_dict = {"case": {"case_id": "12345", "reference": "ref.fa"}, "samples": [], "variants": ""}
    read_dir = Path(tmpdir.mkdir("reads"))

    build_case_module.Case(case_dict, read_dir)
    case_dict["case"].pop("reference")
    build_case_module.Case(case_dict, read_dir)

    assert given == ["ref.fa", None]
