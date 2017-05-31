# coding=utf-8
import random
from lxml import etree
import pytest

from stats.dashboard import ActivityStats

class MockActivityStats(ActivityStats):
    def __init__(self, major_version):
        self.major_version = major_version
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

    def _version(self):
        return self._major_version() + '.02'

HUMANITARIAN_SECTOR_CODES_5_DIGITS = [72010, 72040, 72050, 73010, 74010]
HUMANITARIAN_SECTOR_CODES_3_DIGITS = [720, 730, 740]

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
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
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
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
        	<sector code="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity>
        	<sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_true(major_version, sector, xml):
    """
    Detects an activity to be humanitarian using sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, activity_stats._dac_5_code()))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_true_3_digit(major_version, sector, xml):
    """
    Detects an activity to be humanitarian using 3-digit sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, activity_stats._dac_3_code()))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', [-89, 'not_a_code', HUMANITARIAN_SECTOR_CODES_5_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_5_DIGITS[-1]-1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[-1]-1])
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
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', [2, 99, 'DAC-3'])
def test_humanitarian_sector_false_bad_vocab(major_version, sector, vocab):
    """
    Detects an activity not to be humanitarian due to specification of an incorrect vocabulary despite @code values that are considered to relate to humanitarian by default.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
        	<sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS)
@pytest.mark.parametrize('vocab', [1, 99, 'DAC'])
def test_humanitarian_sector_false_bad_vocab_3_digit(major_version, sector, vocab):
    """
    Detects an activity to be humanitarian using 3-digit sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS + HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', ['1', '2', ''])
def test_humanitarian_sector_false_bad_major_version_1(sector, vocab, major_version='1'):
    """
    Detects an activity not to be humanitarian due to specification of a vocabulary that is valid at an alternative major version of the Standard.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS + HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', ['DAC', 'DAC-3', ''])
def test_humanitarian_sector_false_bad_major_version_2(sector, vocab, major_version='2'):
    """
    Detects an activity not to be humanitarian due to specification of a vocabulary that is valid at an alternative major version of the Standard.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS + [89, 'not_a_code'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_attrib_true_sector_anything(major_version, sector, hum_attrib_val):
    """
    Detect an activity to be humanitarian using @humanitarian values that evaluate to true in combination with sector codes.

    Both valid and invalid sector codes are tested because everything should still evaluate the same, given that @humanitarian is true.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        	<sector code="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('hum_attrib_val', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_attrib_false_sector_true(major_version, sector, hum_attrib_val):
    """
    Detect an activity to be humanitarian using sector codes that are deemed to be humanitarian, in combination with a @humanitarian value which evaluates to false.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        	<sector code="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('sector', [-89, 'not_a_code'])
@pytest.mark.parametrize('hum_attrib_val', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_attrib_false_sector_false(major_version, sector, hum_attrib_val):
    """
    Detect an activity not to be humanitarian using sector codes that are deemed not to be humanitarian, in combination with a @humanitarian value which evaluates to false.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        	<sector code="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_attrib_false_sector_false(major_version, hum_attrib_val):
    """
    Detect an activity not to be humanitarian at version 1 of the standard when a @humanitarian value that evaluates to true is present.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_elements_valid_version(version, hum_attrib_val):
    """
    Tests that humanitarian elements are detected at supported versions.
    """

    activity_stats = ActivityStats()

    tree = etree.fromstring('''
        <iati-activities version="{0}">
           <iati-activity humanitarian="{1}">
              <humanitarian-scope type="" code="" />
           </iati-activity>
        </iati-activities>
    '''.format(version, hum_attrib_val))

    activity_stats.element = tree.getchildren()[0]

    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 1
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_elements_invalid_version(version, hum_attrib_val):
    """
    Tests that humanitarian elements are detected at supported versions.
    """

    activity_stats = ActivityStats()

    tree = etree.fromstring('''
        <iati-activities version="{0}">
           <iati-activity humanitarian="{1}">
              <humanitarian-scope type="" code="" />
           </iati-activity>
        </iati-activities>
    '''.format(version, hum_attrib_val))

    activity_stats.element = tree.getchildren()[0]

    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
def test_humanitarian_scope_valid(major_version):
    """
    Detect that an activity contains a humanitarian-scope element and required attributes.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <humanitarian-scope type="" code="" />
        </iati-activity>
    ''')
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 1


@pytest.mark.parametrize('major_version', ['2'])
def test_humanitarian_scope_invalid(major_version):
    """
    Detect that an activity contains a humanitarian-scope element without required attributes.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <humanitarian-scope />
        </iati-activity>
    ''')
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0


@pytest.mark.parametrize('major_version', ['2'])
def test_humanitarian_clusters_valid(major_version):
    """
    Detect that an activity contains a sector defined by the 'Humanitarian Global Clusters' sector vocabulary.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <sector vocabulary="10" />
        </iati-activity>
    ''')
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 1


@pytest.mark.parametrize('major_version', ['1'])
def test_humanitarian_clusters_version_1(major_version):
    """
    Detect that a version 1 activity containing a sector defined by the 'Humanitarian Global Clusters' sector vocabulary is not detected.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <sector vocabulary="10" />
        </iati-activity>
    ''')
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('sector_vocabulary_code', ['', '1', 'internal vocabulary'])
def test_humanitarian_clusters_invalid(major_version, sector_vocabulary_code):
    """
    Detect that an activity does not contain a sector defined by the 'Humanitarian Global Clusters' sector vocabulary.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <sector vocabulary="{0}" />
        </iati-activity>
    '''.format(sector_vocabulary_code))
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0

