"""
    Tests for build_variant.py
"""

import pytest

from mutacc.builds.build_variant import get_variants, Variant, INFOParser

VARIANT_FIELDS = [
    "variant_type",
    "variant_subtype",
    "alt",
    "ref",
    "chrom",
    "start",
    "end",
    "vcf_entry",
    "reads_region",
    "display_name",
    "samples",
    "padding",
    "genes",
    "RankScore",
]


def test_get_variants(vcf_parser):
    """
        Test get_variants
    """

    count = 0
    for variant in get_variants(
        "tests/fixtures/vcf_test.vcf", padding=100, vcf_parse=vcf_parser["import"]
    ):
        count += 1
        assert isinstance(variant, Variant)

    assert count == 7


def test_variant_with_parser(vcf_parser):
    """
        Test Variant with info parser
    """

    # Try with parser
    for variant in get_variants(
        "tests/fixtures/vcf_test.vcf", padding=1000, vcf_parse=vcf_parser["import"]
    ):

        assert set(variant.keys()) == set(VARIANT_FIELDS)


def test_variant_without_parser():
    """
        Test variant without info parser
    """
    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=300):

        assert set(variant.keys()) == set(VARIANT_FIELDS) - {"genes", "RankScore"}
