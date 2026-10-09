from stats.analytics import PublisherWithHistoryStats


def test_ignore_none():
    # We calculate True/False ignoreing the Nones
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}},
        }
    }
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.25,
        "basic": 0,
        "financials": 0,
        "advanced": 0,
    }


def test_average_scenarios():
    # We average scenario A and B scores
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}, "B": {"True": 7, "False": 9, "None": 11}},
        }
    }
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.34375,
        "basic": 0,
        "financials": 0,
        "advanced": 0,
    }


def test_average_features():
    # We average 1.1 and 1.2 scores
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}, "B": {"True": 7, "False": 9, "None": 11}},
            "1.2_feature": {
                "C": {"True": 13, "False": 19, "None": 15},
            },
        }
    }
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.375,
        "basic": 0,
        "financials": 0,
        "advanced": 0,
    }


def test_separate_components():
    # We calculate 1.X and 2.X scores separately
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}, "B": {"True": 7, "False": 9, "None": 11}},
            "1.2_feature": {
                "C": {"True": 13, "False": 19, "None": 15},
            },
            "2.2_feature": {
                "D": {"True": 23, "False": 27, "None": 25},
            },
        }
    }
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.375,
        "basic": 0.46,
        "financials": 0,
        "advanced": 0,
    }


def test_all_irrelevant():
    # Scenarios that are all irrelevant (all Nones) should be excluded from the average
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}, "B": {"True": 0, "False": 0, "None": 11}},
        }
    }
    # Should be 25%, not 62.5%
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.25,
        "basic": 0,
        "financials": 0,
        "advanced": 0,
    }


def test_all_irrelevant_feature():
    # Scenarios that are all irrelevant (all Nones) should be excluded from the average
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 1, "False": 3, "None": 5}},
            "1.2_feature": {"B": {"True": 0, "False": 0, "None": 11}},
        }
    }
    # Should be 25%, not 62.5%
    assert pwhs.comprehensiveness_new_by_component() == {
        "organisation": 0.25,
        "basic": 0,
        "financials": 0,
        "advanced": 0,
    }


def test_all_irrelevant_component():
    # Components that are all irrelevant score 0
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {
        "gherkin_tests_hierarchy_exclusions": {
            "1.1_feature": {"A": {"True": 0, "False": 0, "None": 11}},
        }
    }
    assert pwhs.comprehensiveness_new_by_component() == {"organisation": 0, "basic": 0, "financials": 0, "advanced": 0}
