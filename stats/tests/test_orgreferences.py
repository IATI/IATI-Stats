# coding=utf-8
import pytest
from lxml import etree

from stats.analytics import ActivityStats


class MockActivityStats(ActivityStats):
    def __init__(self, version):
        if len(version) == 1 or len(version.split(".")) < 2:
            self.major_version = version
            self.minor_version = "02"
        else:
            self.major_version = version.split(".")[0]
            self.minor_version = version.split(".")[1]
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

    def _minor_version(self):
        return self.minor_version

    def _version(self):
        return self._major_version() + "." + self._minor_version()


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
     """,
            1,
        ),
        (
            """
        <iati-activity>
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            2,
        ),
    ],
)
def test_transaction_total(version, xml, expected):
    """
    Count of total transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.transaction_total() == expected


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
            </transaction>
        </iati-activity>
     """,
            (0, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org />
            </transaction>
        </iati-activity>
     """,
            (1, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="" />
            </transaction>
        </iati-activity>
     """,
            (1, 1, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
     """,
            (1, 1, 1, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="XI-IATI-1002" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="NP-COA-370" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="47122" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
    ],
)
def test_transaction_receiver_org_stats(version, xml, expected):
    """
    Counts of receiver organisation references on transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.receiver_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.receiver_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.receiver_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.receiver_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.receiver_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 1, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="XI-IATI-1002" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="NP-COA-370" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="47122" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (2, 2, 2, 1, 1),
        ),
    ],
)
def test_transaction_provider_org_stats(version, xml, expected):
    """
    Counts of provider organisation references on transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.provider_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.provider_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.provider_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.provider_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.provider_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="NP-COA-370" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="XI-IATI-1002" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="47122" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="NP-COA-370" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="XI-IATI-1002" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="47122" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="NP-COA-370" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1, "XI-IATI": 1, "NP-COA": 2},
        ),
    ],
)
def test_transaction_provider_org_valid_prefixes(version, xml, expected):
    """
    Counts of provider organisation references valid prefixes on transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.provider_org_valid_prefixes()[prefix] == expected[prefix]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="NP-COA-370" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="XI-IATI-1002" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="47122" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="NP-COA-370" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="XI-IATI-1002" />
            </transaction>
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="47122" />
            </transaction>
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="NP-COA-370" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1, "XI-IATI": 1, "NP-COA": 2},
        ),
    ],
)
def test_transaction_receiver_org_valid_prefixes(version, xml, expected):
    """
    Counts of receiver organisation references valid prefixes on transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.receiver_org_valid_prefixes()[prefix] == expected[prefix]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="AA-AAA-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 1),
        ),
    ],
)
def test_transaction_funding_org_stats(version, xml, expected):
    """
    Counts of funding organisation references on activity.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.funding_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.funding_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.funding_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.funding_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.funding_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="XI-IATI-1002" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="47122" role="1" />
            <participating-org ref="CC-CCC-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
    ],
)
def test_transaction_funding_org_valid_prefixes(version, xml, expected):
    """
    Counts of funding organisation reference valid prefixes on activity.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.funding_org_valid_prefixes()[prefix] == expected[prefix]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 1),
        ),
    ],
)
def test_transaction_accountable_org_stats(version, xml, expected):
    """
    Counts of accountable organisation references on activity
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.accountable_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.accountable_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.accountable_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.accountable_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.accountable_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="XI-IATI-1002" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="47122" role="2" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
    ],
)
def test_transaction_accountable_org_valid_prefixes(version, xml, expected):
    """
    Counts of accountable organisation reference valid prefixes on activity.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.accountable_org_valid_prefixes()[prefix] == expected[prefix]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 1),
        ),
    ],
)
def test_transaction_extending_org_stats(version, xml, expected):
    """
    Counts of extending organisation references on activity
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.extending_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.extending_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.extending_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.extending_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.extending_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="XI-IATI-1002" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="47122" role="3" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
    ],
)
def test_transaction_extending_org_valid_prefixes(version, xml, expected):
    """
    Counts of extending organisation reference valid prefixes on activity.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.extending_org_valid_prefixes()[prefix] == expected[prefix]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 0, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 0, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="AA-AAA-123456789" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 0, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="BB-BBB-123456789" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 0),
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            (1, 1, 1, 1, 1),
        ),
    ],
)
def test_transaction_implementing_org_stats(version, xml, expected):
    """
    Counts of implementing organisation references on activity
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    assert activity_stats.implementing_org_transaction_stats()["total_orgs"] == expected[0]
    assert activity_stats.implementing_org_transaction_stats()["total_refs"] == expected[1]
    assert activity_stats.implementing_org_transaction_stats()["total_full_refs"] == expected[2]
    assert activity_stats.implementing_org_transaction_stats()["total_notself_refs"] == expected[3]
    assert activity_stats.implementing_org_transaction_stats()["total_valid_refs"] == expected[4]


@pytest.mark.parametrize("version", ["2.02", "2.03"])
@pytest.mark.parametrize(
    "xml, expected",
    [
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="NP-COA-370" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"NP-COA": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="XI-IATI-1002" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"XI-IATI": 1},
        ),
        (
            """
        <iati-activity>
            <reporting-org ref="AA-AAA-123456789" />
            <participating-org ref="47122" role="4" />
            <participating-org ref="CC-CCC-123456789" role="1" />
            <participating-org ref="AA-AAA-123456789" role="2" />
            <participating-org ref="AA-AAA-123456789" role="3" />
            <transaction>
                <provider-org ref="AA-AAA-123456789" />
                <receiver-org ref="BB-BBB-123456789" />
            </transaction>
            <transaction>
                <provider-org ref="BB-BBB-123456789" />
                <receiver-org ref="AA-AAA-123456789" />
            </transaction>
        </iati-activity>
    """,
            {"47122": 1},
        ),
    ],
)
def test_transaction_implementing_org_valid_prefixes(version, xml, expected):
    """
    Counts of implementing organisation reference valid prefixes on activity.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml)

    for prefix in expected:
        assert activity_stats.implementing_org_valid_prefixes()[prefix] == expected[prefix]
