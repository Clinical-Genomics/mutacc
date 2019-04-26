"""
    Tests for build_variant.py
"""
from mutacc.builds.build_variant import get_variants, Variant

VARIANT_FIELDS = ["variant_type",
                  "alt",
                  "ref",
                  "chrom",
                  "start",
                  "end",
                  "vcf_entry",
                  "reads_region",
                  "display_name",
                  "samples",
                  "padding"]

def test_get_variants():
    """
        Test get_variants
    """

    count = 0
    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=100):
        count += 1
        assert isinstance(variant, Variant)

    assert count == 7


def test_variant():
    """
        Test Variant
    """

    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=1000):

        assert set(variant.keys()) == set(VARIANT_FIELDS)
