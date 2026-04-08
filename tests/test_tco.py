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
