"""
    Tests for vcf_handler.py
"""

import pytest
from pathlib import Path

from mutacc.utils.vcf_handler import (
    INFOParser,
    vcf_writer,
    write_info_header,
    write_contigs,
    write_filter_headers
)


def test_INFOParser(vcf_parser):
    """
        test instatiate INFOparser object
    """
    parser = INFOParser(parser_info=vcf_parser["import"], stream="read")
    assert isinstance(parser.parsers, list)

    parser = INFOParser(parser_info=vcf_parser["export"], stream="write")
    assert isinstance(parser.parsers, list)


def test_INFOParser_check():
    """
        test _check method giving badly formated parsing information
    """
    parser_info = [{"id": "test_id", "multi_value": True}]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info, stream="read")

    parser_info = [
        {
            "id": "test_id",
            "multi_value": True,
            "separator": ",",
            "format": "1|2",
            "format_separator": "|",
            "target": "target",
        }
    ]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info, stream="read")

    parser_info = ["element"]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info, stream="read")


def test_INFOParser_parse_read():
    """
        Test parsing mocked variant entries given different parser info
    """
    # GIVEN a mocked
    class MockVariant:
        def __init__(self, info_dict):
            self.INFO = info_dict

    info_dict = {"ID1": "value11|value12,value21|value22"}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [
        {
            "id": "ID1",
            "multi_value": True,
            "separator": ",",
            "format": "value1|value2",
            "format_separator": "|",
            "target": ["value1", "value2"],
            "out_name": "parsed_value",
        }
    ]

    parser = INFOParser(parser_info=parser_info, stream="read")
    parsed_variant = parser.parse(mock_variant)
    assert parsed_variant["parsed_value"][0]["value1"] == "value11"
    assert parsed_variant["parsed_value"][0]["value2"] == "value12"
    assert parsed_variant["parsed_value"][1]["value1"] == "value21"
    assert parsed_variant["parsed_value"][1]["value2"] == "value22"

    # Test parsing an ID separated with ':' where we only want one element
    info_dict = {"RankScore": "10"}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [
        {
            "id": "RankScore",
            "multi_value": False,
            "out_name": "rank_score",
            "out_type": "int",
        }
    ]

    parser = INFOParser(parser_info=parser_info, stream="read")
    parsed_variant = parser.parse(mock_variant)

    assert isinstance(parsed_variant["rank_score"], int)
    assert parsed_variant["rank_score"] == 10

    # Test parsing simple string
    info_dict = {"TYPE": "SNV"}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [
        {"id": "TYPE", "multi_value": False, "out_name": "var_type", "out_type": "str"}
    ]

    parser = INFOParser(parser_info=parser_info, stream="read")
    parsed_variant = parser.parse(mock_variant)

    assert isinstance(parsed_variant["var_type"], str)
    assert parsed_variant["var_type"] == "SNV"


def test_INFOParser_parse_write_list():
    "Testing to write INFO entry by parsing a dictionary"

    parser_info = [
        {
            "id": "ID1",
            "format_separator": "|",
            "target": ["value1", "value2"],
            "out_name": "parsed_value",
        }
    ]

    parser = INFOParser(parser_info=parser_info, stream="write")
    variant_dict = {"ID1": [1, 2.0, "3"]}
    parsed_variant = parser.parse(variant_dict)
    assert parsed_variant == "parsed_value=1,2.0,3"


def test_INFOParser_parse_write_list_of_dict():
    "Testing to write INFO entry by parsing a dictionary"

    parser_info = [
        {
            "id": "ID1",
            "format_separator": "|",
            "target": ["value1", "value2"],
            "out_name": "parsed_value",
        }
    ]

    parser = INFOParser(parser_info=parser_info, stream="write")
    variant_dict = {
        "ID1": [
            {"value1": 1, "value2": "2", "value3": 3},
            {"value1": 4, "value2": 5, "value3": 6},
        ]
    }
    parsed_variant = parser.parse(variant_dict)
    assert parsed_variant == "parsed_value=1|2,4|5"

    parser_info[0].pop("target")
    parser = INFOParser(parser_info=parser_info, stream="write")
    variant_dict = {
        "ID1": [
            {"value1": 1, "value2": "2", "value3": 3},
            {"value1": 4, "value2": 5, "value3": 6},
        ]
    }
    parsed_variant = parser.parse(variant_dict)
    assert parsed_variant == "parsed_value=1|2|3,4|5|6"


def test_vcf_writer(tmpdir, mock_real_adapter, variants):

    # GIVEN a file path and an adapter
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_vcf_father.vcf")

    # WHEN writing vcf-file
    vcf_writer(variants, out_vcf, "father", mock_real_adapter)

    # THEN all variants should have been written to the file
    with open(out_vcf, "r") as handle:

        count = 0
        for line in handle:
            if not line.startswith("#"):
                count += 1

        assert count == len(variants)


def test_vcf_write_with_spec(tmpdir, mock_real_adapter, vcf_parser, variants):

    # GIVEN a file path, an adapter and a dictionary specifying what
    # should be passed to the INFO column from the database
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_vcf_father.vcf")

    # WHEN writing the vcf file
    vcf_writer(
        variants, out_vcf, "father", mock_real_adapter, vcf_parser=vcf_parser["export"]
    )

    # THEN all variants should be written to the file
    with open(out_vcf, "r") as handle:

        count = 0
        for line in handle:
            if not line.startswith("#"):
                count += 1

        assert count == len(variants)


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


def test_write_contigs(tmpdir, variants):

    # GIVEN a file path and a list of variants
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_write_contigs.vcf")

    # WHEN writing the contigs in the header
    with open(out_vcf, "w") as vcf_handle:
        write_contigs(variants, vcf_handle)

    # THEN all lines should start with '##contig=<ID='
    with open(out_vcf, "r") as vcf_handle:
        for line in vcf_handle:
            assert line.startswith("##contig=<ID=")


def test_write_filter_headers(tmpdir, variants):

    # GIVEN a file path and a list of variants
    out_path = Path(tmpdir.mkdir("test_vcf_writer"))
    out_vcf = out_path.joinpath("test_write_filters.vcf")

    # WHEN writing the filters in the header
    with open(out_vcf, "w") as vcf_handle:
        write_filter_headers(variants, vcf_handle)

    # THEN all lines should start with '##FILTER=<ID='
    with open(out_vcf, "r") as vcf_handle:
        line = vcf_handle.readline()
        assert line == '##FILTER=<ID=Ploidy,Description="Ploidy">\n'
