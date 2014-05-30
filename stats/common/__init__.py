import re
import datetime

def debug(stats, error):
    """ prints debugging information for a given stats object and error """
    print unicode(error)+stats.context 

xsDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')
def iso_date_match(raw_date):
    if raw_date:
        m1 = xsDateRegex.match(raw_date)
        if m1:
            return datetime.date(*map(int, m1.groups()))
        else:
            return None

def iso_date(element):
    if element is None:
        return None
    raw_date = element.attrib.get('iso-date')
    if not raw_date:
        raw_date = element.text
    return iso_date_match(raw_date)

def transaction_date(transaction):
    if transaction.find('transaction-date') is not None:
        return iso_date(transaction.find('transaction-date'))
    elif transaction.find('value') is not None:
        return iso_date_match(transaction.find('value').attrib.get('value-date'))

