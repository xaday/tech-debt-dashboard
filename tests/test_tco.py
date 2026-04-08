import pytest
from src.tco import calc_tco


def test_calc_tco_sums_all_cost_fields():
    app = {
        "dev_resources": 2,
        "dev_cost_per_resource": 100.0,
        "support_resources": 1,
        "support_cost_per_resource": 80.0,
        "license_cost": 50.0,
        "infra_cost": 30.0,
        "hardware_sw_cost": 20.0,
    }
    # annual_dev = 2*100 = 200
    # annual_support = 1*80 = 80
    # tco = 200 + 80 + 50 + 30 + 20 = 380
    assert calc_tco(app) == pytest.approx(380.0)


def test_calc_tco_zero_when_all_zero():
    app = {
        "dev_resources": 0,
        "dev_cost_per_resource": 0.0,
        "support_resources": 0,
        "support_cost_per_resource": 0.0,
        "license_cost": 0.0,
        "infra_cost": 0.0,
        "hardware_sw_cost": 0.0,
    }
    assert calc_tco(app) == pytest.approx(0.0)


def test_calc_tco_only_license_cost():
    app = {
        "dev_resources": 0,
        "dev_cost_per_resource": 0.0,
        "support_resources": 0,
        "support_cost_per_resource": 0.0,
        "license_cost": 500.0,
        "infra_cost": 0.0,
        "hardware_sw_cost": 0.0,
    }
    assert calc_tco(app) == pytest.approx(500.0)


# Smoke tests for export modules
def _make_assessment():
    return {
        "client": {"name": "Test Corp", "industry": "Finance", "market": "EU", "size": "Large (5000–50000)"},
        "applications": [],
        "infrastructure": [],
        "architecture": {
            "total_dev_labor": 0.0, "total_support_labor": 0.0, "total_ea_labor": 0.0,
            "ea_op_model_maturity": "", "tools_driven_arch": "", "architecture_compliance": "", "duplicate_capabilities": ""
        },
        "people": {
            "total_dev_labor": 0.0, "total_support_labor": 0.0, "total_ea_labor": 0.0,
            "it_ea_skills": "", "org_change_management": "", "team_motivation": "", "genai_intervention": ""
        },
    }


def _make_results():
    return {
        "scores": {"application": 2.0, "infrastructure": 1.5, "architecture": 3.0, "people": 2.5},
        "total_interest": 150.0,
        "total_tco": 500.0,
        "app_details": [],
        "interest_by_dimension": {"application": 80.0, "infrastructure": 20.0, "architecture": 30.0, "people": 20.0},
    }


def test_generate_pdf_returns_bytes():
    from src.export_pdf import generate_pdf
    pdf = generate_pdf(_make_assessment(), _make_results())
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000


def test_generate_ppt_returns_bytes():
    from src.export_ppt import generate_ppt
    ppt = generate_ppt(_make_assessment(), _make_results())
    assert isinstance(ppt, bytes)
    assert len(ppt) > 5000
