import click

from mutacc.utils.hk_call import findPath

@click.command()
@click.argument('internal_id')
@click.pass_context
def add(context, internal_id):

    """
        Adds content to DB
    """
    files = findPath(internal_id)

    for file in files['paths']:

        click.echo('adding %s to %s' % (file, context.obj['database']))
