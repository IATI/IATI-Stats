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

if __name__ == '__main__':
    unittest.main()
