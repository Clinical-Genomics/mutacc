import pytest
from pathlib import Path

from mutacc.utils.vcf_writer import vcf_writer, HEADER, write_info_header, write_contigs

VARIANT1 = {
    "vcf_entry": "4\t65071643\t.\tT\t<INV>\t100\tPASS\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "end": 6,
    "chrom": "7",
    "genotype": {"GT": "1/0"},
    "variant_type": "snp",
    "_id": "456",
    "case": "1111",
}
VARIANT2 = {
    "vcf_entry": "6\t75071643\t.\tT\t<DUP>\t100\tPASS\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "end": 123,
    "chrom": "X",
    "genotype": {"GT": "1/1", "DP": 30},
    "variant_type": "BND",
    "_id": "123",
    "case": "1111",
}
VARIANTS = [VARIANT1, VARIANT2]


def test_vcf_writer(tmpdir, mock_real_adapter):

    # GIVEN a file path and an adapter
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_vcf_father.vcf")

    # WHEN writing vcf-file
    vcf_writer(VARIANTS, out_vcf, "father", mock_real_adapter)

    # THEN all variants should have been written to the file
    with open(out_vcf, "r") as handle:

        count = 0
        for line in handle:
            if not line.startswith("#"):
                count += 1

        assert count == len(VARIANTS)


def test_vcf_write_with_spec(tmpdir, mock_real_adapter, vcf_parser):

    # GIVEN a file path, an adapter and a dictionary specifying what
    # should be passed to the INFO column from the database
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_vcf_father.vcf")

    # WHEN writing the vcf file
    vcf_writer(
        VARIANTS, out_vcf, "father", mock_real_adapter, vcf_parser=vcf_parser["export"]
    )

    # THEN all variants should be written to the file
    with open(out_vcf, "r") as handle:

        count = 0
        for line in handle:
            if not line.startswith("#"):
                count += 1

        assert count == len(VARIANTS)


def test_write_info_header(tmpdir, vcf_parser):

    # GIVEN a file path and a dictionary specifying what should be passed to
    # the vcf-file from the database
    info_spec = vcf_parser["export"]

    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_write_info_header.vcf")

    # WHEN writing the vcf header
    with open(out_vcf, "w") as vcf_handle:
        write_info_header(info_spec, vcf_handle)

    # THEN all lines should start with '##INFO=<ID'
    with open(out_vcf, "r") as vcf_handle:
        for line in vcf_handle:
            assert line.startswith("##INFO=<ID")


def test_write_contigs(tmpdir):

    # GIVEN a file path and a list of variants
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_write_contigs.vcf")

    # WHEN writing the contigs in the header
    with open(out_vcf, "w") as vcf_handle:
        write_contigs(VARIANTS, vcf_handle)

    # THEN all lines should start with '##contig=<ID='
    with open(out_vcf, "r") as vcf_handle:
        for line in vcf_handle:
            assert line.startswith("##contig=<ID=")
