from flask.cli import with_appcontext

import click


def init_cli(app):
    app.cli.add_command(seed_db)
    app.cli.add_command(create_db)


@click.command()
@with_appcontext
def seed_db():
    """
    create the database
    """
    from faker import Faker
    from faker.providers import geo
    from flask import current_app

    import os
    import random
    import shutil

    from otbp.models import db, UserModel, CheckInModel, GeoCacheModel, ImageModel
    from otbp.praetorian import guard

    # delete and recreate the database
    db.drop_all()
    db.create_all()

    # delete and recreate the upload directory
    shutil.rmtree(current_app.config['UPLOAD_DIRECTORY'])
    os.makedirs(current_app.config['UPLOAD_DIRECTORY'])

    fake = Faker()
    fake.add_provider(geo)

    user = UserModel(email='test@example.com',
                     password=guard.encrypt_password('password123'),
                     roles='player')

    db.session.add(user)

    images = []

    for index in range(1, 6):
        image = ImageModel(user=user)
        db.session.add(image)
        db.session.commit()

        filepath = os.path.join(os.getcwd(), 'testdata', 'images', f'pic{index}.JPG')
        ext = filepath.rsplit('.', 1)[1].lower()

        directory = current_app.config['UPLOAD_DIRECTORY']
        saved_filename = f'{image.id}.{ext}'
        saved_filepath = os.path.join(directory, saved_filename)

        shutil.copy(filepath, saved_filepath)

        image.filepath = saved_filepath
        image.filename = saved_filename

        db.session.commit()
        images.append(image)

    for i in range(0, 25):
        lat = float(fake.latitude())
        lng = float(fake.longitude())

        geocache = GeoCacheModel(lat=lat, lng=lng, user=user)
        checkin = CheckInModel(text=fake.sentence(),
                               lat=lat + random.uniform(-0.001, 0.001),
                               lng=lng + random.uniform(-0.001, 0.001),
                               final_distance=random.random() * 20,
                               geocache=geocache,
                               user=user)

        if random.choice((True, False)):
            checkin.image = random.choice(images)

        db.session.add(geocache)
        db.session.add(checkin)

    db.session.commit()

    print('Seeded 31 items into the database.')


@click.command()
@with_appcontext
def create_db():
    """
    create the database
    """
    from otbp.models import db

    # delete and recreate the database
    db.drop_all()
    db.create_all()

    print('Created the database')
