import yaml

from mutacc.parse.path_parse import parse_path

SAMPLE = ["sample_id", "mother", "father", "bam","fastq"]
class YAMLFieldsError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def yaml_parse(yaml_file):
    
    yaml_file = parse_path(yaml_file)

    with open(yaml_file, 'r') as yaml_handle:

        try:
            yaml_dict = yaml.load(yaml_handle)

        except yaml.YAMLError as exc:
            print('Error loading yaml object: ', exc)

            raise
    
    if len(yaml_dict.keys()) != 3:

        raise YAMLFieldsError("Can only contain three field ('case', 'samples', and 'variants')")

    if set(yaml_dict.keys()) != set(['case','variants','samples']):

        raise YAMLFieldsError("Yaml object must contain 'case', 'samples', and 'variants'")
    
    for sample in yaml_dict["samples"]:

        if not set(SAMPLE).issubset(set(sample.keys())):

            raise YAMLFieldsError("sample object must contain 'sample_id', 'mother', 'father',\
                    'bam', and 'fastq'")
             
    return yaml_dict
