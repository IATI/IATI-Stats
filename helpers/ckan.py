import json
import os
from collections import defaultdict

out = defaultdict(dict)
licenses = {}

# The ckan directory is the one produced by https://github.com/Bjwebb/IATI-Registry-Refresher/tree/save_ckan_json

for publisher in os.listdir('ckan'):
    with open(os.path.join('ckan', publisher)) as fp:
        try:
            for package in json.load(fp)['result']['results']:
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
