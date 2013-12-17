from stats import returns_int, returns_intdict
from decimal import Decimal
import re, datetime

xsDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')
def iso_date(element):
    if element.attrib.get('iso-date'):
        m1 = xsDateRegex.match(element.attrib.get('iso-date'))
        return datetime.date(*map(int, m1.groups()))
    else:
        return None

def memoize(f):
    def wrapper(self):
        if not hasattr(self, 'cache'):
            self.cache = {}
        if not f.__name__ in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__]
    return wrapper

def aggregate_largest(f):
    class LargestAggregator(object):
        value = 0
        def __add__(self, x):
            x = int(x)
            if x > self.value:
                self.value = x
            return self
        def __int__(self):
            return self.value
    def wrapper(self, *args, **kwargs): 
        if self.blank:
            return LargestAggregator()
        else:
            return f(self, *args, **kwargs)
    return wrapper


class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    def _oda_test(self, transaction):
        default_flow_type = self.element.xpath('default-flow-type/@code')
        flow_type = transaction.xpath('flow-type/@code')
        return '10' in default_flow_type or '10' in flow_type or len(default_flow_type) == 0 or len(flow_type) == 0

    @memoize
    def _oda_transactions(self):
        return filter(self._oda_test, self.element.findall('transaction'))

    @returns_int
    def activities(self):
        return 1

    def _transaction_to_dollars(self, transaction, start_date):
        conversion_lookup = {
            'AUD':	('0.966',	'1.092'),
            'CAD':	('0.999',	'1.039'),
            'CLP':	('485.984',	'506.922'),
            'CZK':	('19.538',	'19.519'),
            'DKK':	('5.79',	'5.631'),
            'JPY':	('79.814',	'98.923'),
            'CHF':	('0.938',	'0.932'),
            'GBP':	('0.631',	'0.645'),
            'EUR':	('0.778',	'0.755'),
            'XDR':	('0.632',	'0.66'),
            'ZAR':	('8.21',	'9.991') }
        value = transaction.find('value')
        currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
        conversion = conversion_lookup[currency][0 if start_date == datetime.date(2012,1,1) else 1]
        return Decimal(value.text) * Decimal(conversion)

    def _coverage(self, start_date, end_date):
        return sum([ self._transaction_to_dollars(x, start_date) for x in self._oda_transactions() if x.find('transaction-type').attrib.get('code') in ['D','E']  and iso_date(x.find('transaction-date')) >= start_date and iso_date(x.find('transaction-date')) < end_date ])
    
    @returns_int
    def coverage_A(self):
        return self._coverage(datetime.date(2012,1,1), datetime.date(2013,1,1))

    @returns_int
    def coverage_B(self):
        return self._coverage(datetime.date(2012,10,1), datetime.date(2013,10,1))

    def timelag(self):
        if self.blank:
            class Aggregator(object):
                value = 0
                def __add__(self, x):
                    x = int(x)
                    if x==3 and self.value==3:
                        self.value = 4
                    elif x > self.value:
                        self.value = x
                    return self
                def __int__(self):
                    return self.value
            return Aggregator()
        else:
            dates = [ iso_date(x.find('transaction-date')) for x in self.element.findall('transaction') ]
            three_months_ago = datetime.date(2013, 9, 1)
            six_months_ago = datetime.date(2013, 6, 1)
            twelve_months_ago = datetime.date(2012, 12, 1)
            if len(filter(lambda x: x>three_months_ago, dates)) >= 2:
                return 4
            elif len(filter(lambda x: x>three_months_ago, dates)) >= 1:
                return 3
            elif len(filter(lambda x: x>six_months_ago, dates)) >= 1:
                return 2
            elif len(filter(lambda x: x>twelve_months_ago, dates)) >= 1:
                return 1
            else:
                return 0

    @memoize
    def _start_date(self):
        try:
            return iso_date(self.element.xpath("activity-date[@type='start-actual']")[0])
        except IndexError:
            try:
                return iso_date(self.element.xpath("activity-date[@type='start-planned']")[0])
            except IndexError:
                return None

    def _end_date(self):
        try:
            return iso_date(self.element.xpath("activity-date[@type='end-actual']")[0])
        except IndexError:
            try:
                return iso_date(self.element.xpath("activity-date[@type='end-planned']")[0])
            except IndexError:
                return None

    @memoize
    def _current_activity(self):
        return (self.element.find('activity-status') is None or self.element.find('activity-status').text != '5') and (not self._end_date() or self._end_date() > datetime.date(2011,12,31))

    @returns_int
    def current_activities(self):
        return 1 if self._current_activity() else 0

    @returns_intdict
    def current_activity_elements(self):
        elements = ['reporting-org','iati-identifier','other-identifier','title','description', 'activity-status']
        return dict((xpath, 1 if len(self.element.xpath(xpath)) >=1 else 0) for xpath in elements)
        

    def _cpa(self, transaction):
        sectors = set() # FIXME
        aid_types = set()
        flow_types = set()
        finance_types = set()
        regions = set()
        e = self.element
        return not(
            len(sectors.intersection(e.xpath('sector/@code'))) > 0 or
            len(aid_types.intersection(e.xpath('default-aid-type/@code'))) > 0 or
            len(aid_types.intersection(transaction.xpath('aid-type/@code'))) > 0 or
            len(flow_types.intersection(e.xpath('default-flow-type/@code'))) > 0 or
            len(flow_types.intersection(transaction.xpath('flow-type/@code'))) > 0 or
            len(finance_types.intersection(e.xpath('default-finance-type/@code'))) > 0 or
            len(finance_types.intersection(transaction.xpath('finance-type/@code'))) > 0 or
            len(finance_types.intersection(transaction.xpath('recipient-region/@code'))) > 0)

        #return not (e.xpath('sector/@code'))

    @returns_int
    def forward_looking(self):
        start_date = datetime.date(2012,1,1)
        end_date = datetime.date(2013,1,1)
        transactions = filter(self._cpa, self.element.findall('transaction'))
        return sum([ Decimal(x.find('value').text) for x in transactions if x.find('transaction-type').attrib.get('code') in ['D','E']  and iso_date(x.find('transaction-date')) >= start_date and iso_date(x.find('transaction-date')) < end_date ])

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
