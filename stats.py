"""
This is the default file called by loop.py. 
You can choose a different set of tests by running loop.py with the ``--stats-module`` flag  
"""
from lxml import etree
import datetime, dateutil.parser, dateutil.tz
from collections import defaultdict
from decimal import Decimal
import decimal
from exchange_rates import toUSD
import os, re
import subprocess

## In order to test whether or not correct codelist values are being used in the data 
## we need to pull in data about how codelists map to elements
codelist_mapping_xml = etree.parse('mapping.xml')
codelist_mappings = [ x.text for x in codelist_mapping_xml.xpath('mapping/path') ]
codelist_mappings = [ re.sub('^\/\/iati-activity', './',path) for path in codelist_mappings]
codelist_mappings = [ re.sub('^\/\/', './/', path) for path in codelist_mappings ]

## I have no idea what this does! DC
def memoize(f):
    def wrapper(self):
        if not hasattr(self, 'cache'):
            self.cache = {}
        if not f.__name__ in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__]
    return wrapper

def debug(stats, error):
    """ prints debugging information for a given stats object and error """
    print unicode(error)+stats.context 

def element_to_count_dict(element, path, count_dict):
    """
    Converts an element and it's children to a dictionary containing the
    count for each xpath.
    
    """
    count_dict[path] = 1
    for child in element:
        if type(child.tag) == str:
            element_to_count_dict(child, path+'/'+child.tag, count_dict)
    for attribute in element.attrib:
        count_dict[path+'/@'+attribute] = 1
    return count_dict


## Decorators that modify return when self.blank = True etc.
def returns_numberdictdict(f):
    """ Dectorator for dictionaries of integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(lambda: defaultdict(int))
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_numberdict(f):
    """ Dectorator for dictionaries of integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(int)
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_dict(f):
    """ Dectorator for dictionaries. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return {}
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper


def returns_number(f):
    """ Decorator for integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return 0
        else:
            out = f(self, *args, **kwargs)
            if out is None: return 0
            else: return out
    return wrapper

def no_aggregation(f):
    """ Decorator that perevents aggreagation. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return None
        else: return f(self, *args, **kwargs)
    return wrapper


def returns_date(f):
    class LargestDateAggregator(object):
        value = datetime.datetime(1900,1,1, tzinfo=dateutil.tz.tzutc())
        def __add__(self, x):
            if type(x) == datetime.datetime:
                pass
            elif type(x) == LargestDateAggregator:
                x = x.value
            else:
                x = dateutil.parser.parse(x)
            if x > self.value:
                self.value = x
            return self
    def __int__(self):
        return self.value
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return LargestDateAggregator()
        else:
            return f(self, *args, **kwargs)
    return wrapper

#Deals with elements that are in both organisation and activity files
class CommonSharedElements(object):
    blank = False
    
    @no_aggregation
    def iati_identifier(self):
        try:
            return self.element.find('iati-identifier').text
        except AttributeError:
            return None

    @returns_numberdict
    def reporting_orgs(self):
        return {self.element.find('reporting-org').attrib.get('ref'):1}

class ActivityStats(CommonSharedElements):
    """ Stats calculated on a single iati-activity. """
    element = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @returns_numberdict
    def iati_identifiers(self):
        return {self.element.find('iati-identifier').text:1}


    @returns_number
    def activities(self):
        return 1

    @returns_numberdict
    def reporting_orgs(self):
        return {self.element.find('reporting-org').attrib.get('ref'):1}

    @returns_numberdict
    def element_versions(self):
        return { self.element.attrib.get('version'): 1 }

    @returns_numberdict
    def currencies(self):
        currencies = [ x.find('value').get('currency') for x in self.element.findall('transaction') if x.find('value') is not None ]
        currencies = [ c if c else self.element.get('default-currency') for c in currencies ]
        return dict( (c,1) for c in currencies )
        

    def __get_start_year(self):
        activity_date = self.element.find("activity-date[@type='start-actual']")
        if activity_date is None: activity_date = self.element.find("activity-date[@type='start-planned']")
        if activity_date is not None and activity_date.get('iso-date'):
            try:
                date = datetime.datetime.strptime(activity_date.get('iso-date').strip('Z'), "%Y-%m-%d")
                return int(date.year)
            except ValueError, e:
                debug(self, e)
            except AttributeError, e:
                debug(self, e)

    @returns_numberdict
    def activities_per_year(self):
        return {self.__get_start_year():1}

    def __create_decimal(self, s):
        if self.strict:
            return Decimal(s)
        else:
            return Decimal(s.replace(',', '').replace(' ', ''))

    def __value_to_dollars(self, transaction):
        try:
            value = transaction.find('value')
            currency = value.get('currency') or self.element.get('default-currency')
            if currency == 'USD': return self.__create_decimal(value.text)
            try:
                year = datetime.datetime.strptime(value.get('value-date').strip('Z'), "%Y-%m-%d").year
            except AttributeError:
                try:
                    if self.strict: raise AttributeError
                    year = datetime.datetime.strptime(transaction.find('transaction-date').get('iso-date').strip('Z'), "%Y-%m-%d").year
                except AttributeError:
                    debug(self, 'Transaction without date information')
                    return Decimal(0.0)
            if year == 2013: year = 2012
            return toUSD(value=self.__create_decimal(value.text),
                         currency=currency,
                         year=year)
        except Exception, e:
            debug(self, e)
            return Decimal(0.0)
    
    @returns_number
    def spend(self):
        """ Spend is defined as the sum of all transactions that are Disbursements (D) or Expenditure (E) """
        transactions = [ x for x in self.element.findall('transaction') if x.find('transaction-type') is not None and x.find('transaction-type').get('code') in ['D','E'] ]
        return sum(map(self.__value_to_dollars, transactions))

    @returns_numberdict
    def spend_per_year(self):
        return {self.__get_start_year():self.spend()}
    
    @returns_numberdict
    def activities_per_country(self):
        """ Legacy code according to @bjwebb this is not used now """
        if self.__get_start_year() >= 2010:
            countries = self.element.findall('recipient-country')
            regions = self.element.findall('recipient-region')
            if countries is not None:
                return dict((country.get('code'),1) for country in countries)
            elif regions is not None:
                return dict((region.get('code'),1) for region in regions)

    @returns_number
    def activities_no_country(self):
        if len(self.activities_per_country()) == 0:
            return 1

    @returns_numberdict
    def spend_per_country(self):
        if self.__get_start_year() >= 2010:
            country = self.element.find('recipient-country')
            region = self.element.find('recipient-region')
            if country is not None and country.get('code'):
                return {country.get('code'):self.spend()}
            elif region is not None and region.get('code'):
                return {region.get('code'):self.spend()}
            else:
                return {None:self.spend()}
        else:
            return {'pre2010':self.spend()}
    
    @returns_numberdict
    def spend_per_organisation_type(self):
        try:
            transactions = [ x for x in self.element.findall('transaction') if
                x.find('transaction-type') is not None and
                x.find('transaction-type').get('code') in ['D','E'] and
                x.find('transaction-date') is not None and
                datetime.datetime.strptime(x.find('transaction-date').get('iso-date').strip('Z'), "%Y-%m-%d") > datetime.datetime(2012, 6, 30) ]
            spend = sum(map(self.__value_to_dollars, transactions))
            organisationType = self.element.find('reporting-org')
            if organisationType is not None:
                return {organisationType.get('type'):spend}
        except ValueError:
            pass
        except AttributeError, e:
            pass

    @returns_numberdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-activity', {})

    @returns_numberdictdict
    def codelist_values(self):
        out = defaultdict(lambda: defaultdict(int))
        for path in codelist_mappings:
            for value in self.element.xpath(path):
                out[path][value] += 1
        return out 

    @returns_numberdictdict
    def boolean_values(self):
        out = defaultdict(lambda: defaultdict(int))
        for path in [
                'result/indicator/@ascending',
                'result/@aggregation-status',
                'conditions/@attached',
                'crs-add/aidtype-flag/@significance',
                'fss/@priority'
                ]:
            for value in self.element.xpath(path):
                out[path][value] += 1
        return out 



import json
ckan = json.load(open('ckan.json'))
publisher_re = re.compile('(.*)\-[^\-]')

class GenericFileStats(object):
    blank = False

    @returns_numberdict
    def versions(self):
        return { self.root.attrib.get('version'): 1 }

    @returns_numberdict
    def version_mismatch(self):
        file_version = self.root.attrib.get('version')
        element_versions = self.root.xpath('//iati-activity/@version')
        element_versions = list(set(element_versions))
        return {
            'true' if ( file_version is not None and len(element_versions) and [file_version] != element_versions ) else 'false'
            :1}

    @returns_numberdict
    def validation(self):
        version = self.root.attrib.get('version')
        if version in [None, '1', '1.0', '1.00']: version = '1.01' 
        try:
            with open('schemas/{0}/{1}'.format(version, self.schema_name)) as f:
                xmlschema_doc = etree.parse(f)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                if xmlschema.validate(self.doc):
                    return {'pass':1}
                else:
                    return {'fail':1}
        except IOError:
            debug(self, 'Unsupported version \'{0}\''.format(version))
            return {'fail':1} 

    @returns_numberdict
    def wrong_roots(self):
        tag = self.root.tag
        try:
            ckan_type = ckan[publisher_re.match(self.fname).group(1)][self.fname]['extras']['filetype']
            if not ((tag == 'iati-organisations' and ckan_type == '"organisation"') or (tag == 'iati-activities' and ckan_type == '"activity"')):
                return {tag:1}
        except KeyError:
            pass

    @returns_number
    def file_size(self):
        return os.stat(self.inputfile).st_size

    @returns_numberdict
    def file_size_bins(self):
        file_size = os.stat(self.inputfile).st_size
        if file_size < 1*1024*1024:
            return {'<1MB': 1}
        elif file_size < 5*1024*1024:
            return {'1-5MB': 1}
        elif file_size < 10*1024*1024:
            return {'5-10MB': 1}
        elif file_size < 20*1024*1024:
            return {'10-20MB': 1}
        else:
            return {'>20MB': 1}

    @returns_date
    @memoize
    def updated(self):
        if self.inputfile.startswith('data/'):
            cwd = os.getcwd()
            os.chdir('data')
            out = subprocess.check_output(['git', 'log', '-1', '--format="%ai"', '--', self.inputfile[5:]]).strip('"\n')
            os.chdir(cwd)
            return out

    @returns_numberdict
    def updated_dates(self):
        return {self.updated().split(' ')[0]:1}
        


    

class ActivityFileStats(GenericFileStats):
    """ Stats calculated for an IATI Activity XML file. """
    doc = None
    root = None
    schema_name = 'iati-activities-schema.xsd'

    @returns_number
    def empty(self):
        return 0

    @returns_number
    def invalidxml(self):
        # Must be valid XML to have loaded this function
        return 0

    def nonstandardroots(self):
        return 0

    @returns_number
    def activity_files(self):
        return 1



class PublisherStats(object):
    """ Stats calculated for an IATI Publisher (directory in the data directory). """
    aggregated = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @returns_numberdict
    def publishers_per_country(self):
        countries = self.aggregated['activities_per_country'].keys()
        return dict((c,1) for c in countries)

    @returns_numberdict
    def publishers_per_organisation_type(self):
        organisation_types = self.aggregated['spend_per_organisation_type'].keys()
        return dict((o,1) for o in organisation_types)

    @returns_numberdict
    def publishers_per_version(self):
        versions = self.aggregated['versions'].keys()
        return dict((v,1) for v in versions)

    @returns_number
    def publishers(self):
        return 1

    @returns_numberdict
    def publishers_validation(self):
        if 'fail' in self.aggregated['validation']:
            return {'fail':1}
        else:
            return {'pass':1}

    @returns_numberdict
    def publisher_has_org_file(self):
        if 'organisation_files' in self.aggregated and self.aggregated['organisation_files'] > 0:
            return {'yes':1}
        else:
            return {'no':1}


class OrganisationFileStats(GenericFileStats):
    """ Stats calculated for an IATI Organisation XML file. """
    doc = None
    root = None
    schema_name = 'iati-organisations-schema.xsd'

    @returns_number
    def organisation_files(self):
        return 1


class OrganisationStats(CommonSharedElements):
    """ Stats calculated on a single iati-organisation. """
    blank = False

    @returns_number
    def organisations(self):
        return 1

    @returns_numberdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-organisation', {})

    @returns_numberdict
    def element_versions(self):
        return { self.element.attrib.get('version'): 1 }
        
    
