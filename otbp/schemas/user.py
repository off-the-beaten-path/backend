import marshmallow

from otbp.schemas import ma


class UserAuthSchema(ma.Schema):
    class Meta:
        strict = True

    jwt = marshmallow.fields.Str()


class UserLoginRegisterSchema(ma.Schema):
    class Meta:
        strict = True

    email = marshmallow.fields.Str()
    password = marshmallow.fields.Str()


class UserChangePasswordSchema(ma.Schema):
    class Meta:
        strict = True

    old = marshmallow.fields.Str()
    new = marshmallow.fields.Str()


class UserSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int()
