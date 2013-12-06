from stats import returns_int

class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    @returns_int
    def activities(self):
        return 1
    pass

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
