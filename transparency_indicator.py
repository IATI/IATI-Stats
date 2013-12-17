from stats import returns_int, returns_intdict
from decimal import Decimal
from collections import defaultdict
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

def budget_year(budget):
    start = iso_date(budget.find('period-start'))
    end = iso_date(budget.find('period-end'))

    if start and end:
        if (end-start).days < 370:
            if end.month > 7:
                return end.year
            else:
                return end.year - 1
        else:
            return None
    else:
        return None


class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class GenericStats(object):
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

class ActivityStats(GenericStats):
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
        elements = {
            1:  'reporting-org',
            2:  'iati-identifier',
            3:  'other-identifier',
            4:  'title',
            6:  'description',
            8:  'activity-status',
            9:  self._start_date,
            10: self._end_date,
            11: 'contact-info',
            12: 'participating-org[@role="Funding"]',
            13: 'participating-org[@role="Extending"]',
            14: 'participating-org[@role="Implementing"]',
            15: 'participating-org[@role="Accountable"]',
            16: 'recipient-country|recipient-region',
            17: 'location',
            18: lambda: None,
            20: 'policy-marker',
            21: 'collaboration-type',
            22: 'default-flow-type|transaction/flow-type',
            23: 'default-finance-type|transaction/finance-type',
            24: 'default-aid-type|transaction/aid-type',
            25: 'default-tied-status|transaction/tied-status',
            26: 'budget',
            27: 'planned-disbursement',
            28: 'capital-spend',
            29: 'country-budget-items',
            30: 'transaction/transaction-type[@code="C"]',
            31: 'transaction/transaction-type[@code="D" or @code="E"]',
            32: 'transaction/transaction-type[@code="IF"]',
            33: 'transaction[starts-with(finance-type, "4") and string-length(finance-type) = 3]' #lambda: self.element.xpath('transaction/finance-type')self.element.xpath('transaction/transaction-type[@code="IR" or @code="LR"]'),
            }
        def test_exists(element):
            if callable(element):
                if element() is None: return 0
                else: return 1
            else:
                if len(self.element.xpath(element)) >=1: return 1
                else: return 0
        return dict((str(n).zfill(2), test_exists(e)) for n,e in elements.items())
        

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


    @returns_int
    def coverage_numberator(self):
        start_date = datetime.date(2012,1,1)
        end_date = datetime.date(2013,1,1)
        transactions = filter(self._cpa, self.element.findall('transaction'))
        return sum([ Decimal(x.find('value').text) for x in transactions if x.find('transaction-type').attrib.get('code') in ['D','E']  and iso_date(x.find('transaction-date')) >= start_date and iso_date(x.find('transaction-date')) < end_date ])

    @returns_intdict
    def forward_looking_activity(self):
        budget = self.element.find('budget')
        if budget is not None:
            return {budget_year(budget):self._transaction_to_dollars(budget, datetime.date.today())}
        planned_disbursement = self.element.find('planned-disbursement')
        if planned_disbursement is not None:
            return {budget_year(planned_disbursement):self._transaction_to_dollars(planned_disbursement, datetime.date.today())}


class OrganisationFileStats(object):
    pass

class OrganisationStats(GenericStats):
    blank = False

    @returns_intdict
    def forward_looking_aggregate(self):
        out = defaultdict(Decimal)
        budgets = self.element.findall('recipient-country-budget')
        for budget in budgets:
            out[budget_year(budget)] = self._transaction_to_dollars(budget, datetime.date.today())
        return out

