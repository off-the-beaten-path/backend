from flask.cli import with_appcontext

import click


def init_cli(app):
    app.cli.add_command(create_db)


@click.command()
@with_appcontext
def create_db():
    """
    create the database
    """
    from otbp.models import db
    db.create_all()
