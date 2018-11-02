import pytest
from yaml import YAMLError

from ped_parser.exceptions import PedigreeError

from mutacc.parse.yaml_parse import yaml_parse, YAMLFieldsError

INVALID_YAML = "tests/fixtures/case_invalid_yaml.yaml"
INVALID_KEYS = "tests/fixtures/case_invalid_keys.yaml"
INVALID_KEYS2 = "tests/fixtures/case_invalid_keys2.yaml"
INVALID_PEDIGREE = "tests/fixtures/case_invalid_pedigree.yaml"
def test_yaml_parse():

    with pytest.raises(YAMLError) as error:

        case = yaml_parse(INVALID_YAML)

    with pytest.raises(YAMLFieldsError) as error:

        case = yaml_parse(INVALID_KEYS)

    with pytest.raises(YAMLFieldsError) as error:

        case = yaml_parse(INVALID_KEYS2)

    with pytest.raises(PedigreeError) as error:

        case = yaml_parse(INVALID_PEDIGREE)
