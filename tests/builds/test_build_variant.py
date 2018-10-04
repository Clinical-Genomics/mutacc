import pytest

from mutacc.builds.build_variant import get_variants, Variant

VARIANT_FIELDS = ["variant_type",
                   "alt",
                   "ref",
                   "chrom",
                   "start",
                   "end",
                   "vcf_entry",
                   "reads_region"]

def test_get_variants():
    
    count = 0
    for variant in get_variants("tests/fixtures/vcf_test.vcf"):
        count += 1
        assert isinstance(variant, Variant)
    
    assert count == 9

def test_Variant():
    
    for variant in get_variants("tests/fixtures/vcf_test.vcf"):

        variant.find_region(padding = 1000)
        variant.build_variant_object()

        assert set(variant.variant_object.keys()) == set(VARIANT_FIELDS)


