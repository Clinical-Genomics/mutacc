"""
    Tests for vcf_handler.py
"""

import pytest

from mutacc.utils.vcf_handler import INFOParser


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
    parser_info = [{"id": "test_id", "multivalue": True}]
    with pytest.raises(ValueError) as error:
        parser = INFOParser(parser_info=parser_info, stream="read")

    parser_info = [
        {
            "id": "test_id",
            "multivalue": True,
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
    # test multivalue, array of arrays, eg separated with ',' and then  '|'
    class MockVariant:
        def __init__(self, info_dict):
            self.INFO = info_dict

    info_dict = {"ID1": "value11|value12,value21|value22"}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [
        {
            "id": "ID1",
            "multivalue": True,
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
    info_dict = {"RankScore": "case_1: 10"}
    mock_variant = MockVariant(info_dict=info_dict)
    parser_info = [
        {
            "id": "RankScore",
            "multivalue": False,
            "format": "case_id: rank_score",
            "format_separator": ":",
            "target": ["rank_score"],
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
        {"id": "TYPE", "multivalue": False, "out_name": "var_type", "out_type": "str"}
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

    parser_info[0]["target"] = "all"
    parser = INFOParser(parser_info=parser_info, stream="write")
    variant_dict = {
        "ID1": [
            {"value1": 1, "value2": "2", "value3": 3},
            {"value1": 4, "value2": 5, "value3": 6},
        ]
    }
    parsed_variant = parser.parse(variant_dict)
    assert parsed_variant == "parsed_value=1|2|3,4|5|6"
