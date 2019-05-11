from flask.cli import with_appcontext

import click


def init_cli(app):
    app.cli.add_command(seed_test_data)
    app.cli.add_command(seed_test_user)


@click.command()
@with_appcontext
def seed_test_user():
    """
    seed test user for casual interaction
    """
    from otbp.models import db
    db.create_all()


@click.command()
@with_appcontext
def seed_test_data():
    """
    create (and/or reset) the e2e testing database and seed it
    """
