from unittest.mock import MagicMock

import pytest

from stats.analytics import PublisherWithHistoryStats


def test_individual_component():
    pwhs = PublisherWithHistoryStats()
    assert pwhs._assessment_new_individual_component([2, 4, 6], 5) == {
        "category_number": 2,
        "category": "very_good",
        "value": 5,  # this is always the value we pass in as the second parameter
    }
    assert pwhs._assessment_new_individual_component([2, 4, 6], 7) == {
        "category_number": 3,
        "category": "excellent",
        "value": 7,
    }
    # If the score is equal to a threshold, it gets the higher category
    assert pwhs._assessment_new_individual_component([2, 4, 6], 2) == {
        "category_number": 1,
        "category": "good",
        "value": 2,
    }
    # If thresholds are repeated, it's only possible to score above/below
    assert pwhs._assessment_new_individual_component([2, 2, 2], 1) == {
        "category_number": 0,
        "category": "needs_improvement",
        "value": 1,
    }
    assert pwhs._assessment_new_individual_component([2, 2, 2], 2) == {
        "category_number": 3,
        "category": "excellent",
        "value": 2,
    }


def test_by_component():
    pwhs = PublisherWithHistoryStats()
    pwhs._assessment_new_by_component(
        thresholds_by_component={"a": [2, 4, 6], "b": [1, 3, 3]}, scores_by_component={"a": 5, "b": 2}
    ) == {
        "components": {
            "a": {"category_number": 2, "category": "very_good", "value": 5},
            "b": {"category_number": 1, "category": "good", "value": 2},
        },
        "category_number": 1,  # This should always be equal to the lowest component category number
        "category": "good",
    }
    pwhs._assessment_new_by_component(
        thresholds_by_component={"a": [2, 4, 6], "b": [1, 3, 3]}, scores_by_component={"a": 7, "b": 3}
    ) == {
        "components": {
            "a": {"category_number": 3, "category": "excellent", "value": 7},
            "b": {"category_number": 2, "category": "very_good", "value": 3},
        },
        "category_number": 1,
        "category": "very_good",
    }


def test_comprehensiveness():
    pwhs = PublisherWithHistoryStats()
    pwhs.aggregated = {}
    pwhs.comprehensiveness_new_by_component = MagicMock(
        return_value={
            "advanced": 0.35714285714285715,
            "basic": 0.9743589743589743,
            "financials": 0.6666666666666666,
            "organisation": 0.9444444444444444,
        }
    )
    assert pwhs._assessment_new_comprehensiveness() == {
        "components": {
            "basic": {"category_number": 2, "category": "very_good", "value": 0.9743589743589743},
            "organisation": {"category_number": 3, "category": "excellent", "value": 0.9444444444444444},
            "financials": {"category_number": 1, "category": "good", "value": 0.6666666666666666},
            "advanced": {"category_number": 1, "category": "good", "value": 0.35714285714285715},
        },
        "category_number": 1,
        "category": "good",
    }


def test_coverage():
    # TODO
    # pwhs = PublisherWithHistoryStats()
    pass


def test_timeliness():
    # TODO
    # pwhs = PublisherWithHistoryStats()
    pass


def test_availability():
    # TODO
    # pwhs = PublisherWithHistoryStats()
    pass


@pytest.mark.parametrize(
    "category_numbers,category_number_out,category_out",
    [
        ([3, 3, 3, 3], 3, "excellent"),
        ([0, 1, 2, 3], 0, "needs_improvement"),
        ([1, 2, 1, 2], 1, "good"),
        ([0, 0, 0, 0], 0, "needs_improvement"),
        ([2, 2, 2, 3], 2, "very_good"),
    ],
)
def test_asssesment(category_numbers, category_number_out, category_out):
    pwhs = PublisherWithHistoryStats()
    pwhs._assessment_new_comprehensiveness = MagicMock(return_value={"category_number": category_numbers[0]})
    pwhs._assessment_new_coverage = MagicMock(return_value={"category_number": category_numbers[1]})
    pwhs._assessment_new_timeliness = MagicMock(return_value={"category_number": category_numbers[2]})
    pwhs._assessment_new_availability = MagicMock(return_value={"category_number": category_numbers[3]})
    assessment = pwhs.assessment_new()
    assert assessment["dimensions"]["comprehensiveness"] == {"category_number": category_numbers[0]}
    assert assessment["dimensions"]["coverage"] == {"category_number": category_numbers[1]}
    assert assessment["dimensions"]["timeliness"] == {"category_number": category_numbers[2]}
    assert assessment["dimensions"]["availability"] == {"category_number": category_numbers[3]}
    assert assessment["overall"]["category_number"] == category_number_out
    assert assessment["overall"]["category"] == category_out
    pwhs._assessment_new_comprehensiveness.assert_called_with()
    pwhs._assessment_new_coverage.assert_called_with()
    pwhs._assessment_new_timeliness.assert_called_with()
    pwhs._assessment_new_availability.assert_called_with()
