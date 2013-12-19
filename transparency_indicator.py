from stats import returns_int, returns_intdict, returns_dict
from decimal import Decimal
from collections import defaultdict
import re, datetime
import csv 

"""
Errors
InvalidOperation: Invalid literal for Decimal: '5 948.54'
ValueError: day is out of range for month
KeyError: ''
KeyError: 'INR'

"""

reader = csv.reader(open('country_lang_map.csv'), delimiter=';')
country_lang_map = dict((row[0], row[2]) for row in reader)
reader = csv.reader(open('Timeliness_Files_1.2.csv'))
frequency_map = dict((row[0], row[13]) for row in reader)

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
            try:
                x = int(x)
            except TypeError: x = 0
            except ValueError: x = 0
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
    blank = False

    @returns_dict
    def bottom_hierarchy(self):
        h = int(self.aggregated['hierarchy'])
        try:
            out = self.aggregated['by_hierarchy']['' if h==0 else str(h)]
        except KeyError:
            out = {}
        if '(iati-organisation)' in self.aggregated['by_hierarchy']:
            for k,v in self.aggregated['by_hierarchy']['(iati-organisation)'].items():
                if not k in out:
                    out[k] = v
        return out

    @aggregate_largest
    def timelag(self):
        if (
            (1 if self.aggregated['timelag_months']['2-3'] > 0 else 0) +
            (1 if self.aggregated['timelag_months']['1-2'] > 0 else 0) +
            (1 if self.aggregated['timelag_months']['1'] > 0 else 0)
            ) >= 2:
            return 4
        elif self.aggregated['timelag_months']['3'] > 0:
                return 3
        elif self.aggregated['timelag_months']['6'] > 0:
            return 2
        elif self.aggregated['timelag_months']['12'] > 0:
            return 1
        else:
            return 0

    @aggregate_largest
    def frequency(self):
        frenquency_weightings = {
            'Monthly': 4,
            'Quarterly': 3,
            'Six-monthly': 2,
            'Annually': 1,
            'Beyond one year': 0
        }
        return frenquency_weightings[frequency_map[self.folder]]




class ActivityFileStats(object):
    pass

class GenericStats(object):
    def _transaction_to_dollars(self, transaction, start_date):
        conversion_lookup = {
            'USD': (1,1),
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
        return Decimal(value.text) / Decimal(conversion)

class ActivityStats(GenericStats):
    blank = False

    @aggregate_largest
    def hierarchy(self):
        return self.element.attrib.get('hierarchy') or ''

    @returns_intdict
    def hierarchies(self):
        return {self.element.attrib.get('hierarchy'):1}

    def _oda_test(self, transaction):
        default_flow_type = self.element.xpath('default-flow-type/@code')
        flow_type = transaction.xpath('flow-type/@code')
        return '10' in default_flow_type or '10' in flow_type or (len(default_flow_type) == 0 and len(flow_type) == 0)

    @memoize
    def _oda_transactions(self):
        return filter(self._oda_test, self.element.findall('transaction'))

    @returns_int
    def activities(self):
        return 1

    def _coverage_oda(self, start_date, end_date):
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ self._transaction_to_dollars(x, start_date) for x in self._oda_transactions() if x.find('transaction-type').attrib.get('code') in ['D','E']  and date_conditions(transaction_date(x)) ])
    
    def _coverage_all(self, start_date, end_date):
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ self._transaction_to_dollars(x, start_date) for x in self.element.findall('transaction') if x.find('transaction-type').attrib.get('code') in ['D','E']  and date_conditions(transaction_date(x)) ])

    @returns_int
    def coverage_A(self):
        return self._coverage_oda(datetime.date(2012,1,1), datetime.date(2013,1,1))

    @returns_int
    def coverage_B(self):
        return self._coverage_oda(datetime.date(2012,10,1), datetime.date(2013,10,1))

    @returns_int
    def coverage_C(self):
        return self._coverage_all(datetime.date(2012,1,1), datetime.date(2013,1,1))

    @returns_int
    def coverage_D(self):
        return self._coverage_all(datetime.date(2012,10,1), datetime.date(2013,10,1))

    @returns_intdict
    def timelag_months(self):
        one_month_ago = datetime.date(2013, 11, 1)
        two_months_ago = datetime.date(2013, 11, 1)
        three_months_ago = datetime.date(2013, 9, 1)
        six_months_ago = datetime.date(2013, 6, 1)
        twelve_months_ago = datetime.date(2012, 12, 1)
        dates = [ transaction_date(x) for x in self.element.findall('transaction') ]
        return {
            '1':   len(filter(lambda x: x and x>one_month_ago, dates)),
            '1-2': len(filter(lambda x: x and x>two_months_ago and x<one_month_ago, dates)),
            '2-3': len(filter(lambda x: x and x>three_months_ago and x<two_months_ago, dates)),
            '6':   len(filter(lambda x: x and x>six_months_ago, dates)),
            '12':  len(filter(lambda x: x and x>twelve_months_ago, dates))
        }

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
        try:
            lang = country_lang_map[self.element.find('recipient-country').attrib.get('code')]
        except AttributeError: lang = None
        except KeyError: lang = None
        if lang == 'other': lang = None

        elements = {
            1:  'reporting-org',
            2:  'iati-identifier',
            3:  'other-identifier',
            4:  'title',
            5:  'title[@xml:lang="en" or ../@xml:lang="en"]'.format(lang) if lang else 'title',
            6:  'description',
            7:  'description[@xml:lang="en" or ../@xml:lang="en"]'.format(lang) if lang else 'description',
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
            18: 'sector[@vocabulary="DAC" or @vocabulary="DAC-3" or @vocabulary="" or not(@vocabulary)]',
            19: 'sector[@vocabulary!="DAC" and @vocabulary!="DAC-3" and @vocabulary!=""]',
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
            33: lambda: self.element.xpath('transaction/transaction-type[@code="IR" or @code="LR"]') if len(self.element.xpath('transaction[starts-with(finance-type/@code, "4") and string-length(finance-type/@code) = 3]')) or self.element.xpath('starts-with(default-finance-type/@code, "4") and string-length(default-finance-type/@code) = 3') else True,
            34: 'document-link',
            35: 'activity-website',
            36: 'related-activity',
            37: 'conditions/@attached',
            38: 'conditions/condition',
            39: 'result'
            }
        def test_exists(element):
            if callable(element):
                if element() is None: return 0
                else: return 1
            else:
                if len(self.element.xpath(element)) >=1: return 1
                else: return 0
        return dict((str(n).zfill(2), test_exists(e)) for n,e in elements.items())
        

    def _cpa(self, transaction=None):
        sectors = set() # FIXME
        aid_types = set()
        flow_types = set()
        finance_types = set()
        regions = set()
        e = self.element
        return not(
            len(sectors.intersection(e.xpath('sector/@code'))) > 0 or
            len(aid_types.intersection(e.xpath('default-aid-type/@code'))) > 0 or
            len(flow_types.intersection(e.xpath('default-flow-type/@code'))) > 0 or
            len(finance_types.intersection(e.xpath('default-finance-type/@code'))) > 0 or
            len(finance_types.intersection(e.xpath('recipient-region/@code'))) > 0 or
            (transaction is not None and
                (len(aid_types.intersection(transaction.xpath('aid-type/@code'))) > 0 or
                len(flow_types.intersection(transaction.xpath('flow-type/@code'))) > 0 or
                len(finance_types.intersection(transaction.xpath('finance-type/@code'))) > 0)))


    @returns_int
    def coverage_numerator(self):
        start_date = datetime.date(2012,1,1)
        end_date = datetime.date(2013,1,1)
        transactions = filter(self._cpa, self.element.findall('transaction'))
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ Decimal(x.find('value').text) for x in transactions if x.find('transaction-type').attrib.get('code') in ['D','E']  and date_conditions(transaction_date(x)) ])

    @returns_intdict
    def forward_looking_activity(self):
        if not self._cpa:
            return {}
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

    @aggregate_largest
    def hierarchy(self):
        return '(iati-organisation)'

    @returns_intdict
    def forward_looking_aggregate(self):
        out = defaultdict(Decimal)
        budgets = self.element.findall('recipient-country-budget')
        for budget in budgets:
            out[budget_year(budget)] = self._transaction_to_dollars(budget, datetime.date.today())
        return out

