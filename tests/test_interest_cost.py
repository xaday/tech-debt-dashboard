import pytest
from src.interest_cost import (
    calc_app_interest,
    calc_infra_interest,
    calc_arch_interest,
    calc_people_interest,
)


def _make_app(doc_score=1, code_quality_score=1, code_dup_score=1,
              integration_score=1, platform_score=1, incident_score=1,
              arch_compliance_score=1, niche_score=1,
              app_type="Custom-Built",
              dev_resources=2, dev_cost_per_resource=100.0,
              support_resources=1, support_cost_per_resource=80.0):
    return {
        "type": app_type,
        "dev_resources": dev_resources,
        "dev_cost_per_resource": dev_cost_per_resource,
        "support_resources": support_resources,
        "support_cost_per_resource": support_cost_per_resource,
        "scores": {
            "documentation": doc_score,
            "code_quality": code_quality_score,
            "code_duplication": code_dup_score,
            "ease_of_integration": integration_score,
            "platform_currency": platform_score,
            "incident_fixes": incident_score,
            "architecture_compliance": arch_compliance_score,
            "niche_skills": niche_score,
        },
    }


def test_calc_app_interest_all_score1_is_zero():
    app = _make_app()  # all scores = 1 → all pcts = 0
    assert calc_app_interest(app) == pytest.approx(0.0)


def test_calc_app_interest_documentation_score5():
    # doc score 5: dev_pct=0.04, support_pct=0.01
    # annual_dev = 2 * 100 = 200, annual_support = 1 * 80 = 80
    # doc interest = 0.04*200 + 0.01*80 = 8.0 + 0.8 = 8.8
    # all other scores = 1 → 0
    app = _make_app(doc_score=5)
    assert calc_app_interest(app) == pytest.approx(8.8)


def test_calc_app_interest_saas_skips_code_metrics():
    # SaaS app: code_quality, code_duplication are not applicable → cost = 0 even if scored
    app = _make_app(app_type="SaaS", code_quality_score=5, code_dup_score=5)
    # Only non-code metrics count. Set all non-code to 1 → 0 interest
    assert calc_app_interest(app) == pytest.approx(0.0)


def _make_infra(component_type="Hardware", eol_score=1, incident_score=1,
                engg_resources=1, engg_cost_per_resource=90.0,
                support_resources=1, support_cost_per_resource=70.0):
    return {
        "component_type": component_type,
        "engg_resources": engg_resources,
        "engg_cost_per_resource": engg_cost_per_resource,
        "support_resources": support_resources,
        "support_cost_per_resource": support_cost_per_resource,
        "scores": {
            "eol": eol_score,
            "incident_fixes": incident_score,
        },
    }


def test_calc_infra_interest_all_score1_is_zero():
    comp = _make_infra()
    assert calc_infra_interest(comp) == pytest.approx(0.0)


def test_calc_infra_interest_hardware_eol_score3():
    # Hardware EOL score 3: age_factor=1.0, engg_pct=0.004, support_pct=0.001
    # annual_engg = 1 * 90 = 90, annual_support = 1 * 70 = 70
    # eol_interest = 1.0 * (0.004*90 + 0.001*70) = 1.0 * (0.36 + 0.07) = 0.43
    comp = _make_infra(component_type="Hardware", eol_score=3)
    assert calc_infra_interest(comp) == pytest.approx(0.43)


def _make_arch(ea_score=1, tools_score=1, arch_compliance_score=1, dup_score=1,
               total_dev_labor=1000.0, total_support_labor=500.0, total_ea_labor=200.0):
    return {
        "total_dev_labor": total_dev_labor,
        "total_support_labor": total_support_labor,
        "total_ea_labor": total_ea_labor,
        "scores": {
            "ea_op_model_maturity": ea_score,
            "tools_driven_arch": tools_score,
            "architecture_compliance": arch_compliance_score,
            "duplicate_capabilities": dup_score,
        },
    }


def test_calc_arch_interest_all_score1_is_zero():
    arch = _make_arch()
    assert calc_arch_interest(arch) == pytest.approx(0.0)


def test_calc_arch_interest_ea_score2():
    # ea_op score 2: dev=0.0075, support=0.0025, ea=0
    # dev_labor=1000, support_labor=500, ea_labor=200
    # interest = 0.0075*1000 + 0.0025*500 + 0*200 = 7.5 + 1.25 = 8.75
    arch = _make_arch(ea_score=2)
    assert calc_arch_interest(arch) == pytest.approx(8.75)


def _make_people(skills_score=1, change_score=1, motivation_score=1, genai_score=1,
                 total_dev_labor=1000.0, total_support_labor=500.0, total_ea_labor=200.0):
    return {
        "total_dev_labor": total_dev_labor,
        "total_support_labor": total_support_labor,
        "total_ea_labor": total_ea_labor,
        "scores": {
            "it_ea_skills": skills_score,
            "org_change_management": change_score,
            "team_motivation": motivation_score,
            "genai_intervention": genai_score,
        },
    }


def test_calc_people_interest_all_score1_is_zero():
    people = _make_people()
    assert calc_people_interest(people) == pytest.approx(0.0)


def test_calc_people_interest_skills_score3():
    # skills score 3: dev=0.008, support=0.002, ea=0.1
    # dev_labor=1000, support_labor=500, ea_labor=200
    # interest = 0.008*1000 + 0.002*500 + 0.1*200 = 8 + 1 + 20 = 29.0
    people = _make_people(skills_score=3)
    assert calc_people_interest(people) == pytest.approx(29.0)
