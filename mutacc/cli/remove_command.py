import click

from mutacc.mutaccDB.remove_case import remove_case_from_db

@click.command('remove')
@click.argument('case_id')
@click.pass_context
def remove_command(context, case_id):

    """
       Deletes case from mutacc DB
    """

    adapter = context.obj['adapter']

    remove_case_from_db(adapter, case_id)
