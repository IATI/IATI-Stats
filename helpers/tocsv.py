import csv
import json
import sys

writer = csv.writer(sys.stdout, lineterminator='\n')

with open('aggregated.json') as fp:
    aggregated = json.load(fp)
    for line in sorted(aggregated[sys.argv[1]].items()):
        writer.writerow(line)
