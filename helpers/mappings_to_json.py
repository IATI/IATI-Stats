import json
import sys

from lxml import etree as ET


def mapping_to_json(mappings):
    for mapping in mappings.getroot().xpath('//mapping'):
        out = {
            'path': mapping.find('path').text,
            'codelist': mapping.find('codelist').attrib['ref']
        }
        if mapping.find('condition') is not None:
            out['condition'] = mapping.find('condition').text
        yield out


mappings = []
for filename in sys.argv[1:]:
    doc = ET.parse(filename)
    mappings += mapping_to_json(doc)

print(json.dumps(mappings))
