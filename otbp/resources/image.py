from flask import current_app, send_from_directory
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
    tags=['Image'],
    security=security_rules
)
class ImageRetrievalResource(MethodResource):

    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self, filename):
        image_id, ext = filename.split('.')

        image = ImageModel.query.get_or_404(image_id)

        if image.user_id != flask_praetorian.current_user_id():
            return {'message': 'Unauthorized'}, 401

        return send_from_directory(current_app.config['UPLOAD_DIRECTORY'], filename)


@doc(
    tags=['Image'],
    security=security_rules
)
class ImageUploadResource(MethodResource):

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
        image = ImageModel()
        image.user = flask_praetorian.current_user()
        db.session.add(image)
        db.session.commit()

        directory = current_app.config['UPLOAD_DIRECTORY']
        saved_filename = f'{image.id}.{ext}'
        saved_filepath = os.path.join(directory, saved_filename)
        file.save(saved_filepath)

        image.filepath = saved_filepath
        image.filename = saved_filename
        db.session.commit()

        return image, 201
