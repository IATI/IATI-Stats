from collections import defaultdict

from dashboard import element_to_count_dict, returns_numberdict


class PublisherStats(object):
    pass


class ActivityFileStats(object):
    pass


class ActivityStats(object):
    blank = False

    @returns_numberdict
    def elements(self):
        return element_to_count_dict(self.element, "iati-activity", {})

    @returns_numberdict
    def elements_total(self):
        return element_to_count_dict(self.element, "iati-activity", defaultdict(int), True)


class OrganisationFileStats(object):
    pass


class OrganisationStats(object):
    blank = False

    @returns_numberdict
    def elements(self):
        return element_to_count_dict(self.element, "iati-organisation", {})

    @returns_numberdict
    def elements_total(self):
        return element_to_count_dict(self.element, "iati-organisation", defaultdict(int), True)


class AllDataStats(object):
    pass
