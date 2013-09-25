from lxml import etree
import datetime
from collections import defaultdict
from decimal import Decimal
import decimal

def returns_intdict(f):
    def wrapper(self, *args, **kwargs):
        if self.activity == None:
            return defaultdict(int)
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def no_aggregation(f):
    def wrapper(self, *args, **kwargs):
        if self.activity == None:
            return None
        else: return f(self, *args, **kwargs)
    return wrapper

class ActivityStats(object):
    context = ''

    def __init__(self, activity=None):
        self.activity = activity

    @no_aggregation
    def iati_identifier(self):
        try:
            return self.activity.find('iati-identifier').text
        except AttributeError:
            return None

    def activities(self):
        if self.activity is None: return 0
        else: return 1

    @returns_intdict
    def currencies(self):
        currencies = [ x.find('value').get('currency') for x in self.activity.findall('transaction') if x.find('value') is not None ]
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

    def __value_to_dollars(self, value):
        # FIXME
        try:
            return Decimal(value.text)
        # Should we allow commas
        except decimal.InvalidOperation, e:
            print unicode(e)+self.context
        
    def __spend(self):
        values = [ x.find('value') for x in self.activity.findall('transaction') if x.find('transaction-type') is not None and x.find('transaction-type').get('code') in ['D','E'] ]
        map(self.__value_to_dollars, values)
        return 1

    @returns_intdict
    def spend_per_year(self):
        return {self.__get_actual_start_year():self.__spend()}
    
    @returns_intdict
    def activities_per_country(self):
        countries = self.activity.findall('recipient-country')
        regions = self.activity.findall('recipient-region')
        if countries is not None:
            return dict((country.get('code'),1) for country in countries)
        elif regions is not None:
            return dict((region.get('code'),1) for region in regions)

    @returns_intdict
    def spend_per_country(self):
        country = self.activity.find('recipient-country')
        region = self.activity.find('recipient-region')
        if country is not None:
            return {country.get('code'):self.__spend()}
        elif region is not None:
            return {region.get('code'):self.__spend()}
    
