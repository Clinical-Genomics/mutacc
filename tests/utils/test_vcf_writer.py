import pytest
from pathlib import Path

from mutacc.utils.vcf_writer import vcf_writer

VARIANT1 = {
    "vcf_entry": "4\t65071643\t.\tT\t<INV>\t100\tPASS\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "genotype": "1/0",
    "_id": "456"
}
VARIANT2 = {
    "vcf_entry": "6\t75071643\t.\tT\t<DUP>\t100\tPASS\tSOMATIC;SVTYPE=INV\tGT\t./.",
    "genotype": "1/0",
    "_id": "123"
}
VARIANTS = [VARIANT1, VARIANT2]


def test_vcf_writer(tmpdir):

    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_vcf_father.vcf")

    vcf_writer(VARIANTS, out_vcf, "father")

    with open(out_vcf, "r") as handle:

        count = 0
        for line in handle:
            if count == 0:
                assert line.startswith("##")
            elif count == 1:
                assert line.startswith("#")
                assert len(line.split("\t")) == 10
            else:
                assert len(line.split("\t")) == 10
            count += 1

        assert count == 4
