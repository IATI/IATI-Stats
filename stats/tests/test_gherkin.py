# coding=utf-8
import pytest
from lxml import etree

from stats.analytics import ActivityStats


class MockActivityStats(ActivityStats):
    def __init__(self, major_version):
        self.major_version = major_version
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version


@pytest.mark.parametrize("major_version", ["1", "2"])
def test_gherkin_titles(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["2.4_title"]["Title is present"] == {"True": 0, "False": 1, "None": 0}
    assert gherkin_dict["2.4_title"]["Title has at least 10 characters"] == {"True": 0, "False": 1, "None": 0}

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <title>
                <narrative>Title</narrative>
            </title>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["2.4_title"]["Title is present"] == {"True": 1, "False": 0, "None": 0}
    assert gherkin_dict["2.4_title"]["Title has at least 10 characters"] == {"True": 0, "False": 1, "None": 0}

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <title>
                <narrative>Title with at least 10 characters</narrative>
            </title>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["2.4_title"]["Title is present"] == {"True": 1, "False": 0, "None": 0}
    assert gherkin_dict["2.4_title"]["Title has at least 10 characters"] == {"True": 1, "False": 0, "None": 0}

    # The same dict should also appear in by_hierarchy
    assert activity_stats.by_hierarchy()["1"]["gherkin_tests"]["2.4_title"]["Title has at least 10 characters"] == {
        "True": 1,
        "False": 0,
        "None": 0,
    }
    assert activity_stats.by_hierarchy()["1"]["gherkin_tests"]["2.4_title"] == gherkin_dict["2.4_title"]


@pytest.mark.parametrize("major_version", ["1", "2"])
def test_gherkin_skip(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert "3.3_traceability" not in gherkin_dict


def test_gherkin_threshold():
    activity_stats = MockActivityStats(major_version="2")
    activity_stats.element = etree.fromstring("""
        <iati-activity>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["4.8_documents"]["Conditions document"] == {"True": 0, "False": 0, "None": 1}

    activity_stats = MockActivityStats(major_version="2")
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <activity-status code="2" />
            <default-aid-type code="A01" />
            <transaction>
                <transaction-type code="3" />
                <value currency="EUR" value-date="2012-01-01">1000000</value>
            </transaction>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["4.8_documents"]["Conditions document"] == {"True": 0, "False": 1, "None": 0}

    activity_stats = MockActivityStats(major_version="2")
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <activity-status code="2" />
            <default-aid-type code="A01" />
            <transaction>
                <transaction-type code="3" />
                <value currency="EUR" value-date="2012-01-01">1000000</value>
            </transaction>
            <document-link><category code="A04" /></document-link>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["4.8_documents"]["Conditions document"] == {"True": 1, "False": 0, "None": 0}


def test_hierarchy_exclusions():
    activity_stats = MockActivityStats(major_version="2")
    activity_stats.element = etree.fromstring("""
        <iati-activity hierarchy="1">
            <activity-status code="2" />
            <default-aid-type code="A01" />
        </iati-activity>
    """)
    activity_stats.folder = "fcdo"
    gherkin_dict = activity_stats.gherkin_tests()
    gherkin_dict_with_hierarchy_exclusions = activity_stats.gherkin_tests_hierarchy_exclusions()
    assert gherkin_dict["2.10_aid_type"]["Aid type is present"] == {"True": 1, "False": 0, "None": 0}
    assert gherkin_dict_with_hierarchy_exclusions["2.10_aid_type"]["Aid type is present"] == {
        "True": 0,
        "False": 0,
        "None": 1,
    }
