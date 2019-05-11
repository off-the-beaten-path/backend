# thanks to https://medium.com/grammofy/testing-your-python-api-app-with-json-schema-52677fe73351
# and https://medium.com/grammofy/handling-complex-json-schemas-in-python-9eacc04a60cf
# for major inspiration!

# also major props to https://www.jsonschema.net/ for writing schemas!

from os.path import join, dirname
from jsonschema import validate

import jsonref


def validate_json(data, schema_file):

    schema = _load_json_schema(schema_file)
    return validate(data, schema)


def _load_json_schema(filename):
    relative_path = join('schemas', filename)
    absolute_path = join(dirname(__file__), relative_path)

    base_path = dirname(absolute_path)
    base_uri = f'file://{base_path}/'

    with open(absolute_path) as schema_file:
        return jsonref.load(schema_file, base_uri=base_uri, jsonschema=True)
