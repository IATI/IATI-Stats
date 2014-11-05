from lxml import etree
import datetime

from stats.dashboard import ActivityStats

# FIXME comprehensiveness is spelt wrong

def test_comperhensiveness_is_current():
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="3"/>
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()

    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    def end_planned_date(datestring):
        return etree.fromstring('''
            <iati-activity>
                <activity-date type="end-planned" iso-date="{}"/>
            </iati-activity>
        '''.format(datestring))
    
    # Any end dates in a year before this year should be current
    activity_stats.element = end_planned_date('9989-06-01')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats.element = end_planned_date('9989-12-31')
    assert not activity_stats._comprehensiveness_is_current()

    # Any end dates in a year after this year should be current
    activity_stats.element = end_planned_date('9990-01-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats.element = end_planned_date('9990-01-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats.element = end_planned_date('9990-06-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats.element = end_planned_date('9990-06-02')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats.element = end_planned_date('9991-06-01')
    assert activity_stats._comprehensiveness_is_current()

    def datetype(typestring):
        return etree.fromstring('''
            <iati-activity>
                <activity-date type="{}" iso-date="9989-06-01"/>
            </iati-activity>
        '''.format(typestring))

    # Ignore start dates
    activity_stats.element = datetype('start-actual')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats.element = datetype('start-planned')
    assert activity_stats._comprehensiveness_is_current()

    # But use all end dates
    activity_stats.element = datetype('end-actual')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats.element = datetype('end-planned')
    assert not activity_stats._comprehensiveness_is_current()

    # If there are two end dates, and one of them is in the future, then it is current
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date type="end-planned" iso-date="9989-06-01"/>
            <activity-date type="end-actual" iso-date="9990-12-31"/>
y
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()
