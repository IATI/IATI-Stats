from lxml import etree
import datetime
from collections import defaultdict
from decimal import Decimal
import decimal
from exchange_rates import toUSD

def returns_intdict(f):
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(int)
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_int(f):
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return 0
        else:
            out = f(self, *args, **kwargs)
            if out is None: return 0
            else: return out
    return wrapper

def no_aggregation(f):
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return None
        else: return f(self, *args, **kwargs)
    return wrapper

class ActivityStats(object):
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    def __init__(self, activity=None, blank=False):
        self.activity = activity
        self.blank = blank

    @no_aggregation
    def iati_identifier(self):
        try:
            return self.activity.find('iati-identifier').text
        except AttributeError:
            return None

    @returns_int
    def activities(self):
        return 1

    @returns_intdict
    def currencies(self):
        currencies = [ x.find('value').get('currency') for x in self.activity.findall('transaction') if x.find('value') is not None ]
        currencies = [ c if c else self.activity.get('default-currency') for c in currencies ]
        return dict( (c,1) for c in currencies )
        

    def __get_actual_start_year(self):
        activity_date = self.activity.find("activity-date[@type='start-actual']")
        if activity_date is not None and activity_date.get('iso-date'):
            try:
                date = datetime.datetime.strptime(activity_date.get('iso-date').strip('Z'), "%Y-%m-%d")
                return int(date.year)
            except ValueError, e:
                print unicode(e)+self.context

    @returns_intdict
    def activities_per_year(self):
        return {self.__get_actual_start_year():1}

    def __create_decimal(self, s):
        if self.strict:
            return Decimal(s)
        else:
            return Decimal(s.replace(',', '').replace(' ', ''))

    def __value_to_dollars(self, value):
        try:
            currency = value.get('currency') or self.activity.get('default-currency')
            if currency == 'USD': return self.__create_decimal(value.text)

            year = datetime.datetime.strptime(value.get('value-date').strip('Z'), "%Y-%m-%d").year
            if year == 2013: year = 2012
            return toUSD(value=self.__create_decimal(value.text),
                         currency=currency,
                         year=year)
        # Should we allow commas
        except Exception, e:
            print unicode(e)+self.context
            return Decimal(0.0)
        
    def __spend(self):
        values = [ x.find('value') for x in self.activity.findall('transaction') if x.find('transaction-type') is not None and x.find('transaction-type').get('code') in ['D','E'] ]
        return sum(map(self.__value_to_dollars, values))

    @returns_intdict
    def spend_per_year(self):
        return {self.__get_actual_start_year():self.__spend()}
    
    @returns_intdict
    def activities_per_country(self):
        if self.__get_actual_start_year() >= 2010:
            countries = self.activity.findall('recipient-country')
            regions = self.activity.findall('recipient-region')
            if countries is not None:
                return dict((country.get('code'),1) for country in countries)
            elif regions is not None:
                return dict((region.get('code'),1) for region in regions)

    @returns_int
    def activities_no_country(self):
        if len(self.activities_per_country()) == 0:
            return 1

    @returns_intdict
    def spend_per_country(self):
        if self.__get_actual_start_year() >= 2010:
            country = self.activity.find('recipient-country')
            region = self.activity.find('recipient-region')
            if country is not None:
                return {country.get('code'):self.__spend()}
            elif region is not None:
                return {region.get('code'):self.__spend()}
    
    @returns_intdict
    def spend_per_organisation_type(self):
        organisationType = self.activity.find('reporting-org')
        if organisationType is not None:
            return {organisationType.get('type'):self.__spend()}
       
    

class PublisherStats(object):
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    def __init__(self, aggregated=None, blank=False):
        self.aggregated = aggregated
        self.blank = blank

    @returns_intdict
    def publishers_per_country(self):
        countries = self.aggregated['activities_per_country'].keys()
        return dict((c,1) for c in countries)

    @returns_int
    def publishers(self):
        return 1
