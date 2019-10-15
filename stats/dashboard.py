"""
This is the default stats module used by calculate_stats.py
You can choose a different set of tests by running calculate_stats.py with the ``--stats-module`` flag.

"""
from __future__ import print_function
from lxml import etree
import datetime
from datetime import date
from collections import defaultdict, OrderedDict
from decimal import Decimal
import decimal
import os
import re
import json
import csv

from stats.common.decorators import (
    memoize,
    no_aggregation,
    returns_dict,
    returns_numberdict,
    returns_numberdictdict,
    returns_number,
    returns_numberdictdictdict,
)
from stats.common import (
    budget_year,
    debug,
    get_registry_id_matches,
    iso_date,
    iso_date_match,
    planned_disbursement_year,
    transaction_date,
)

import iatirulesets
from helpers.currency_conversion import get_USD_value


def add_years(d, years):
    """Return a date that's `years` years before/after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    Keyword arguments:
    d -- a date (or datetime) object
    years -- number of years to increment the date. Accepts negative numbers

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def all_true_and_not_empty(bool_iterable):
    """For a given list, check that all elements return true and that the list is not empty.

    Args:
        bool_iterable (iterable of bool): An iterable containing values that can be cast to a bool.

    """

    # Ensure that the given list is indeed a simple list
    bool_list = list(bool_iterable)

    # Perform logic. Check that all elements return true and that the list is not empty
    if (all(bool_list)) and (len(bool_list) > 0):
        return True
    else:
        return False


def is_number(v):
    """ Tests if a variable is a number.
        Input: s - a variable
        Return: True if v is a number
                False if v is not a number
        NOTE: Any changes to this function should be replicated in:
              https://github.com/IATI/IATI-Dashboard/blob/master/coverage.py#L7
    """
    try:
        float(v)
        return True
    except ValueError:
        return False


def convert_to_float(x):
    """ Converts a variable to a float value, or 0 if it cannot be converted to a float.
        Input: x - a variable
        Return: x as a float, or zero if x is not a number
        NOTE: Any changes to this function should be replicated in:
              https://github.com/IATI/IATI-Dashboard/blob/master/coverage.py#L19
    """
    if is_number(x):
        return float(x)
    else:
        return 0


# Import codelists
# In order to test whether or not correct codelist values are being used in the data
# we need to pull in data about how codelists map to elements
def get_codelist_mapping(major_version):
    codelist_mapping_xml = etree.parse('helpers/mapping-{}.xml'.format(major_version))
    codelist_mappings = [x.text for x in codelist_mapping_xml.xpath('mapping/path')]
    codelist_mappings = [re.sub(r'^\/\/iati-activity', './', path) for path in codelist_mappings]
    codelist_mappings = [re.sub(r'^\/\/', './/', path) for path in codelist_mappings]
    return codelist_mappings


codelist_mappings = {major_version: get_codelist_mapping(major_version) for major_version in ['1', '2']}

CODELISTS = {'1': {}, '2': {}}
for major_version in ['1', '2']:
    for codelist_name in [
        'Version',
        'ActivityStatus',
        'Currency',
        'Sector',
        'SectorCategory',
        'DocumentCategory',
        'AidType',
        'BudgetNotProvided'
    ]:
        CODELISTS[major_version][codelist_name] = set(
            c['code'] for c in json.load(
                open('helpers/codelists/{}/{}.json'.format(major_version, codelist_name))
            )['data']
        )


# Import country language mappings, and save as a dictionary
# Contains a dictionary of ISO 3166-1 country codes (as key) with a list of ISO 639-1 language codes (as value)
reader = csv.reader(open('helpers/transparency_indicator/country_lang_map.csv'), delimiter=',')
country_lang_map = {}
for row in reader:
    if row[0] not in country_lang_map.keys():
        country_lang_map[row[0]] = [row[2]]
    else:
        country_lang_map[row[0]].append(row[2])


# Import reference spending data, and save as a dictionary
reference_spend_data = {}
with open('helpers/transparency_indicator/reference_spend_data.csv', 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for line in reader:
        pub_registry_id = line[1]

        # Update the publisher registry ID, if this publisher has since updated their registry ID
        if pub_registry_id in get_registry_id_matches().keys():
            pub_registry_id = get_registry_id_matches()[pub_registry_id]

        reference_spend_data[pub_registry_id] = {'publisher_name': line[0],
                                                 '2014_ref_spend': line[2],
                                                 '2015_ref_spend': line[6],
                                                 '2015_official_forecast': line[10],
                                                 'currency': line[11],
                                                 'spend_data_error_reported': True if line[12] == 'Y' else False,
                                                 'DAC': True if 'DAC' in line[3] else False}


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
            element_to_count_dict(child, path + '/' + child.tag, count_dict, count_multiple)
    for attribute in element.attrib:
        if count_multiple:
            count_dict[path + '/@' + attribute] += 1
        else:
            count_dict[path + '/@' + attribute] = 1
    return count_dict


def valid_date(date_element):
    if date_element is None:
        return False
    schema_root = etree.XML('''
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="activity-date" type="dateType"/>
            <xsd:element name="transaction-date" type="dateType"/>
            <xsd:element name="period-start" type="dateType"/>
            <xsd:element name="period-end" type="dateType"/>
            <xsd:complexType name="dateType" mixed="true">
                <xsd:sequence>
                    <xsd:any minOccurs="0" maxOccurs="unbounded" processContents="lax" />
                </xsd:sequence>
                <xsd:attribute name="iso-date" type="xsd:date" use="required"/>
                <xsd:anyAttribute processContents="lax"/>
            </xsd:complexType>
            <xsd:element name="value">
                <xsd:complexType mixed="true">
                    <xsd:sequence>
                        <xsd:any minOccurs="0" maxOccurs="unbounded" processContents="lax" />
                    </xsd:sequence>
                    <xsd:attribute name="value-date" type="xsd:date" use="required"/>
                    <xsd:anyAttribute processContents="lax"/>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    ''')
    schema = etree.XMLSchema(schema_root)
    return schema.validate(date_element)


def valid_url(element):
    if element is None:
        return False

    if element.tag == 'document-link':
        url = element.attrib.get('url')
    elif element.tag == 'activity-website':
        url = element.text
    else:
        return False

    if url is None or url == '' or '://' not in url:
        # Return false if it's empty or not an absolute url
        return False

    schema_root = etree.XML('''
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="document-link">
                <xsd:complexType mixed="true">
                    <xsd:sequence>
                        <xsd:any minOccurs="0" maxOccurs="unbounded" processContents="lax" />
                    </xsd:sequence>
                    <xsd:attribute name="url" type="xsd:anyURI" use="required"/>
                    <xsd:anyAttribute processContents="lax"/>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="activity-website">
                <xsd:complexType>
                    <xsd:simpleContent>
                        <xsd:extension base="xsd:anyURI">
                            <xsd:anyAttribute processContents="lax"/>
                        </xsd:extension>
                    </xsd:simpleContent>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    ''')
    schema = etree.XMLSchema(schema_root)
    return schema.validate(element)


def valid_value(value_element):
    if value_element is None:
        return False
    schema_root = etree.XML('''
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="value">
                <xsd:complexType>
                    <xsd:simpleContent>
                        <xsd:extension base="xsd:decimal">
                            <xsd:anyAttribute processContents="lax"/>
                        </xsd:extension>
                    </xsd:simpleContent>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    ''')
    schema = etree.XMLSchema(schema_root)
    return schema.validate(value_element)


def valid_coords(x):
    try:
        coords = x.split(' ')
    except AttributeError:
        return False
    if len(coords) != 2:
        return False
    try:
        lat = decimal.Decimal(coords[0])
        lng = decimal.Decimal(coords[1])
        # the (0, 0) coordinate is invalid since it's in the ocean in international waters and near-certainly not actual data
        if lat == 0 and lng == 0:
            return False
        # values outside the valid (lat, lng) coordinate space are invalid
        elif lat < -90 or lat > 90 or lng < -180 or lng > 180:
            return False
        else:
            return True
    except decimal.InvalidOperation:
        return False


def get_currency(iati_activity_object, budget_pd_transaction):
    """ Returns the currency used for a budget, planned disbursement or transaction value. This is based
        on either the currency specified in value/@currency, or the default currency specified in
        iati-activity/@default-currency).
    """

    # Get the default currency (specified in iati-activity/@default-currency)
    currency = iati_activity_object.element.attrib.get('default-currency')

    # If there is a currency within the value element, overwrite the default currency
    if budget_pd_transaction.xpath('value/@currency'):
        currency = budget_pd_transaction.xpath('value/@currency')[0]

    # Return the currency
    return currency


def has_xml_lang(obj):
    """Test if an obj has an XML lang attribute declared.
       Input: an etree XML object, for example a narrative element
       Return: True if @xml:lang is present, or False if not
    """
    return len(obj.xpath("@xml:lang", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})) > 0


def get_language(major_version, iati_activity_obj, title_or_description_obj):
    """ Returns the language (or languages if publishing to version 2.x) used for a single title or
        description element. This is based on either the language specified in @xml:lang
        (version 1.x) or narrative/@xml:lang (version 2.x), or the default language, as specified
        in iati-activity/@xml:lang).
        Input: iati_activity_object - An IATI Activity element. Will be self in most cases.
        Returns: List of language/s used in the given title_or_description_elem.
                 Empty list if no languages specified.
    """

    langs = []

    # Get default language for this activity
    if has_xml_lang(iati_activity_obj):
        default_lang = iati_activity_obj.xpath("@xml:lang", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})[0]

    if major_version == '2':
        for narrative_obj in title_or_description_obj.findall('narrative'):
            if has_xml_lang(narrative_obj):
                langs.append(narrative_obj.xpath("@xml:lang", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})[0])
            elif has_xml_lang(iati_activity_obj):
                langs.append(default_lang)

    else:
        if has_xml_lang(title_or_description_obj):
            langs.append(title_or_description_obj.xpath("@xml:lang", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})[0])
        elif has_xml_lang(iati_activity_obj):
            langs.append(default_lang)

    # Remove any duplicates and return
    return list(set(langs))


# Deals with elements that are in both organisation and activity files
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
        try:
            return {self.element.find('reporting-org').attrib.get('ref'): 1}
        except AttributeError:
            return {'null': 1}


    @returns_numberdict
    def participating_orgs(self):
        return dict([(x.attrib.get('ref'), 1) for x in self.element.findall('participating-org')])

    @returns_numberdict
    def element_versions(self):
        return {self.element.attrib.get('version'): 1}

    @returns_numberdict
    @memoize
    def _major_version(self):
        if self._version().startswith('2.'):
            return '2'
        else:
            return '1'

    @returns_numberdict
    @memoize
    def _version(self):
        allowed_versions = CODELISTS['2']['Version']
        parent = self.element.getparent()
        if parent is None:
            print('No parent of iati-activity, is this a test? Assuming version 1.01')
            return '1.01'
        version = parent.attrib.get('version')
        if version and version in allowed_versions:
            return version
        else:
            return '1.01'

    @returns_numberdict
    def _ruleset_passes(self):
        out = {}
        for ruleset_name in ['standard']:
            ruleset = json.load(open('helpers/rulesets/{0}.json'.format(ruleset_name)), object_pairs_hook=OrderedDict)
            out[ruleset_name] = int(iatirulesets.test_ruleset_subelement(ruleset, self.element))
        return out


class ActivityStats(CommonSharedElements):
    """ Stats calculated on a single iati-activity. """
    element = None
    blank = False
    strict = False  # (Setting this to true will ignore values that don't follow the schema)
    context = ''
    now = datetime.datetime.now()  # TODO Add option to set this to date of git commit


    @returns_numberdict
    def iati_identifiers(self):
        try:
            return {self.element.find('iati-identifier').text: 1}
        except AttributeError:
            return None


    @returns_number
    def activities(self):
        return 1

    @returns_numberdict
    def hierarchies(self):
        return {self.element.attrib.get('hierarchy'): 1}

    def _budget_not_provided(self):
        if self.element.attrib.get('budget-not-provided') is not None:
            return int(self.element.attrib.get('budget-not-provided'))
        else:
            return None

    @returns_numberdict
    def currencies(self):
        currencies = [x.find('value').get('currency') for x in self.element.findall('transaction') if x.find('value') is not None]
        currencies = [c if c else self.element.get('default-currency') for c in currencies]
        return dict((c, 1) for c in currencies)

    def _planned_start_code(self):
        if self._major_version() == '1':
            return 'start-planned'
        else:
            return '1'

    def _actual_start_code(self):
        if self._major_version() == '1':
            return 'start-actual'
        else:
            return '2'

    def _planned_end_code(self):
        if self._major_version() == '1':
            return 'end-planned'
        else:
            return '3'

    def _actual_end_code(self):
        if self._major_version() == '1':
            return 'end-actual'
        else:
            return '4'

    def _incoming_funds_code(self):
        if self._major_version() == '1':
            return 'IF'
        else:
            return '1'

    def _commitment_code(self):
        if self._major_version() == '1':
            return 'C'
        else:
            return '2'

    def _disbursement_code(self):
        if self._major_version() == '1':
            return 'D'
        else:
            return '3'

    def _expenditure_code(self):
        if self._major_version() == '1':
            return 'E'
        else:
            return '4'

    def _dac_5_code(self):
        if self._major_version() == '1':
            return 'DAC'
        else:
            return '1'

    def _dac_3_code(self):
        if self._major_version() == '1':
            return 'DAC-3'
        else:
            return '2'

    def _funding_code(self):
        if self._major_version() == '1':
            return 'Funding'
        else:
            return '1'

    def _OrganisationRole_Extending_code(self):
        if self._major_version() == '1':
            return 'Extending'
        else:
            return '3'

    def _OrganisationRole_Implementing_code(self):
        if self._major_version() == '1':
            return 'Implementing'
        else:
            return '4'

    def __get_start_year(self):
        activity_date = self.element.find("activity-date[@type='{}']".format(self._actual_start_code()))
        if activity_date is None:
            activity_date = self.element.find("activity-date[@type='{}']".format(self._planned_start_code()))
        if activity_date is not None and activity_date.get('iso-date'):
            try:
                act_date = datetime.datetime.strptime(activity_date.get('iso-date').strip('Z'), "%Y-%m-%d")
                return int(act_date.year)
            except ValueError as e:
                debug(self, e)
            except AttributeError as e:
                debug(self, e)

    @returns_numberdict
    def activities_per_year(self):
        return {self.__get_start_year(): 1}

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
        for path in codelist_mappings[self._major_version()]:
            for value in self.element.xpath(path):
                out[path][value] += 1
        return out

    @returns_numberdictdict
    def codelist_values_by_major_version(self):
        out = defaultdict(lambda: defaultdict(int))
        for path in codelist_mappings[self._major_version()]:
            for value in self.element.xpath(path):
                out[path][value] += 1
        return {self._major_version(): out}

    @returns_numberdictdict
    def boolean_values(self):
        out = defaultdict(lambda: defaultdict(int))
        for path in [
                'conditions/@attached',
                'crs-add/aidtype-flag/@significance',
                'crs-add/other-flags/@significance',
                'fss/@priority',
                '@humanitarian',
                'reporting-org/@secondary-reporter',
                'result/indicator/@ascending',
                'result/@aggregation-status',
                'transaction/@humanitarian'
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

    def _transaction_year(self, transaction):
        t_date = transaction_date(transaction)
        return t_date.year if t_date else None

    def _is_secondary_reported(self):
        """Tests if this activity has been secondary reported. Test based on if the
           secondary-reporter flag is set.
        Input -- None
        Output:
          True -- Secondary-reporter flag set
          False -- Secondary-reporter flag not set, or evaulates to False
        """
        return bool(list((filter(lambda x: int(x) if str(x).isdigit() else 0,
                    self.element.xpath('reporting-org/@secondary-reporter')))))

    @returns_dict
    def activities_secondary_reported(self):
        if self._is_secondary_reported():
            return {self.element.find('iati-identifier').text: 0}
        else:
            return {}

    def _get_end_date(self):
        """Gets the end date for the activity. An 'actual end date' is preferred
           over a 'planned end date'
           Inputs: None
           Output: a date object, or None if no value date found
        """
        # Get enddate. An 'actual end date' is preferred over a 'planned end date'
        end_date_list = (self.element.xpath('activity-date[@type="{}"]'.format(self._actual_end_code())) or
                         self.element.xpath('activity-date[@type="{}"]'.format(self._planned_end_code())))

        # If there is a date, convert to a date object
        if end_date_list:
            return iso_date(end_date_list[0])
        else:
            return None

    def _get_ratio_commitments_disbursements(self, year):
        """ Calculates the ratio of commitments vs total amount disbursed or expended in or before the
            input year. Values are converted to USD to improve comparability.
            Input:
              year -- The point in time to aggregate expenditure and disbursements
            Returns:
              Float: 0 represents no commitments disbursed, 1 represents all commitments disbursed.
        """

        # Compute the sum of all commitments

        # Build a list of tuples, each tuple contains: (currency, value, date)
        commitment_transactions = [(
            get_currency(self, transaction),
            transaction.xpath('value/text()')[0] if transaction.xpath('value/text()') else None,
            transaction_date(transaction)
        ) for transaction in self.element.xpath('transaction[transaction-type/@code="{}"]'.format(self._commitment_code()))]

        # Convert transaction values to USD and aggregate
        commitment_transactions_usd_total = sum([get_USD_value(x[0], x[1], x[2].year)
                                                 for x in commitment_transactions if None not in x])

        # Compute the sum of all disbursements and expenditures up to and including the inputted year
        # Build a list of tuples, each tuple contains: (currency, value, date)
        exp_disb_transactions = [(
            get_currency(self, transaction),
            transaction.xpath('value/text()')[0] if transaction.xpath('value/text()') else None,
            transaction_date(transaction)
        ) for transaction in self.element.xpath('transaction[transaction-type/@code="{}" or transaction-type/@code="{}"]'.format(self._disbursement_code(), self._expenditure_code()))]

        # If the transaction date this year or older, convert transaction values to USD and aggregate
        exp_disb_transactions_usd_total = sum([get_USD_value(x[0], x[1], x[2].year)
                                              for x in exp_disb_transactions if None not in x and x[2].year <= int(year)])

        if commitment_transactions_usd_total > 0:
            return convert_to_float(exp_disb_transactions_usd_total) / convert_to_float(commitment_transactions_usd_total)
        else:
            return None

    def _is_donor_publisher(self):
        """Returns True if this activity is deemed to be reported by a donor publisher.
           Methodology descibed in https://github.com/IATI/IATI-Dashboard/issues/377
        """
        # If there is no 'reporting-org/@ref' element, return False to avoid a 'list index out of range'
        # error in the statement that follows
        if len(self.element.xpath('reporting-org/@ref')) < 1:
            return False

        return (
            (
                self.element.xpath('reporting-org/@ref')[0] in self.element.xpath("participating-org[@role='{}']/@ref|participating-org[@role='{}']/@ref".format(
                    self._funding_code(),
                    self._OrganisationRole_Extending_code()))
            ) and (
                self.element.xpath('reporting-org/@ref')[0] not in self.element.xpath("participating-org[@role='{}']/@ref".format(
                    self._OrganisationRole_Implementing_code())
                )
            )
        )

    def _is_recipient_language_used(self):
        """If there is only 1 recipient-country, test if one of the languages for that country is used
           in the title and description elements.
        """

        # Test only applies to activities where there is only 1 recipient-country
        if len(self.element.findall('recipient-country')) == 1:
            # Get list of languages for the recipient-country
            try:
                country_langs = country_lang_map[self.element.xpath('recipient-country/@code')[0]]
            except (KeyError, IndexError):
                country_langs = []

            # Get lists of the languages used in the title and descripton elements
            langs_in_title = []
            for title_elem in self.element.findall('title'):
                langs_in_title.extend(get_language(self._major_version(), self.element, title_elem))

            langs_in_description = []
            for descripton_elem in self.element.findall('description'):
                langs_in_description.extend(get_language(self._major_version(), self.element, descripton_elem))

            # Test if the languages used for the title and description are in the list of country langs
            if len(set(langs_in_title).intersection(country_langs)) > 0 and len(set(langs_in_description).intersection(country_langs)) > 0:
                return 1
            else:
                return 0

        else:
            return 0

    @returns_numberdict
    def humanitarian(self):
        humanitarian_sectors_dac_5_digit = ['72010', '72040', '72050', '73010', '74010', '74020']
        humanitarian_sectors_dac_3_digit = ['720', '730', '740']

        # logic around use of the @humanitarian attribute
        is_humanitarian_by_attrib_activity = 1 if ('humanitarian' in self.element.attrib) and (self.element.attrib['humanitarian'] in ['1', 'true']) else 0
        is_not_humanitarian_by_attrib_activity = 1 if ('humanitarian' in self.element.attrib) and (self.element.attrib['humanitarian'] in ['0', 'false']) else 0
        is_humanitarian_by_attrib_transaction = 1 if set(self.element.xpath('transaction/@humanitarian')).intersection(['1', 'true']) else 0
        is_humanitarian_by_attrib = (self._version() in ['2.02', '2.03']) and (is_humanitarian_by_attrib_activity or (is_humanitarian_by_attrib_transaction and not is_not_humanitarian_by_attrib_activity))

        # logic around DAC sector codes deemed to be humanitarian
        is_humanitarian_by_sector_5_digit_activity = 1 if set(self.element.xpath('sector[@vocabulary="{0}" or not(@vocabulary)]/@code'.format(self._dac_5_code()))).intersection(humanitarian_sectors_dac_5_digit) else 0
        is_humanitarian_by_sector_5_digit_transaction = 1 if set(self.element.xpath('transaction[not(@humanitarian="0" or @humanitarian="false")]/sector[@vocabulary="{0}" or not(@vocabulary)]/@code'.format(self._dac_5_code()))).intersection(humanitarian_sectors_dac_5_digit) else 0
        is_humanitarian_by_sector_3_digit_activity = 1 if set(self.element.xpath('sector[@vocabulary="{0}"]/@code'.format(self._dac_3_code()))).intersection(humanitarian_sectors_dac_3_digit) else 0
        is_humanitarian_by_sector_3_digit_transaction = 1 if set(self.element.xpath('transaction[not(@humanitarian="0" or @humanitarian="false")]/sector[@vocabulary="{0}"]/@code'.format(self._dac_3_code()))).intersection(humanitarian_sectors_dac_3_digit) else 0
        # helper variables to help make logic easier to read
        is_humanitarian_by_sector_activity = is_humanitarian_by_sector_5_digit_activity or is_humanitarian_by_sector_3_digit_activity
        is_humanitarian_by_sector_transaction = is_humanitarian_by_sector_5_digit_transaction or is_humanitarian_by_sector_3_digit_transaction
        is_humanitarian_by_sector = is_humanitarian_by_sector_activity or (is_humanitarian_by_sector_transaction and (self._major_version() in ['2']))

        # combine the various ways in which an activity may be humanitarian
        is_humanitarian = 1 if (is_humanitarian_by_attrib or is_humanitarian_by_sector) else 0
        # deal with some edge cases that have veto
        if is_not_humanitarian_by_attrib_activity:
            is_humanitarian = 0

        return {
            'is_humanitarian': is_humanitarian,
            'is_humanitarian_by_attrib': is_humanitarian_by_attrib,
            'contains_humanitarian_scope': 1 if (
                is_humanitarian and
                self._version() in ['2.02', '2.03'] and
                all_true_and_not_empty(self.element.xpath('humanitarian-scope/@type')) and
                all_true_and_not_empty(self.element.xpath('humanitarian-scope/@code'))
            ) else 0,
            'uses_humanitarian_clusters_vocab': 1 if (
                is_humanitarian and
                self._version() in ['2.02', '2.03'] and
                self.element.xpath('sector/@vocabulary="10"')
            ) else 0
        }

    def _transaction_type_code(self, transaction):
        type_code = None
        transaction_type = transaction.find('transaction-type')
        if transaction_type is not None:
            type_code = transaction_type.attrib.get('code')
        return type_code

    @returns_numberdictdict
    def activity_dates(self):
        out = defaultdict(lambda: defaultdict(int))
        for activity_date in self.element.findall('activity-date'):
            type_code = activity_date.attrib.get('type')
            act_date = iso_date(activity_date)
            out[type_code][act_date] += 1
        return out

    @returns_numberdictdictdict
    def sum_transactions_by_type_by_year(self):
        out = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
        for transaction in self.element.findall('transaction'):
            value = transaction.find('value')
            if (transaction.find('transaction-type') is not None and
                    transaction.find('transaction-type').attrib.get('code') in [self._incoming_funds_code(), self._commitment_code(), self._disbursement_code(), self._expenditure_code()]):

                # Set transaction_value if a value exists for this transaction. Else set to 0
                transaction_value = 0 if value is None else Decimal(value.text)

                out[self._transaction_type_code(transaction)][get_currency(self, transaction)][self._transaction_year(transaction)] += transaction_value
        return out

    @returns_numberdictdictdict
    def sum_transactions_by_type_by_year_usd(self):
        out = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))

        # Loop over the values in computed in sum_transactions_by_type_by_year() and build a
        # dictionary of USD values for the currency and year
        for transaction_type, data in list(self.sum_transactions_by_type_by_year().items()):
            for currency, years in data.items():
                for year, value in years.items():
                    if None not in [currency, value, year]:
                        out[transaction_type]['USD'][year] += get_USD_value(currency, value, year)
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

            # Set budget_value if a value exists for this budget. Else set to 0
            budget_value = 0 if value is None else Decimal(value.text)

            out[budget.attrib.get('type')][get_currency(self, budget)][budget_year(budget)] += budget_value
        return out

    @returns_numberdictdictdict
    def sum_budgets_by_type_by_year_usd(self):
        out = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))

        # Loop over the values in computed in sum_budgets_by_type_by_year() and build a
        # dictionary of USD values for the currency and year
        for budget_type, data in self.sum_budgets_by_type_by_year().items():
            for currency, years in data.items():
                for year, value in years.items():
                    if None not in [currency, value, year]:
                        out[budget_type]['USD'][year] += get_USD_value(currency, value, year)
        return out

    @returns_numberdictdict
    def sum_planned_disbursements_by_year(self):
        out = defaultdict(lambda: defaultdict(Decimal))
        for pd in self.element.findall('planned-disbursement'):
            value = pd.find('value')

            # Set disbursement_value if a value exists for this disbursement. Else set to 0
            disbursement_value = 0 if value is None else Decimal(value.text)

            out[get_currency(self, pd)][planned_disbursement_year(pd)] += disbursement_value
        return out


ckan = json.load(open('helpers/ckan.json'))
publisher_re = re.compile(r'(.*)\-[^\-]')


class GenericFileStats(object):
    blank = False

    @returns_numberdict
    def versions(self):
        return {self.root.attrib.get('version'): 1}

    @returns_numberdict
    def version_mismatch(self):
        file_version = self.root.attrib.get('version')
        element_versions = self.root.xpath('//iati-activity/@version')
        element_versions = list(set(element_versions))
        return {
            'true' if (file_version is not None and len(element_versions) and [file_version] != element_versions) else 'false': 1
        }

    @returns_numberdict
    def validation(self):
        version = self.root.attrib.get('version')
        if version in [None, '1', '1.0', '1.00']:
            version = '1.01'
        try:
            with open('helpers/schemas/{0}/{1}'.format(version, self.schema_name)) as f:
                xmlschema_doc = etree.parse(f)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                if xmlschema.validate(self.doc):
                    return {'pass': 1}
                else:
                    return {'fail': 1}
        except IOError:
            debug(self, 'Unsupported version \'{0}\' '.format(version))
            return {'fail': 1}

    @returns_numberdict
    def wrong_roots(self):
        tag = self.root.tag
        try:
            ckan_type = ckan[publisher_re.match(self.fname).group(1)][self.fname]['extras']['filetype']
            if not ((tag == 'iati-organisations' and ckan_type == '"organisation"') or (tag == 'iati-activities' and ckan_type == '"activity"')):
                return {tag: 1}
        except KeyError:
            pass

    @returns_number
    def file_size(self):
        return os.stat(self.inputfile).st_size

    @returns_numberdict
    def file_size_bins(self):
        file_size = os.stat(self.inputfile).st_size
        if file_size < 1 * 1024 * 1024:
            return {'<1MB': 1}
        elif file_size < 5 * 1024 * 1024:
            return {'1-5MB': 1}
        elif file_size < 10 * 1024 * 1024:
            return {'5-10MB': 1}
        elif file_size < 20 * 1024 * 1024:
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
    strict = False  # (Setting this to true will ignore values that don't follow the schema)
    context = ''

    @returns_numberdict
    def publishers_per_version(self):
        versions = self.aggregated['versions'].keys()
        return dict((v, 1) for v in versions)

    @returns_number
    def publishers(self):
        return 1

    @returns_numberdict
    def publishers_validation(self):
        if 'fail' in self.aggregated['validation']:
            return {'fail': 1}
        else:
            return {'pass': 1}

    @returns_numberdict
    def publisher_has_org_file(self):
        if 'organisation_files' in self.aggregated and self.aggregated['organisation_files'] > 0:
            return {'yes': 1}
        else:
            return {'no': 1}

    # The following two functions have different names to the AllData equivalents
    # This is because the aggregation of the publisher level functions will ignore duplication between publishers

    @returns_number
    @memoize
    def publisher_unique_identifiers(self):
        return len(self.aggregated['iati_identifiers'])

    @returns_numberdict
    def publisher_duplicate_identifiers(self):
        return {k: v for k, v in self.aggregated['iati_identifiers'].items() if v > 1}

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

    def _transaction_alignment(self):
        transaction_months = self.aggregated['transaction_months'].keys()
        if len(transaction_months) == 12:
            return 'Monthly'
        elif len(set(map(lambda x: (int(x) - 1) // 3, transaction_months))) == 4:
            return 'Quarterly'
        elif len(transaction_months) >= 1:
            return 'Annually'
        else:
            return ''

    @no_aggregation
    def date_extremes(self):
        activity_dates = {
            k: list(filter(lambda x: x is not None, map(iso_date_match, v.keys()))) for k, v in self.aggregated['activity_dates'].items()
        }
        min_dates = {k: min(v) for k, v in activity_dates.items() if v}
        max_dates = {k: max(v) for k, v in activity_dates.items() if v}
        overall_min = min(min_dates.values()) if min_dates else None
        overall_max = max(max_dates.values()) if min_dates else None
        return {
            'min': {
                'overall': overall_min,
                'by_type': {k: v for k, v in min_dates.items()}
            },
            'max': {
                'overall': overall_max,
                'by_type': {k: v for k, v in max_dates.items()}
            },
        }


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
        return {self.element.attrib.get('version'): 1}


class AllDataStats(object):
    blank = False

    @returns_number
    def unique_identifiers(self):
        return len(self.aggregated['iati_identifiers'])

    @returns_numberdict
    def duplicate_identifiers(self):
        return {k: v for k, v in self.aggregated['iati_identifiers'].items() if v > 1}
