from stats.dashboard import valid_date, valid_url
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


def test_valid_url():
    assert not valid_url(etree.XML('<document-link/>'))
    assert not valid_url(etree.XML('<document-link url=""/>'))
    #assert not valid_url(etree.XML('<document-link url="http://:notaurl"/>'))
    assert not valid_url(etree.XML('<document-link url="notaurl"/>'))
    assert valid_url(etree.XML('<document-link url="http://example.org/"/>'))

    assert not valid_url(etree.XML('<activity-website/>'))
    assert not valid_url(etree.XML('<activity-website></activity-website>'))
    #assert not valid_url(etree.XML('<activity-website>notaurl</activity-website>'))
    assert not valid_url(etree.XML('<activity-website>http://:notaurl</activity-website>'))
    assert valid_url(etree.XML('<document-link url="http://example.org/"/>'))
