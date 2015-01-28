from stats.common import budget_year
from stats.dashboard import ActivityStats
from lxml import etree

def test_forwardlooking_is_current():
    activity_stats = ActivityStats()

    # If there are no end dates, the activity is current
    activity_stats.element = etree.fromstring('''<iati-activity>
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="start-planned" />
        <activity-date iso-date="9980-01-01" type="start-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)

    # If there is an end date before the given year, it's not current
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-planned" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-actual" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)

    # If there is an end date on or after the given year, it is current
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="end-planned" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="end-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-planned" />
        <activity-date iso-date="9990-01-01" type="end-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)

def wrap_activity(activity):
    return etree.fromstring('<iati-activities version="2.01">{}</iati-activities>'.format(activity)).find('iati-activity')

def test_forwardlooking_is_current_2xx():
    activity_stats = ActivityStats()

    # If there are no end dates, the activity is current
    activity_stats.element = wrap_activity('''<iati-activity>
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="1" />
        <activity-date iso-date="9980-01-01" type="2" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)

    # If there is an end date before the given year, it's not current
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="3" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="4" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)

    # If there is an end date on or after the given year, it is current
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="3" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="4" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="3" />
        <activity-date iso-date="9990-01-01" type="4" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
