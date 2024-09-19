import json
import os
from collections import defaultdict
from glob import glob

out = defaultdict(dict)
licenses = {}


for filepath in glob(os.path.join('metadata', '*', '*')):
    publisher = filepath.split('/', 2)[1]
    with open(filepath) as fp:
        try:
            package = json.load(fp)
            if package['resources']:
                extras = dict((x['key'], x['value']) for x in package['extras'])
                out[publisher][package['name']] = {
                    'title': package['title'],
                    'extras': extras,
                    'license_id': package['license_id'],
                    'resource': package['resources'][0],
                }
                if package['license_id']:
                    licenses[package['license_id']] = {
                        'name': package['license_title'],
                        'url': package.get('license_url'),
                    }
        except ValueError:
            print('{0} is not valid JSON'.format(publisher))

with open('ckan.json', 'w') as fp:
    json.dump(out, fp, indent=2, sort_keys=True)
with open('licenses.json', 'w') as fp:
    json.dump(licenses, fp, indent=2, sort_keys=True)
