"""
This is the default stats module used by calculate_stats.py
You can choose a different set of tests by running calculate_stats.py with the ``--stats-module`` flag. 

"""
from __future__ import print_function
from lxml import etree
import datetime
from collections import defaultdict, OrderedDict
from decimal import Decimal
import decimal
import os, re
import subprocess
import copy

from stats.common.decorators import *
from stats.common import *

import iatirulesets

## In order to test whether or not correct codelist values are being used in the data 
## we need to pull in data about how codelists map to elements
codelist_mapping_xml = etree.parse('helpers/mapping.xml')
codelist_mappings = [ x.text for x in codelist_mapping_xml.xpath('mapping/path') ]
codelist_mappings = [ re.sub('^\/\/iati-activity', './',path) for path in codelist_mappings]
codelist_mappings = [ re.sub('^\/\/', './/', path) for path in codelist_mappings ]

import csv
reader = csv.reader(open('helpers/transparency_indicator/country_lang_map.csv'), delimiter=';')
country_lang_map = dict((row[0], row[2]) for row in reader)

def element_to_count_dict(element, path, count_dict, count_multiple=False):
    """
    Converts an element and it's children to a dictionary containing the
    count for each xpath.
    
    """
    if count_multiple:
        count_dict[path] += 1
    else:
        count_dict[path] = 1
    for child in element:
        if type(child.tag) == str:
            element_to_count_dict(child, path+'/'+child.tag, count_dict, count_multiple)
    for attribute in element.attrib:
        if count_multiple:
            count_dict[path+'/@'+attribute] += 1
        else:
            count_dict[path+'/@'+attribute] = 1
    return count_dict

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

    @returns_numberdict
    def participating_orgs(self):
        return dict([ (x.attrib.get('ref'), 1) for x in self.element.findall('participating-org')])

    @returns_numberdictdict
    def participating_orgs_text(self):
        return dict([ (x.attrib.get('ref'), {x.text:1}) for x in self.element.findall('participating-org')])

    @returns_numberdictdict
    def participating_orgs_by_role(self):
        return dict([ (x.attrib.get('role'), {x.attrib.get('ref'):1}) for x in self.element.findall('participating-org')])

    @returns_numberdict
    def element_versions(self):
        return { self.element.attrib.get('version'): 1 }

    @returns_numberdict
    def ruleset_passes(self):
        out = {}
        for ruleset_name in ['standard']:
            ruleset = json.load(open('helpers/rulesets/{0}.json'.format(ruleset_name)), object_pairs_hook=OrderedDict)
            out[ruleset_name] = int(iatirulesets.test_ruleset_subelement(ruleset, self.element))
        return out


class ActivityStats(CommonSharedElements):
    """ Stats calculated on a single iati-activity. """
    element = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''
    now = datetime.datetime.now() # TODO Add option to set this to date of git commit

    @returns_numberdict
    def iati_identifiers(self):
        return {self.element.find('iati-identifier').text:1}

    @returns_number
    def activities(self):
        return 1

    @returns_numberdict
    def hierarchies(self):
        return {self.element.attrib.get('hierarchy'):1}

    def by_hierarchy(self):
        out = {}
        for stat in ['activities', 'elements', 'elements_total',
                     'annualreport', 'annualreport_denominator',
                     'forwardlooking_currency_year', 'forwardlooking_activities_current', 'forwardlooking_activities_with_budgets'
                     ]:
            out[stat] = copy.deepcopy(getattr(self, stat)())
        if self.blank:
            return defaultdict(lambda: out)
        else:
            return { self.element.attrib.get('hierarchy'): out }

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

    @returns_numberdict
    @memoize
    def elements(self):
        return element_to_count_dict(self.element, 'iati-activity', {})

    @returns_numberdict
    @memoize
    def elements_total(self):
        return element_to_count_dict(self.element, 'iati-activity', defaultdict(int), True)

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
    
    @returns_numberdict
    def provider_org(self):
        out = defaultdict(int)
        for transaction in self.element.findall('transaction'):
            provider_org = transaction.find('provider-org')
            if provider_org is not None:
                out[provider_org.attrib.get('ref')] += 1
        return out

    @returns_numberdict
    def receiver_org(self):
        out = defaultdict(int)
        for transaction in self.element.findall('transaction'):
            receiver_org = transaction.find('receiver-org')
            if receiver_org is not None:
                out[receiver_org.attrib.get('ref')] += 1
        return out

    @returns_numberdict
    def transaction_timing(self):
        today = self.now.date()
        def months_ago(n):
            self.now.date() - datetime.timedelta(days=n*30)
        out = { 30:0, 60:0, 90:0, 180:0, 360:0 }
        for transaction in self.element.findall('transaction'):
            date = transaction_date(transaction)
            if date:
                days = (today - date).days
                if days < -1:
                    continue
                for k in sorted(out.keys()):
                    if days < k:
                        out[k] += 1
        return out

    @returns_numberdict
    def transaction_months(self):
        out = defaultdict(int)
        for transaction in self.element.findall('transaction'):
            date = transaction_date(transaction)
            if date:
                out[date.month] += 1
        return out

    @returns_numberdict
    def transaction_months_with_year(self):
        out = defaultdict(int)
        for transaction in self.element.findall('transaction'):
            date = transaction_date(transaction)
            if date:
                out['{}-{}'.format(date.year, str(date.month).zfill(2))] += 1
        return out

    @memoize
    def _end_actual(self):
        try:
            return iso_date(self.element.xpath("activity-date[@type='end-actual']")[0])
        except IndexError:
            return None

    @memoize
    def _current_activity(self):
        activity_status = self.element.find('activity-status')
        return (activity_status is not None and activity_status.attrib.get('code') not in ['3','4','5']) and (self._end_actual() is None or self._end_actual() > self.now.date())

    def _future_budget_planned_disbursement(self):
        for el in self.element.findall('budget') + self.element.findall('planned-disbursement'):
            date = iso_date(el.find('period-end'))
            if date and date >= self.now.date():
                return True
        return False

    @returns_numberdict
    def budget_lengths(self):
        out = defaultdict(int)
        for budget in self.element.findall('budget'):
            period_start = iso_date(budget.find('period-start'))
            period_end = iso_date(budget.find('period-end'))
            if period_start and period_end:
                out[(period_end - period_start).days] += 1
        return out

    @memoize
    def _recipient_language(self):
        try:
            return country_lang_map[self.element.xpath('recipient-country/@code')[0]]
        except IndexError:
            return None


    @returns_numberdict
    @memoize
    def annualreport(self):
        return {
            '1.3': 1 if self._current_activity() and self._future_budget_planned_disbursement() else 0,
            '2.2': 1 if ( len(self.element.xpath('recipient-country')) == 1 and
                          self.element.xpath('recipient-country/@code')[0] in country_lang_map and
                          self.element.xpath('@xml:lang') != country_lang_map[self.element.xpath('recipient-country/@code')[0]] and
                          self._recipient_language() and
                          ( self.element.xpath('title[@xml:lang="{0}"]'.format(self._recipient_language())
                            or self.element.xpath('description[@xml:lang="{0}"]'.format(self._recipient_language()))))) else 0,
            '2.3': 1 if self.element.xpath('activity-date[@type="start-planned"]') or self.element.xpath('activity-date[@type="start-actual"]') else 0,
            '2.4': 1 if self.element.xpath('activity-date[@type="end-planned"]') or self.element.xpath('activity-date[@type="end-actual"]') else 0,
            '2.5': 1 if self.element.xpath('participating-org[@role="Implementing"]') else 0,
            '2.6': 1 if self.element.xpath('participating-org[@role="Accountable"]') else 0,
            '3.1': 1 if self.element.xpath('location/description') else 0,
            '3.2': 1 if self.element.xpath('location/coordinates') or self.element.xpath('location/administrative') else 0,
            '3.3': 1 if self.element.xpath('sector[@vocabulary="" or @vocabulary="DAC" or not(@vocabulary)]') else 0,
            '5.1': 1 if self.element.xpath('transaction/transaction-type[@code="C"]') else 0,
            '5.2': 1 if self.element.xpath('transaction/transaction-type[@code="D"]') or self.element.xpath('transaction/transaction-type[@code="E"]') else 0,
            '5.3': len(self.element.xpath('transaction[(transaction-type/@code="D" and receiver-org) or (transaction-type/@code="IF" and provider-org)]')),
            '6.1': 1 if self.element.xpath('location/coordinates') or self.element.xpath('location/administrative') else 0,
            '6.2': 1 if self.element.xpath('conditions/@attached') in ['0', 'false'] or self.element.xpath('conditions/condition') else 0,
            '6.3': 1 if self.element.xpath('result') else 0,
            '6.4': 1 if self.element.xpath('result/indicator') else 0,
        }

    @returns_numberdict
    @memoize
    def annualreport_denominator(self):
        return {
            '1.3': 1 if self._current_activity() else 0,
            '2.2': 1 if ( len(self.element.xpath('recipient-country')) == 1 and
                          self.element.xpath('recipient-country/@code')[0] in country_lang_map and
                          self.element.xpath('@xml:lang') != country_lang_map[self.element.xpath('recipient-country/@code')[0]]) else 0,
            '2.3': 1,
            '2.4': 1,
            '2.5': 1,
            '2.6': 1,
            '3.1': 1,
            '3.2': 1,
            '3.3': 1,
            '5.1': 1,
            '5.2': 1,
            '5.3': len(self.element.xpath('transaction[transaction-type/@code="D" or transaction-type/@code="IF"]')),
            '6.1': 1,
            '6.2': 1,
            '6.3': 1,
            '6.4': 1,

        }

    def _transaction_year(self, transaction):
        date = transaction_date(transaction)
        return date.year if date else None

    def _spend_currency_year(self, transactions):
        out = defaultdict(lambda: defaultdict(Decimal))
        for transaction in transactions:
            value = transaction.find('value')
            if (transaction.find('transaction-type') is not None and
                    transaction.find('transaction-type').attrib.get('code') in ['D','E']):
                currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
                out[self._transaction_year(transaction)][currency] += Decimal(value.text)
        return out

    @returns_numberdictdict
    def spend_currency_year(self):
        return self._spend_currency_year(self.element.findall('transaction'))

    @returns_numberdictdict
    def forwardlooking_currency_year(self):
        out = defaultdict(lambda: defaultdict(Decimal))
        budgets = self.element.findall('budget')
        for budget in budgets:
            value = budget.find('value')
            currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
            out[budget_year(budget)][currency] += Decimal(value.text)
        return out

    def _forwardlooking_is_current(self, year):
        activity_end_years = [ iso_date(x).year for x in self.element.xpath('activity-date[@type="end-planned" or @type="end-actual"]') if iso_date(x) ]
        return any(activity_end_year>=year for activity_end_year in activity_end_years)

    @returns_numberdict
    def forwardlooking_activities_current(self):
        """
        The number of current activities for this year and the following 2 years.

        http://support.iatistandard.org/entries/52291985-Forward-looking-Activity-level-budgets-numerator

        Note: this is a different definition of 'current' to the older annual
        report stats in this file, so does not re-use those functions.

        """
        this_year = datetime.date.today().year
        return { year: int(self._forwardlooking_is_current(year))
                    for year in range(this_year, this_year+3) }

    @returns_numberdict
    def forwardlooking_activities_with_budgets(self):
        """
        The number of current activities with budgets for this year and the following 2 years.

        http://support.iatistandard.org/entries/52292065-Forward-looking-Activity-level-budgets-denominator

        """
        this_year = datetime.date.today().year
        budget_years = ([ budget_year(budget) for budget in self.element.findall('budget') ])
        return { year: int(self._forwardlooking_is_current(year) and year in budget_years)
                    for year in range(this_year, this_year+3) }

    def _transaction_type_code(self, transaction):
        type_code = None
        transaction_type = transaction.find('transaction-type')
        if transaction_type is not None:
            type_code = transaction_type.attrib.get('code')
        return type_code

    @returns_numberdictdict
    def transaction_dates(self):
        out = defaultdict(lambda: defaultdict(int))
        for transaction in self.element.findall('transaction'):
            date = transaction_date(transaction)
            out[self._transaction_type_code(transaction)][unicode(date)] += 1
        return out

    @returns_numberdictdict
    def activity_dates(self):
        out = defaultdict(lambda: defaultdict(int))
        for activity_date in self.element.findall('activity-date'):
            type_code = activity_date.attrib.get('type')
            date = iso_date(activity_date)
            out[type_code][unicode(date)] += 1
        return out

    @returns_numberdictdict
    def count_transactions_by_type_by_year(self):
        out = defaultdict(lambda: defaultdict(int))
        for transaction in self.element.findall('transaction'):
            out[self._transaction_type_code(transaction)][self._transaction_year(transaction)] += 1
        return out

    @returns_numberdictdictdict
    def sum_transactions_by_type_by_year(self):
        out = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
        for transaction in self.element.findall('transaction'):
            value = transaction.find('value')
            if (transaction.find('transaction-type') is not None and
                    transaction.find('transaction-type').attrib.get('code') in ['D','E']):
                currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
                out[self._transaction_type_code(transaction)][currency][self._transaction_year(transaction)] += Decimal(value.text)
        return out

    @returns_numberdictdict
    def count_budgets_by_type_by_year(self):
        out = defaultdict(lambda: defaultdict(int))
        for budget in self.element.findall('budget'):
            out[budget.attrib.get('type')][budget_year(budget)] += 1
        return out

    @returns_numberdictdictdict
    def sum_budgets_by_type_by_year(self):
        out = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
        for budget in self.element.findall('budget'):
            value = budget.find('value')
            currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
            out[budget.attrib.get('type')][currency][budget_year(budget)] += Decimal(value.text)
        return out

    @returns_numberdict
    def count_planned_disbursements_by_year(self):
        out = defaultdict(int)
        for pd in self.element.findall('planned-disbursement'):
            out[planned_disbursement_year(pd)] += 1
        return out

    @returns_numberdictdict
    def sum_planned_disbursements_by_year(self):
        out = defaultdict(lambda: defaultdict(Decimal))
        for pd in self.element.findall('planned-disbursement'):
            value = pd.find('value')
            currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
            out[currency][planned_disbursement_year(pd)] += Decimal(value.text)
        return out

import json
ckan = json.load(open('helpers/ckan.json'))
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
            with open('helpers/schemas/{0}/{1}'.format(version, self.schema_name)) as f:
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

    """
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
    """
        
    @returns_number
    def empty(self):
        return 0

    @returns_number
    def invalidxml(self):
        # Must be valid XML to have loaded this function
        return 0

    def nonstandardroots(self):
        return 0

    def toolarge(self):
        return 0



    

class ActivityFileStats(GenericFileStats):
    """ Stats calculated for an IATI Activity XML file. """
    doc = None
    root = None
    schema_name = 'iati-activities-schema.xsd'

    @returns_number
    def activity_files(self):
        return 1



class PublisherStats(object):
    """ Stats calculated for an IATI Publisher (directory in the data directory). """
    aggregated = None
    blank = False
    strict = False # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @returns_dict
    def bottom_hierarchy(self):
        hierarchies = self.aggregated['hierarchies'].keys()
        if not hierarchies: return
        try:
            h = str(max(map(int, hierarchies)))
        except ValueError:
            h = max(hierarchies)
        try:
            out = copy.deepcopy(self.aggregated['by_hierarchy'][h])
        except KeyError:
            out = {}
        return out

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

    # The following two functions have different names to the AllData equivalents
    # This is because the aggregation of the publisher level functions will ignore duplication between publishers

    @returns_number
    @memoize
    def publisher_unique_identifiers(self):
        return len(self.aggregated['iati_identifiers'])

    @returns_numberdict
    def publisher_duplicate_identifiers(self):
        return {k:v for k,v in self.aggregated['iati_identifiers'].items() if v>1}

    def _timeliness_transactions(self):
        tt = self.aggregated['transaction_timing']
        if [tt['30'], tt['60'], tt['90']].count(0) <= 1:
            return 'Monthly'
        elif [tt['30'], tt['60'], tt['90']].count(0) <= 2:
            return 'Quarterly'
        elif tt['180'] != 0:
            return 'Six-monthly'
        elif tt['360'] != 0:
            return 'Annual'
        else:
            return 'Beyond one year'

    @no_aggregation
    def timelag(self):
        def previous_months_generator(d):
            year = d.year
            month = d.month
            for i in range(0,12):
                month -= 1
                if month <= 0:
                    year -= 1
                    month = 12
                yield '{}-{}'.format(year,str(month).zfill(2))
        previous_months = list(previous_months_generator(self.today))
        transaction_months_with_year = self.aggregated['transaction_months_with_year']
        if [ x in transaction_months_with_year  for x in previous_months[:3] ].count(True) >= 2:
            return 'One month'
        elif [ x in transaction_months_with_year  for x in previous_months[:3] ].count(True) >= 1:
            return 'A quarter'
        elif True in [ x in transaction_months_with_year  for x in previous_months[:6] ]:
            return 'Six months'
        elif  True in [ x in transaction_months_with_year  for x in previous_months[:12] ]:
            return 'One year'
        else:
            return 'More than one year'

    def _transaction_alignment(self):
        transaction_months = self.aggregated['transaction_months'].keys()
        if len(transaction_months) == 12:
            return 'Monthly'
        elif len(set(map(lambda x: (int(x)-1)//3, transaction_months))) == 4:
            return 'Quarterly'
        elif len(transaction_months) >= 1:
            return 'Annually'
        else:
            return ''
   
    @no_aggregation
    @memoize
    def budget_length_median(self):
        budget_lengths = self.aggregated['budget_lengths']
        budgets = sum(budget_lengths.values())
        i = 0
        median = None
        for k,v in sorted([ (int(k),v) for k,v in budget_lengths.items()]):
            i += v
            if i >= (budgets/2.0):
                if median:
                    # Handle the case where the median falls between two frequency bins
                    median = (median + k) / 2.0
                else:
                    median = k
                if i != (budgets/2.0):
                    break
        return median

    def _budget_alignment(self):
        median = self.budget_length_median()
        if median is None:
            return 'Not known'
        elif median < 100:
            return 'Quarterly'
        elif median < 370:
            return 'Annually'
        else:
            return 'Beyond one year'

    @no_aggregation
    def annualreport_textual(self):
        return {
            '1.1': self._timeliness_transactions(),
            #'1.2':
            '1.4': self._transaction_alignment(),
            '1.5': self._budget_alignment(),
        }

    @returns_numberdict
    def annualreport(self):
        out = self.aggregated['annualreport']
        out.update({
            '1.1': 0,
            '1.2': 0,
            '1.4': 0,
            '1.5': 0,
            '2.1': self.publisher_unique_identifiers()
        })
        return out

    @returns_numberdict
    def annualreport_denominator(self):
        out = self.aggregated['annualreport_denominator']
        out.update({
            '2.1': self.aggregated['activities']
        })
        return out

    @no_aggregation
    def date_extremes(self):
        notnone = lambda x: x is not None
        activity_dates = { k:filter(notnone, map(iso_date_match, v.keys()))
                for k,v in self.aggregated['activity_dates'].items() }
        min_dates = { k:min(v) for k,v in activity_dates.items() if v }
        max_dates = { k:max(v) for k,v in activity_dates.items() if v }
        overall_min = unicode(min(min_dates.values())) if min_dates else None
        overall_max = unicode(max(max_dates.values())) if min_dates else None
        return {
            'min': {
                'overall': overall_min,
                'by_type': { k:unicode(v) for k,v in min_dates.items() }
            },
            'max': {
                'overall': overall_max,
                'by_type': { k:unicode(v) for k,v in max_dates.items() }
            },
        }

    @no_aggregation
    def most_recent_transaction_date(self):
        nonfuture_transaction_dates = filter(lambda x: x is not None and x <= self.today,
            map(iso_date_match, sum((x.keys() for x in self.aggregated['transaction_dates'].values()), [])))
        if nonfuture_transaction_dates:
            return unicode(max(nonfuture_transaction_dates))

    @no_aggregation
    def latest_transaction_date(self):
        transaction_dates = filter(lambda x: x is not None,
            map(iso_date_match, sum((x.keys() for x in self.aggregated['transaction_dates'].values()), [])))
        if transaction_dates:
            return unicode(max(transaction_dates))

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
    def elements_total(self):
        return element_to_count_dict(self.element, 'iati-organisation', defaultdict(int), True)

    @returns_numberdict
    def element_versions(self):
        return { self.element.attrib.get('version'): 1 }
        
class AllDataStats(object):
    blank = False

    @returns_number
    def unique_identifiers(self):
        return len(self.aggregated['iati_identifiers'])

    @returns_numberdict
    def duplicate_identifiers(self):
        return {k:v for k,v in self.aggregated['iati_identifiers'].items() if v>1}
