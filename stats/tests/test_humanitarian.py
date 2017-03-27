# coding=utf-8

from lxml import etree
import pytest

from stats.dashboard import ActivityStats

class MockActivityStats(ActivityStats):
    def __init__(self, major_version):
        self.major_version = major_version
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_attrib_true(major_version, hum_attrib_val):
    """
    Detect an activity to be humanitarian using @humanitarian values that evaluate to true.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('hum_attrib_val', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_attrib_false(major_version, hum_attrib_val):
    """
    Detect an activity to not be humanitarian using @humanitarian values that evaluate to false.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', [72010, 74010])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
        	<sector code="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity>
        	<sector code="{0}" vocabulary="1" />
        </iati-activity>
    '''])
def test_humanitarian_sector_true(major_version, sector, xml):
    """
    Detects an activity to be humanitarian using sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', [-89, 'not_a_code'])
def test_humanitarian_sector_false_bad_codes(major_version, sector):
    """
    Detects an activity not to be humanitarian using sector codes that are not considered to relate to humanitarian.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
        	<sector code="{0}" />
        </iati-activity>
    '''.format(sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', [72010, 74010])
def test_humanitarian_sector_false_bad_vocab(major_version, sector):
    """
    Detects an activity not to be humanitarian due to specification of an incorrect vocabulary despite @code values that are considered to relate to humanitarian by default.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
        	<sector code="{0}" vocabulary="99" />
        </iati-activity>
    '''.format(sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0
