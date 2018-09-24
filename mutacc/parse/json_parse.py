import json
from pathlib import Path

def parse_json(json_format):

    path = Path(json_format)
    path = Path.expanduser(path)
    path = Path.absolute(path)

    if Path.is_file(path):

        with open(path, 'r') as json_handle:
                
            try: 
                json_format = json.load(json_handle)

            except json.JSONDecodeError:
                
                print("Not valid JSON")

                raise

    else:

        try: 

            json_format = json.loads(json_format)

        except json.JSONDecodeError:

            print("Not valid JSON")

            raise

    
    return json_format
