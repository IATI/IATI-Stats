from lxml import etree
import datetime, dateutil.parser, dateutil.tz
from collections import defaultdict
from decimal import Decimal
import decimal
from exchange_rates import toUSD
import os, re
import subprocess

codelist_mapping_xml = etree.parse('mapping.xml')
codelist_mappings = [ x.text for x in codelist_mapping_xml.xpath('mapping/path') ]
codelist_mappings = [ re.sub('^\/\/iati-activity', './',path) for path in codelist_mappings]
codelist_mappings = [ re.sub('^\/\/', './/', path) for path in codelist_mappings ]

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
        element_to_count_dict(child, path+'/'+child.tag, count_dict)
    return count_dict


## Decorators that modify return when self.blank = True etc.
def returns_intdictdict(f):
    """ Dectorator for dictionaries of integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(lambda: defaultdict(int))
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_intdict(f):
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


def returns_int(f):
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



class ActivityStats(object):
    """ Stats calculated on a single iati-activity. """
    element = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @no_aggregation
    def iati_identifier(self):
        try:
            return self.element.find('iati-identifier').text
        except AttributeError:
            return None

    @returns_int
    def activities(self):
        return 1

    @returns_intdict
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

    @returns_intdict
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
    
    @returns_int
    def spend(self):
        transactions = [ x for x in self.element.findall('transaction') if x.find('transaction-type') is not None and x.find('transaction-type').get('code') in ['D','E'] ]
        return sum(map(self.__value_to_dollars, transactions))

    @returns_intdict
    def spend_per_year(self):
        return {self.__get_start_year():self.spend()}
    
    @returns_intdict
    def activities_per_country(self):
        if self.__get_start_year() >= 2010:
            countries = self.element.findall('recipient-country')
            regions = self.element.findall('recipient-region')
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
    
    @returns_intdict
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

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-activity', {})

    @returns_intdictdict
    def codelist_values(self):
        out = defaultdict(lambda: defaultdict(int))
        for path in codelist_mappings:
            for value in self.element.xpath(path):
                out[path][value] += 1
        return out 

    @returns_intdictdict
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

    @returns_intdict
    def versions(self):
        return { self.root.attrib.get('version'): 1 }

    @returns_intdict
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

    @returns_intdict
    def wrong_roots(self):
        tag = self.root.tag
        try:
            ckan_type = ckan[publisher_re.match(self.fname).group(1)][self.fname]['extras']['filetype']
            if not ((tag == 'iati-organisations' and ckan_type == '"organisation"') or (tag == 'iati-activities' and ckan_type == '"activity"')):
                return {tag:1}
        except KeyError:
            pass

    @returns_int
    def file_size(self):
        return os.stat(self.inputfile).st_size

    @returns_intdict
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
    def updated(self):
        if self.inputfile.startswith('data/'):
            os.chdir('data')
            out = subprocess.check_output(['git', 'log', '-1', '--format="%ai"', '--', self.inputfile[5:]]).strip('"\n')
            os.chdir('..')
            return out
        


class ActivityFileStats(GenericFileStats):
    """ Stats calculated for an IATI Activity XML file. """
    doc = None
    root = None
    schema_name = 'iati-activities-schema.xsd'

    @returns_int
    def empty(self):
        return 0

    @returns_int
    def invalidxml(self):
        # Must be valid XML to have loaded this function
        return 0

    def nonstandardroots(self):
        return 0

    @returns_int
    def activity_files(self):
        return 1






class PublisherStats(object):
    """ Stats calculated for an IATI Publisher (directory in the data directory). """
    aggregated = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @returns_intdict
    def publishers_per_country(self):
        countries = self.aggregated['activities_per_country'].keys()
        return dict((c,1) for c in countries)

    @returns_intdict
    def publishers_per_organisation_type(self):
        organisation_types = self.aggregated['spend_per_organisation_type'].keys()
        return dict((o,1) for o in organisation_types)

    @returns_intdict
    def publishers_per_version(self):
        versions = self.aggregated['versions'].keys()
        return dict((v,1) for v in versions)

    @returns_int
    def publishers(self):
        return 1

    @returns_intdict
    def publishers_validation(self):
        if 'fail' in self.aggregated['validation']:
            return {'fail':1}
        else:
            return {'pass':1}

    @returns_intdict
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

    @returns_int
    def organisation_files(self):
        return 1


class OrganisationStats(object):
    """ Stats calculated on a single iati-organisation. """
    blank = False

    @returns_int
    def organisations(self):
        return 1

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-organisation', {})
