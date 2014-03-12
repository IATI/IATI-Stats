import os
import hashlib

base = os.path.join('out', 'aggregated-file')
output_dir = 'data'
for publisher in os.listdir(output_dir):
    if not os.path.isdir(os.path.join(output_dir, publisher)):
        continue
    for dataset in os.listdir(os.path.join(output_dir, publisher)):
        md5hash = hashlib.md5(os.path.join(output_dir, publisher, dataset)).hexdigest()
        if os.path.exists(os.path.join('gitout','hash',md5hash)):
            try:
                os.makedirs(os.path.join(base, publisher))
            except OSError:
                pass
            os.symlink(os.path.join('/home','bjwebb','iati','stats','gitout','hash',md5hash), os.path.join(base, publisher, dataset))

