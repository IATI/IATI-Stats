import csv
import json
import sys

traceable_activities_by_publisher = json.load(open("out/current/aggregated/traceable_activities_by_publisher_id.json"))
# This may be different from the total number of activity identifiers
total_activities_by_publisher = json.load(open("out/current/aggregated/traceable_activities_by_publisher_id_denominator.json"))
traceable_spend_by_publisher = json.load(open("out/current/aggregated/traceable_sum_commitments_and_disbursements_by_publisher_id.json"))
total_spend_by_publisher = json.load(open("out/current/aggregated/traceable_sum_commitments_and_disbursements_by_publisher_id_denominator.json"))

csvwriter = csv.writer(sys.stdout)

for publisher, total_activities in total_activities_by_publisher.items():
    traceable_activities = traceable_activities_by_publisher.get(publisher, 0)
    percentage_activities = traceable_activities / total_activities * 100
    traceable_spend = traceable_spend_by_publisher.get(publisher, 0)
    total_spend = total_spend_by_publisher.get(publisher, 0)
    if total_activities == 0 or traceable_activities == 0:
        continue
    csvwriter.writerow([
        publisher,
        traceable_activities,
        total_activities,
        f"{percentage_activities}" if percentage_activities == 100 else f"{percentage_activities:.2g}",
        traceable_spend,
        total_spend,
        "" if total_spend == 0 else f"{(traceable_spend / total_spend * 100):.2g}",
    ])
