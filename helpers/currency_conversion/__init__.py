# Script to provide currency conversion functionality

import csv
import os.path
from collections import defaultdict
from decimal import Decimal

currency_values = defaultdict(dict)

# Open exchange rate data and import into a dictionary
fname = os.path.join(os.path.dirname(__file__), "exchange_rates.csv")
with open(fname) as fh:
    for row in csv.DictReader(fh):
        currency = row["Currency"]
        rate = float(row["Rate"])
        year = int(row["Date"][:4])
        currency_values[currency][year] = rate

currency_values = dict(currency_values)


def get_USD_value(input_currency, input_value, year):
    """Returns a USD value based on an inputted ISO currency, an inputted value and a year
    Inputs:
       input_currency -- ISO currency code for the input currency
       input_value -- Currency value
       year -- year, as a string or integer

    Returns:
       Decimal of the USD value. Can be a negative value
    """

    # Attempt to make a USD conversion
    try:
        usd_value = (1 / currency_values[input_currency][int(year)]) * float(input_value)
    except KeyError:
        # Arises if the currency is not in the sheet
        usd_value = 0
    except ZeroDivisionError:
        # Arises if there is no data for the given year - i.e. set as zero for that year
        usd_value = 0

    # Cast to Decimal and return result
    return Decimal(usd_value)
