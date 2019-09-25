import pytest

from mutacc.parse.parse_ped import parse_ped

def test_parse_ped(ped_path):

    family = parse_ped(ped_path)
    assert isinstance(family, dict)
    
