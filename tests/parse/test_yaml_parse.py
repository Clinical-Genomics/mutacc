import pytest
from yaml import YAMLError

from mutacc.parse.yaml_parse import yaml_parse, YAMLFieldsError

INVALID_YAML = "tests/fixtures/case_invalid_yaml.yaml"
INVALID_KEYS = "tests/fixtures/case_invalid_keys.yaml"

def test_yaml_parse():

    with pytest.raises(YAMLError) as error:

        case = yaml_parse(INVALID_YAML)

    with pytest.raises(YAMLFieldsError) as error:

        case = yaml_parse(INVALID_KEYS)
