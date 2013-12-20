import csv, os, json

coverage = csv.writer(open('out-ti-csv/1-coverage.csv','w'))
coverage.writerow(['endorser','A','B','C','D'])
timelag = csv.writer(open('out-ti-csv/2-timelag.csv','w'))
timelag.writerow(['endorser','frequency','timelag'])
detail = csv.writer(open('out-ti-csv/3-detail.csv','w'))
detail_columns = [ unicode(x).zfill(2) for x in range(1,40) ]
detail.writerow(['endorser','activities'] + detail_columns)
forward = csv.writer(open('out-ti-csv/4-forward-looking.csv','w'))
forward.writerow(['endorser','numerator','2014 Agg','2014 Act','2015 Agg','2015 Act','2016 Agg', '2016 Act'])

for endorser in sorted(os.listdir('out-ti')):
    if not endorser.endswith('.json'): continue
    endorser_name = endorser[:-5]
    aggregated = json.load(open(os.path.join('out-ti', endorser)))
    coverage.writerow([endorser_name,
        aggregated['bottom_hierarchy']['coverage_A'],
        aggregated['bottom_hierarchy']['coverage_B'],
        aggregated['bottom_hierarchy']['coverage_C'],
        aggregated['bottom_hierarchy']['coverage_D']])
    timelag.writerow([endorser_name,aggregated['frequency'],aggregated['timelag']])
    detail.writerow([endorser_name,aggregated['bottom_hierarchy']['activities']]+[aggregated['bottom_hierarchy']['current_activity_elements'].get(x) for x in detail_columns])
    forward.writerow([endorser_name,
        aggregated['bottom_hierarchy']['coverage_numerator'],
        aggregated['forward_looking_aggregate'].get('2014') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2014') or 0,
        aggregated['forward_looking_aggregate'].get('2015') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2015') or 0,
        aggregated['forward_looking_aggregate'].get('2016') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2016') or 0
        ])

