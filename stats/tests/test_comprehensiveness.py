from lxml import etree
import datetime
import pytest

from stats.dashboard import ActivityStats


def test_comprehensiveness_is_current():
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="3"/>
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()

    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    def end_planned_date(datestring):
        activity_stats = ActivityStats()
        activity_stats.today = datetime.date(9990, 6, 1)
        activity_stats.element = etree.fromstring('''
            <iati-activity>
                <activity-date type="end-planned" iso-date="{}"/>
            </iati-activity>
        '''.format(datestring))
        return activity_stats
    
    # Any end dates in a year before this year should be current
    activity_stats = end_planned_date('9989-06-01')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9989-12-31')
    assert not activity_stats._comprehensiveness_is_current()

    # Any end dates in a year after this year should be current
    activity_stats = end_planned_date('9990-01-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9990-01-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9990-06-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9990-06-02')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9991-06-01')
    assert activity_stats._comprehensiveness_is_current()

    def datetype(typestring):
        activity_stats = ActivityStats()
        activity_stats.today = datetime.date(9990, 6, 1)
        activity_stats.element = etree.fromstring('''
            <iati-activity>
                <activity-date type="{}" iso-date="9989-06-01"/>
            </iati-activity>
        '''.format(typestring))
        return activity_stats

    # Ignore start dates
    activity_stats = datetype('start-actual')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = datetype('start-planned')
    assert activity_stats._comprehensiveness_is_current()

    # But use all end dates
    activity_stats = datetype('end-actual')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = datetype('end-planned')
    assert not activity_stats._comprehensiveness_is_current()

    # If there are two end dates, and one of them is in the future, then it is current
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date type="end-planned" iso-date="9989-06-01"/>
            <activity-date type="end-actual" iso-date="9990-12-31"/>
y
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    # Activity status should take priority over activity date
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/> 
            <activity-date type="end-actual" iso-date="9990-12-31"/>
y
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="4"/> 
            <activity-date type="end-actual" iso-date="9990-06-01"/>
y
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()


def test_comprehensiveness_empty():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org></reporting-org>
            <iati-identifier></iati-identifier>
            <title/>
            <description/>
            <transaction>
                <transaction-type/>
            </transaction>
            <transaction provider-activity-id="">
            <!-- provider-activity-id only on one transaction should get no points -->
                <transaction-type/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness() == {
        'version': 0,
        'reporting-org': 0,
        'iati-identifier': 0,
        'participating-org': 0,
        'title': 0,
        'description': 0,
        'activity-status': 0,
        'activity-date': 0,
        'sector': 0,
        'country_or_region': 0,
        'transaction_commitment': 0,
        'transaction_spend': 0,
        'transaction_currency': 0,
        'transaction_traceability': 0,
        'budget': 0,
        'contact-info': 0,
        'location': 0,
        'location_point_pos': 0,
        'sector_dac': 0,
        'capital-spend': 0,
        'document-link': 0,
        'activity-website': 0,
        #'title_recipient_language': 0,
        'conditions_attached': 0,
        'result_indicator': 0,
    }


def test_comprehensiveness_full():
    activity_stats = ActivityStats()
    root = etree.fromstring('''
        <iati-activities version="1.05">
            <iati-activity xml:lang="en">
                <reporting-org>Reporting ORG Name</reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>A title</title>
                <description>A description</description>
                <activity-status/>
                <activity-date/>
                <sector vocabulary="DAC"/>
                <recipient-country code="AI"/>
                <transaction provider-activity-id="AAA">
                    <transaction-type code="C"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction provider-activity-id="AAA">
                    <transaction-type code="E"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <activity-website/>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 1,
        'reporting-org': 1,
        'iati-identifier': 1,
        'participating-org': 1,
        'title': 1,
        'description': 1,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 1,
        'country_or_region': 1,
        'transaction_commitment': 1,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 1,
        'budget': 1,
        'contact-info': 1,
        'location': 1,
        'location_point_pos': 1,
        'sector_dac': 1,
        'capital-spend': 1,
        'document-link': 1,
        'activity-website': 1,
        #'title_recipient_language': 1,
        'conditions_attached': 1,
        'result_indicator': 1,
    }

    # Check recipient-region independently
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <recipient-region/>
            </transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['country_or_region'] == 1


def test_comprehensiveness_other_passes():
    activity_stats = ActivityStats()
    root = etree.fromstring('''
        <iati-activities>
            <iati-activity default-currency="">
            <!-- default currency can be used instead of at transaction level -->
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="2014-01-01"/>
                </transaction>
                <document-link>
                    <category code="A12"/>
                </document-link>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 0,
        'reporting-org': 0,
        'iati-identifier': 0,
        'participating-org': 0,
        'title': 0,
        'description': 0,
        'activity-status': 0,
        'activity-date': 0,
        'sector': 0,
        'country_or_region': 0,
        'transaction_commitment': 0,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 0,
        'budget': 0,
        'contact-info': 0,
        'location': 0,
        'location_point_pos': 0,
        'sector_dac': 0,
        'capital-spend': 0,
        'document-link': 1,
        'activity-website': 1,
        #'title_recipient_language': 0,
        'conditions_attached': 0,
        'result_indicator': 0,
    }


def test_comprehensiveness_location_other_passes():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <location>
                <name>Name</name>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <location>
                <description>Name</description>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <location>
                <location-administrative>Name</location-administrative>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0


def test_comprehensiveness_sector_other_passes():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <sector/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 0

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <sector vocabulary="DAC"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 1

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <sector vocabulary="DAC-3"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 1


def test_comprehensiveness_with_validation():
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(2014, 1, 1)
    root = etree.fromstring('''
        <iati-activities version="9.99">
            <iati-activity>
                <reporting-org ref="BBB"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org type="2"/>
                <activity-status/>
                <!-- Must have at least one activity-date of type start-planned or start-actual with valid date -->
                <activity-date type="end-planned" iso-date="2014-01-01" />
                <activity-date type="start-planned" iso-date="2014-0101" />
                <sector vocabulary="DAC" percentage="100" />
                <sector vocabulary="DAC" percentage="100" />
                <sector vocabulary="RO" percentage="100" />
                <sector vocabulary="RO" percentage="100" />
                <recipient-country percentage="100"/>
                <recipient-region percentage="100"/>
                <transaction>
                    <transaction-type code="C"/>
                    <value value-date="" currency=""/>
                </transaction>
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="" currency=""/>
                </transaction>
                <budget/>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    activity_stats_valid = ActivityStats()
    root_valid = etree.fromstring('''
        <iati-activities version="1.04">
            <iati-activity>
                <reporting-org ref="AAA"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org type="1"/>
                <activity-status code="2"/>
                <!-- Must have at least one activity-date of type start-planned or start-actual with valid date -->
                <activity-date type="start-planned" iso-date="2014-01-01" />
                <sector vocabulary="DAC" percentage="50" />
                <sector vocabulary="DAC" percentage="50" />
                <sector vocabulary="RO" percentage="51" />
                <sector vocabulary="RO" percentage="49" />
                <recipient-country percentage="44.5"/>
                <recipient-region percentage="55.5"/>
                <transaction>
                    <transaction-type code="C"/>
                    <value value-date="2014-01-01" currency="GBP"/>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="2014-01-01" currency="GBP"/>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <budget>
                    <period-start iso-date="2014-01-01"/>
                    <period-end iso-date="2014-01-02"/>
                    <value value-date="2014-01-01"/>
                </budget>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    comprehensiveness = activity_stats.comprehensiveness()
    not_valid = activity_stats.comprehensiveness_with_validation()
    valid = activity_stats_valid.comprehensiveness_with_validation()
    for key in [
            'version', 'iati-identifier', 'participating-org', 'activity-status',
            'activity-date', 'sector', 'country_or_region',
            'transaction_commitment', 'transaction_spend', 'transaction_currency',
            'budget',
            #'location_point_pos', 'sector_dac', 'activity-website'
            ]:
        print(key)
        assert comprehensiveness[key] == 1
        assert not_valid[key] == 0
        assert valid[key] == 1


@pytest.mark.xfail
def test_valid_value():
    # We should test that a value elements contain a valid decimal, where relevant
    raise NotImplementedError

@pytest.mark.xfail
def test_transaction_exclusions():
    raise NotImplementedError
    

def test_comprehensiveness_transaction_level_elements():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <sector/>
                <recipient-country/>
            </transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['sector'] == 1
    assert comprehensiveness['country_or_region'] == 1

    # Check recipient-region too
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <recipient-region/>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['country_or_region'] == 1

    # If is only at transaction level, but not for all transactions, we should get 0
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <sector/>
                <recipient-country/>
                <recipient-region/>
            </transaction>
            <transaction></transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['sector'] == 0
    assert comprehensiveness['country_or_region'] == 0


def test_comprehensiveness_with_validation_transaction_level_elements():
    activity_stats = ActivityStats()
    activity_stats.today = datetime.date(2014, 1, 1)
    root = etree.fromstring('''
        <iati-activities version="9.99">
            <iati-activity>
                <sector/>
                <recipient-country/>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    activity_stats_valid = ActivityStats()
    root_valid = etree.fromstring('''
        <iati-activities version="1.04">
            <iati-activity>
                <transaction>
                    <sector/>
                    <recipient-country/>
                </transaction>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    comprehensiveness = activity_stats.comprehensiveness()
    not_valid = activity_stats.comprehensiveness_with_validation()
    valid = activity_stats_valid.comprehensiveness_with_validation()
    for key in ['sector', 'country_or_region']:
        print(key)
        assert comprehensiveness[key] == 1
        assert not_valid[key] == 0
        assert valid[key] == 1
    


## Denominator


def test_comprehensivness_denominator_default():
    activity_stats = ActivityStats()
    activity_stats._comprehensiveness_is_current = lambda: True
    assert activity_stats.comprehensiveness_denominator_default() == 1
    activity_stats = ActivityStats()
    activity_stats._comprehensiveness_is_current = lambda: False
    assert activity_stats.comprehensiveness_denominator_default() == 0


def test_comprehensivness_denominator_empty():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators() == {}
