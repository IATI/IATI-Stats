from lxml import etree
import datetime
from collections import defaultdict

class ActivityStats(object):
    context = ''

    def __init__(self, activity=None):
        self.activity = activity

    def peryear(self):
        if self.activity == None:
            return defaultdict(int)
        activity_date = self.activity.find("activity-date[@type='start-actual']")
        if activity_date is not None and activity_date.get('iso-date'):
            try:
                date = datetime.datetime.strptime(activity_date.get('iso-date').strip('Z'), "%Y-%m-%d")
                return {int(date.year):1}
            except ValueError, e:
                print unicode(e)+self.context
        return {}
