from flask import current_app
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource

import flask_praetorian
import marshmallow
import os

from otbp.resources import security_rules
from otbp.models import db, ImageModel
from otbp.schemas import ImageSchema, ErrorSchema

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

@doc(
    tags=['Photos'],
    security=security_rules
)
class ImageResource(MethodResource):

    @marshal_with(ImageSchema, code=201)
    @marshal_with(ErrorSchema, code=400)
    @use_kwargs({'file': marshmallow.fields.Field(location='files')})
    @flask_praetorian.auth_required
    def post(self, file):
        # validate the file
        filename = file.filename

        if not '.' in filename:
            return {'message': 'Invalid image filename (missing extension)'}, 400

        ext = filename.rsplit('.', 1)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return {'message': 'Invalid image file type'}, 400

        # Create a new Image in the database, then save the image file with the id
        # TODO use UUID?
        image = ImageModel()
        image.user = flask_praetorian.current_user()
        db.session.add(image)
        db.session.commit()

        directory = current_app.config['UPLOAD_DIRECTORY']

        saved_filepath = os.path.join(directory, f'{image.id}.{ext}')
        file.save(saved_filepath)

        image.filepath = saved_filepath
        db.session.commit()

        return image, 201
