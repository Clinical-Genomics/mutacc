import click

from mutacc.utils.hk_call import find_files

@click.command()
@click.argument('internal_id')
@click.pass_context
def add(context, internal_id):

    """
        Adds content to DB
    """
    files = find_files(internal_id = internal_id, tags = ("vcf-snv-clinical", "pedigree"))

    for key in files.keys():
        
        click.echo('%s: ' % (key))
        
        for file in files[key]:
            
            click.echo('    %s' % (file))
