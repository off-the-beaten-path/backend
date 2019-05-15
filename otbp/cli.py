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
    from faker import Faker
    from faker.providers import geo

    import random

    from otbp.models import db, UserModel, CheckInModel, GeoCacheModel
    from otbp.praetorian import guard

    db.drop_all()
    db.create_all()

    fake = Faker()
    fake.add_provider(geo)

    user = UserModel(email='test@example.com',
                     password=guard.encrypt_password('password123'),
                     roles='player')

    db.session.add(user)

    for i in range(0, 25):
        geocache = GeoCacheModel(lat=fake.latitude(), lng=fake.longitude())
        checkin = CheckInModel(text=fake.sentence(),
                               lat=fake.latitude(),
                               lng=fake.longitude(),
                               final_distance=random.random() * 20,
                               geocache=geocache,
                               user=user)
        db.session.add(geocache)
        db.session.add(checkin)

    db.session.commit()

    print('Seeded 26 items into the database.')
