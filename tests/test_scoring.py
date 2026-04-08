import pytest
from src.scoring import score_metric, score_dimension, detect_tech_debt


def test_score_metric_documentation_score1():
    assert score_metric("application", "documentation", "Updated every release/quarter") == 1


def test_score_metric_documentation_score5():
    assert score_metric("application", "documentation", "Never gets updated/Does not exist") == 5


def test_score_metric_arch_compliance_partially_compliant():
    # Partially Compliant maps to score 3 (not 2)
    assert score_metric("application", "architecture_compliance", "Partially Compliant") == 3


def test_score_metric_infra_eol_score3():
    assert score_metric("infrastructure", "eol", "Component is 0-6 months from EOL.") == 3


def test_score_metric_people_genai_score2():
    assert score_metric("people", "genai_intervention", "Enabled with some GenAI based KM platforms and limited GenAI agents") == 2


def test_score_metric_unknown_option_raises():
    with pytest.raises(ValueError, match="Unknown option"):
        score_metric("application", "documentation", "Not a real option")


def test_score_metric_unknown_metric_raises():
    with pytest.raises(ValueError, match="Unknown metric"):
        score_metric("application", "not_a_metric", "any value")


def test_score_dimension_average_of_scores():
    assert score_dimension([1, 3, 5]) == pytest.approx(3.0)


def test_score_dimension_single_score():
    assert score_dimension([2]) == pytest.approx(2.0)


def test_score_dimension_empty_raises():
    with pytest.raises(ValueError, match="No scores"):
        score_dimension([])


def test_detect_tech_debt_true_by_average():
    # avg=1.5 >= threshold 1.0
    assert detect_tech_debt([1, 2]) is True


def test_detect_tech_debt_true_by_max():
    # avg=1.0 (border), max=2 >= threshold 2.0
    assert detect_tech_debt([1, 1, 2]) is True


def test_detect_tech_debt_single_score_one():
    # score=1 avg=1.0 >= 1.0 → flagged
    assert detect_tech_debt([1]) is True
