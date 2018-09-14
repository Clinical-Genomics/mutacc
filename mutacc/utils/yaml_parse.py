import yaml

class YAMLKeysError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def yaml_parse(yaml_file):

    with open(yaml_file, 'r') as yaml_handle:

        try:
            yaml_dict = yaml.load(yaml_handle)

        except yaml.YAMLError as exc:
            print('Error loading yaml object: ', exc)

            raise
    
    if len(yaml_dict.keys()) != 3:

        raise YAMLKeysError("Can only contain three field ('case', 'samples', and 'variant')")

    if set(yaml_dict.keys()) != set(['case','variant','samples']):

        raise YAMLKeysError("Yaml object must contain 'case', 'samples', and 'variant'")
    
    return yaml_dict
