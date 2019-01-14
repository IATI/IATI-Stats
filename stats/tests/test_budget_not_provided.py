import json
from lxml import etree

from collections import defaultdict, OrderedDict
from stats.common.decorators import *


CODELISTS = {'1':{}, '2':{}}
for major_version in ['1', '2']:
    CODELISTS[major_version]['BudgetNotProvided'] = set(c['code'] for c in json.load(open('../../helpers/codelists/{}/{}.json'.format(major_version, 'BudgetNotProvided')))['data'])

def test_budget_not_provided_works():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity budget-not-provided="1">
            </iati-activity>
    ''')
    assert activity_stats._budget_not_provided() == 1


def test_budget_not_provided_fails():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity>
            </iati-activity>
    ''')
    assert activity_stats._budget_not_provided() is None


def test_budget_validation_bools():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity budget-not-provided="3">
            </iati-activity>
    ''')
    assert (not (len(activity_stats.element.findall('budget')) > 0) and str(activity_stats._budget_not_provided()) in CODELISTS['2']['BudgetNotProvided'])



class CommonSharedElements(object):
    blank = False


class ActivityStats(CommonSharedElements):
    """ Stats calculated on a single iati-activity. """
    element = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''
    comprehensiveness_current_activity_status = None
    now = datetime.datetime.now()

    def _budget_not_provided(self):
        if self.element.attrib.get('budget-not-provided'):
            return int(self.element.attrib.get('budget-not-provided'))
        else:
            return None
