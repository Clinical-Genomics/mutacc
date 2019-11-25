"""
    Tests for build_variant.py
"""

import pytest

from mutacc.builds.build_variant import get_variants, Variant, INFOParser
from mutacc.resources import path_vcf_info_def

VARIANT_FIELDS = ["variant_type",
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
                  "RankScore"]

def test_get_variants():
    """
        Test get_variants
    """

    count = 0
    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=100,
                                vcf_parse=path_vcf_info_def):
        count += 1
        assert isinstance(variant, Variant)

    assert count == 7


def test_variant_with_parser():
    """
        Test Variant with info parser
    """

    # Try with parser
    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=1000,
                                vcf_parse=path_vcf_info_def):

        assert set(variant.keys()) == set(VARIANT_FIELDS)


def test_variant_without_parser():
    """
        Test variant without info parser
    """
    for variant in get_variants("tests/fixtures/vcf_test.vcf", padding=300):

        assert set(variant.keys()) == set(VARIANT_FIELDS) - {"genes", "RankScore"}


def test_INFOParser():
    """
        test instatiate INFOparser object
    """
    parser_file = path_vcf_info_def
    parser = INFOParser(parser_info=path_vcf_info_def)
    assert isinstance(parser.parsers, list)


def test_INFOParser_check():
    """
        test _check method giving badly formated parsing information
    """
    parser_info = [{'id': 'test_id', 'multivalue': True},]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info)

    parser_info = [{'id': 'test_id',
                    'multivalue': True,
                    'separator': ',',
                    'format': '1|2',
                    'format_separator': '|',
                    'target': 'target'}]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info)

    parser_info = ['element']
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info)


def test_INFOParser_parse():
    """
        Test parsing mocked variant entries given different parser info
    """
    # test multivalue, array of arrays, eg separated with ',' and then  '|'
    class MockVariant():
        def __init__(self, info_dict):
            self.INFO = info_dict

    info_dict = {'ID1': 'value11|value12,value21|value22'}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [{'id':'ID1',
                    'multivalue': True,
                    'separator': ',',
                    'format': 'value1|value2',
                    'format_separator': '|',
                    'target': ['value1', 'value2'],
                    'out_name': 'parsed_value'}]

    parser = INFOParser(parser_info=parser_info)
    parsed_variant = parser.parse(mock_variant)

    assert parsed_variant['parsed_value'][0]['value1'] == 'value11'
    assert parsed_variant['parsed_value'][0]['value2'] == 'value12'
    assert parsed_variant['parsed_value'][1]['value1'] == 'value21'
    assert parsed_variant['parsed_value'][1]['value2'] == 'value22'

    # Test parsing an ID separated with ':' where we only want one element
    info_dict = {'RankScore': 'case_1: 10'}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [{'id': 'RankScore',
                    'multivalue': False,
                    'format': 'case_id: rank_score',
                    'format_separator': ':',
                    'target': ['rank_score'],
                    'out_name': 'rank_score',
                    'out_type': 'int'}]

    parser = INFOParser(parser_info=parser_info)
    parsed_variant = parser.parse(mock_variant)

    assert isinstance(parsed_variant['rank_score'], int)
    assert parsed_variant['rank_score'] == 10

    # Test parsing simple string
    info_dict = {'TYPE': 'SNV'}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [{'id': 'TYPE',
                    'multivalue': False,
                    'out_name': 'var_type',
                    'out_type': 'str'}]

    parser = INFOParser(parser_info=parser_info)
    parsed_variant = parser.parse(mock_variant)

    assert isinstance(parsed_variant['var_type'], str)
    assert parsed_variant['var_type'] == 'SNV'
