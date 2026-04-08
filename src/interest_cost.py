from src.reference_data import (
    APP_INTEREST_PCTS,
    INFRA_EOL_PCTS,
    INFRA_INCIDENT_PCTS,
    ARCH_INTEREST_PCTS,
    PEOPLE_INTEREST_PCTS,
    CODE_METRIC_APP_TYPES,
)

# Metrics not applicable to SaaS/COTS apps (no custom code)
_CODE_ONLY_METRICS = {"code_quality", "code_duplication"}


def calc_app_interest(app: dict) -> float:
    """
    Calculate annual interest cost (€) for one application.

    app must have:
      type: str (application type)
      dev_resources: float
      dev_cost_per_resource: float (€/year)
      support_resources: float
      support_cost_per_resource: float (€/year)
      scores: dict of metric_name → score (int)
    """
    annual_dev = app["dev_resources"] * app["dev_cost_per_resource"]
    annual_support = app["support_resources"] * app["support_cost_per_resource"]
    app_type = app.get("type", "Custom-Built")
    scores = app["scores"]

    total = 0.0
    for metric, pct_table in APP_INTEREST_PCTS.items():
        if metric in _CODE_ONLY_METRICS and app_type not in CODE_METRIC_APP_TYPES:
            continue
        score = scores.get(metric, 1)
        dev_pct, support_pct = pct_table.get(score, (0.0, 0.0))
        total += dev_pct * annual_dev + support_pct * annual_support
    return total


def calc_infra_interest(component: dict) -> float:
    """
    Calculate annual interest cost (€) for one infrastructure component.

    component must have:
      component_type: str (Hardware/Operating System/Middleware/Database/Storage)
      engg_resources: float
      engg_cost_per_resource: float (€/year)
      support_resources: float
      support_cost_per_resource: float (€/year)
      scores: dict with keys 'eol' and 'incident_fixes'
    """
    annual_engg = component["engg_resources"] * component["engg_cost_per_resource"]
    annual_support = component["support_resources"] * component["support_cost_per_resource"]
    component_type = component["component_type"]
    scores = component["scores"]

    eol_score = scores.get("eol", 1)
    eol_table = INFRA_EOL_PCTS.get(component_type, INFRA_EOL_PCTS["Hardware"])
    age_factor, engg_pct, support_pct = eol_table.get(eol_score, (1.0, 0.0, 0.0))
    eol_interest = age_factor * (engg_pct * annual_engg + support_pct * annual_support)

    incident_score = scores.get("incident_fixes", 1)
    engg_inc_pct, support_inc_pct = INFRA_INCIDENT_PCTS.get(incident_score, (0.0, 0.0))
    incident_interest = engg_inc_pct * annual_engg + support_inc_pct * annual_support

    return eol_interest + incident_interest


def calc_arch_interest(arch: dict) -> float:
    """
    Calculate annual interest cost (€) for the architecture dimension.

    arch must have:
      total_dev_labor: float (€/year)
      total_support_labor: float (€/year)
      total_ea_labor: float (€/year)
      scores: dict with ea_op_model_maturity, tools_driven_arch,
              architecture_compliance, duplicate_capabilities
    """
    dev = arch["total_dev_labor"]
    support = arch["total_support_labor"]
    ea = arch["total_ea_labor"]
    scores = arch["scores"]

    ea_score = scores.get("ea_op_model_maturity", 1)

    total = 0.0
    for metric, pct_table in ARCH_INTEREST_PCTS.items():
        # tools_driven_arch and architecture_compliance only apply when ea_score <= 3
        if metric in ("tools_driven_arch", "architecture_compliance") and ea_score > 3:
            continue
        score = scores.get(metric, 1)
        dev_pct, support_pct, ea_pct = pct_table.get(score, (0.0, 0.0, 0.0))
        total += dev_pct * dev + support_pct * support + ea_pct * ea
    return total


def calc_people_interest(people: dict) -> float:
    """
    Calculate annual interest cost (€) for the people dimension.

    people must have:
      total_dev_labor: float (€/year)
      total_support_labor: float (€/year)
      total_ea_labor: float (€/year)
      scores: dict with it_ea_skills, org_change_management,
              team_motivation, genai_intervention
    """
    dev = people["total_dev_labor"]
    support = people["total_support_labor"]
    ea = people["total_ea_labor"]
    scores = people["scores"]

    total = 0.0
    for metric, pct_table in PEOPLE_INTEREST_PCTS.items():
        score = scores.get(metric, 1)
        dev_pct, support_pct, ea_pct = pct_table.get(score, (0.0, 0.0, 0.0))
        total += dev_pct * dev + support_pct * support + ea_pct * ea
    return total
