import stats.analytics
from statsrunner.aggregate import make_blank
from collections import defaultdict

import yaml

schema = {}

def get_schema(value):
    if type(value) == int: 
        return {"type": "integer"}
    elif type(value) == defaultdict:
        return {"type": "object", "additionalProperties": get_schema(value.default_factory())}
    raise NotImplementedError

for key, value in make_blank(stats.analytics).items():
    try:
        schema[key] = get_schema(value)
    except NotImplementedError:
        print("Not implemented", key, value)

with open("schema.yml", "w") as fp:
    yaml.dump(schema, fp)
