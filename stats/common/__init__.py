import re
import datetime

def debug(stats, error):
    """ prints debugging information for a given stats object and error """
    print unicode(error)+stats.context 

xsDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')

def iso_date_match(raw_date):
    """Return a datetime object for a given textual ISO date string

    Keyword arguments:
    raw_date -- an ISO date as text
    """
    if raw_date:
        m1 = xsDateRegex.match(raw_date)
        if m1:
            return datetime.date(*map(int, m1.groups()))
        else:
            return None

def iso_date(element):
    """Return a datetime object for a given XML element either i) an 'iso-date' attribute or ii) an iso date as text

    Keyword arguments:
    element -- an XML element containing either i) an 'iso-date' attribute or ii) an iso date as text
    """
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

def budget_year(budget):
    start = iso_date(budget.find('period-start'))
    end = iso_date(budget.find('period-end'))

    if start and end:
        if (end-start).days <= 370:
            if end.month >= 7:
                return end.year
            else:
                return end.year - 1
        else:
            return None
    else:
        return None

def planned_disbursement_year(planned_disbursement):
    start = iso_date(planned_disbursement.find('period-start'))
    end = iso_date(planned_disbursement.find('period-end'))

    if start and end:
        return budget_year(planned_disbursement)
    elif start:
        return start.year
    else:
        return None

