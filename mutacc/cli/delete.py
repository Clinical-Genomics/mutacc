import click

@click.command()
@click.argument('sample_id')
@click.pass_context
def delete(context, sample_id):

    """
       Deletes content to DB
    """

    click.echo('')
