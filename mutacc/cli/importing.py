import json
import sys, os

import click

from mutacc.utils.hk_call import find_files

@click.command('import')
@click.option('--bam', multiple = True, type = click.Path(exists = True), help = 'path to .bam file')
@click.option('--fastq', multiple = True, type = click.Path(exists = True), help = 'path to .fastq file')
@click.option('--variant', help = 'Variant data as JSON string, or path to .json file')
@click.option('--case', help = 'Metadata for the case as JSON string or path to .json file')
@click.pass_context
def importing(context,bam,fastq,variant,case):

    """
        Import cases to the database
    """
            
    case = parse_JSON(case)
    variant = parse_JSON(variant)

    for path in bam:
        click.echo(path)
    
    click.echo(case)
    click.echo(variant)

def parse_JSON(json_format):

    if json_format[0] == '~':

        json_format = os.path.expanduser(json_format)

    if os.path.isfile(json_format):

        with open(json_format, 'r') as json_handle:
                
            try: 
                json_format = json.load(json_handle)

            except json.JSONDecodeError:
                    
                sys.exit("Not valid Json")

    else:

        try: 

            json_format = json.loads(json_format)

        except json.JSONDecodeError:
                    
            sys.exit("Not valid Json")

    return json_format
