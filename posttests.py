from __future__ import unicode_literals
import unittest
import json

class TestAggregatedValues(unittest.TestCase):
    def setUp(self):
        with open('aggregated.json') as fp:
            self.aggregated = json.load(fp)

    def test_activity_sum(self):
        a = self.aggregated
        for key in ['activities_per_year']:
            self.assertEqual(a['activities'], sum(a[key].values()), msg=key)

    def test_publishers_upper_bound(self):
        a = self.aggregated
        for key in ['activities_per_country', 'activities_per_year']:
            for value in a[key].values():
                self.assertLessEqual(value, a['activities'], msg='{0} {1}'.format(key,value))

    def test_activities_upper_bound(self):
        a = self.aggregated
        for key in ['publishers_per_country']:
            for value in a[key].values():
                self.assertLessEqual(value, a['publishers'], msg='{0} {1}'.format(key,value))
        

if __name__ == '__main__':
    unittest.main()
