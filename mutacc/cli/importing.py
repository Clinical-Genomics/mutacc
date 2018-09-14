import click

from mutacc.utils.yaml_parse import yaml_parse

@click.command('import')
@click.option('--case', type = click.Path(exists = True), help = " .yaml file for case. See README.md for information on what to include or example .yaml file in data/data.yaml")
@click.option('--padding', type = click.IntRange(0, 5000), default = 300)
@click.pass_context
def importing(context, case, padding):

    """
        Import cases to the database
    """
            
    case = yaml_parse(case)
   
    click.echo(case)
