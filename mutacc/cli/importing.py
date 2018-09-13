import click

from mutacc.utils.json_parse import parse_json

@click.command('import')
@click.option('--bam', multiple = True, type = click.Path(exists = True), help = 'path to .bam file')
@click.option('--fastq', multiple = True, type = click.Path(exists = True), help = 'path to .fastq file')
@click.option('--variant', help = 'Variant data as JSON string, or path to .json file')
@click.option('--case', help = 'Metadata for the case as JSON string or path to .json file')
@click.pass_context
def importing(context, bam, fastq, variant, case):

    """
        Import cases to the database
    """
            
    case = parse_json(case)
    variant = parse_json(variant)

    for path in bam:
        click.echo(path)
    
    click.echo(case)
    click.echo(variant)

