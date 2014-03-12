import os
import hashlib
import shutil

base = os.path.join('out', 'aggregated-file')
output_dir = 'data'
gitout_dir = os.path.join('/home','bjwebb','iati','stats','gitout')
for publisher in os.listdir(base):
    for dataset in os.listdir(os.path.join(base, publisher)):
        md5hash = hashlib.md5(os.path.join(output_dir, publisher, dataset)).hexdigest()
        if not os.path.exists(os.path.join('gitout','hash',md5hash)):
            shutil.move(os.path.join(base, publisher, dataset), os.path.join(gitout_dir,'hash',md5hash))
            os.symlink(os.path.join(gitout_dir,'hash',md5hash), os.path.join(base, publisher, dataset))
