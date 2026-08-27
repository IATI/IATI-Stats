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
def test_comprehensiveness_is_current(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <title>
                <narrative>Title</narrative>
            </title>
        </iati-activity>
    """)
    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["iati-activity"]["Title: Title is present"] == 1
    assert gherkin_dict["iati-activity"]["Title: Title has at least 10 characters"] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring("""
        <iati-activity>
            <title>
                <narrative>Title with at least 10 characters</narrative>
            </title>
        </iati-activity>
    """)

    gherkin_dict = activity_stats.gherkin_tests()
    assert gherkin_dict["iati-activity"]["Title: Title is present"] == 1
    assert gherkin_dict["iati-activity"]["Title: Title has at least 10 characters"] == 1

    assert (
        activity_stats.by_hierarchy()["1"]["gherkin_tests"]["iati-activity"]["Title: Title has at least 10 characters"]
        == 1
    )

    assert "Traceability: Traceability" not in gherkin_dict["iati-activity"]
