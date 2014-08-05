from stats.common.decorators import *
from stats.common import transaction_date, iso_date_match
from collections import defaultdict
import datetime
from hashlib import md5

class PublisherStats(object):
    blank = False

    @no_aggregation
    def most_recent_transaction_date(self):
        nonfuture_transaction_dates = filter(lambda x: x is not None and x <= datetime.date.today(),
            map(iso_date_match, self.aggregated['transaction_dates'].keys()))
        if nonfuture_transaction_dates:
            return unicode(max(nonfuture_transaction_dates))

    @no_aggregation
    def latest_transaction_date(self):
        transaction_dates = filter(lambda x: x is not None,
            map(iso_date_match, self.aggregated['transaction_dates'].keys()))
        if transaction_dates:
            return unicode(max(transaction_dates))

    @no_aggregation
    def transaction_dates_hash(self):
        return md5(unicode(self.aggregated['transaction_dates'].keys())).hexdigest()


class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    @returns_numberdict
    def transaction_dates(self):
        out = defaultdict(int)
        for transaction in self.element.findall('transaction'):
            date = transaction_date(transaction)
            out[unicode(date)] += 1
        return out

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
        
class AllDataStats(object):
    pass

