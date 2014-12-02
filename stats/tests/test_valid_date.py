from stats.dashboard import valid_date
from lxml import etree

def test_valid_date():
    assert not valid_date(etree.XML('<activity-date iso-date=""/>'))
    assert valid_date(etree.XML('<activity-date iso-date="2014-01-01"/>'))
    assert valid_date(etree.XML('<activity-date iso-date="2014-01-01" attribute="1"><someelement/></activity-date>'))

    assert not valid_date(etree.XML('<transaction-date iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<transaction-date iso-date="2014-01-01"/>'))

    assert not valid_date(etree.XML('<value value-date="2014-0101"/>'))
    assert valid_date(etree.XML('<value value-date="2014-01-01"/>'))

    assert not valid_date(etree.XML('<period-start iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<period-start iso-date="2014-01-01"/>'))
    assert not valid_date(etree.XML('<period-end iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<period-end iso-date="2014-01-01"/>'))

    assert not valid_date(None)
    assert not valid_date(etree.XML('<otherelement/>'))
