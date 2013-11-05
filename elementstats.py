from stats import returns_intdict

class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

def element_to_count_dict(e, path, d):
    d[path] = 1
    for child in e:
        element_to_count_dict(child, path+'/'+child.tag, d)
    return d

class ActivityStats(object):
    blank = False

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-activity', {})

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    blank = False

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-organisation', {})
