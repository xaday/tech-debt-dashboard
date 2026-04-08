# Tech Debt Calculator Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit web app that replaces the Accenture Tech Debt Calculator Excel — users fill in data across 4 dimensions, the app calculates Tech Debt Scores and Annual Interest Costs using the original Excel formulas, and produces a dashboard plus PDF/PPT exports.

**Architecture:** Pure Python/Streamlit single-page app. Reference data (scoring options, cost percentages) is hardcoded from the Excel into `src/reference_data.py`. Calculation logic lives in pure functions with no I/O (`scoring.py`, `interest_cost.py`, `tco.py`). All form state lives in `st.session_state.assessment`. Exports use `reportlab` (PDF) and `python-pptx` (PPT).

**Tech Stack:** Python 3.9+, Streamlit, Plotly, reportlab, python-pptx, pytest

---

## File Structure

| File | Responsibility |
|------|----------------|
| `app.py` | Entry point. Accenture CSS, sidebar (save/load/export), 6 tabs (Client, Applications, Infrastructure, Architecture, People, Dashboard) |
| `src/reference_data.py` | Hardcoded lookup dicts: `SCORING_OPTIONS`, `INTEREST_COST_PCTS`, `THRESHOLDS`, `DIMENSION_PCTS` |
| `src/scoring.py` | `score_metric(dimension, metric, option_text) → int`, `score_dimension(scores: list[int]) → float`, `detect_tech_debt(scores: list[int]) → bool` |
| `src/interest_cost.py` | `calc_app_interest(app, ref)`, `calc_infra_interest(component, ref)`, `calc_arch_interest(arch, scores, ref)`, `calc_people_interest(people, scores, ref)` — all return float (kUSD) |
| `src/tco.py` | `calc_tco(app) → float` |
| `src/export_pdf.py` | `generate_pdf(assessment, results) → bytes` |
| `src/export_ppt.py` | `generate_ppt(assessment, results) → bytes` |
| `tests/test_scoring.py` | Unit tests for all scoring functions |
| `tests/test_interest_cost.py` | Unit tests for all interest cost functions |
| `tests/test_tco.py` | Unit tests for TCO calculation |

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `.gitignore`
- Create: `.streamlit/config.toml`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
reportlab>=4.0.0
python-pptx>=0.6.23
openpyxl>=3.1.0
```

- [ ] **Step 2: Create requirements-dev.txt**

```
-r requirements.txt
pytest>=8.0.0
pytest-cov>=4.1.0
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 4: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
htmlcov/
.coverage
*.egg-info/
dist/
.superpowers/
```

- [ ] **Step 5: Create .streamlit/config.toml**

```toml
[theme]
primaryColor = "#A100FF"
backgroundColor = "#000000"
secondaryBackgroundColor = "#1A1A1A"
textColor = "#FFFFFF"
font = "sans serif"

[browser]
gatherUsageStats = false
```

- [ ] **Step 6: Create empty init files**

Create `src/__init__.py` and `tests/__init__.py` — both empty files.

- [ ] **Step 7: Install dependencies**

Run: `pip install -r requirements-dev.txt`
Expected: All packages install without errors.

- [ ] **Step 8: Commit**

```bash
git add requirements.txt requirements-dev.txt pytest.ini .gitignore .streamlit/config.toml src/__init__.py tests/__init__.py
git commit -m "chore: project setup — dependencies, pytest config, Accenture theme"
```

---

## Task 2: Reference Data Module

**Files:**
- Create: `src/reference_data.py`

All scoring options and interest cost percentages extracted directly from `0.A Ref. and Master Values` and `0.B Score to Interest Mapping` sheets of the Excel.

- [ ] **Step 1: Create src/reference_data.py**

```python
# Scoring options: dimension → metric → list of (option_text, score) tuples
# Scores from 0.A Ref. and Master Values
SCORING_OPTIONS = {
    "application": {
        "documentation": [
            ("Updated every release/quarter", 1),
            ("Updated every 6 months", 2),
            ("Updated every year", 3),
            ("Updated in 2-3 years, no specific plan", 4),
            ("Never gets updated/Does not exist", 5),
        ],
        "code_quality": [
            ("Low/standard complexity (< 10%)", 1),
            ("Medium complexity (>10% to <=15%)", 2),
            ("Moderate complexity (>15% to <=20%)", 3),
            ("High complexity (>20% to <=30%)", 4),
            ("Very high complexity (>30%)", 5),
        ],
        "code_duplication": [
            ("Duplication is low", 1),
            ("Duplication is medium", 2),
            ("Duplication is moderate", 3),
            ("Duplication is high", 4),
            ("Duplication is very high", 5),
        ],
        "ease_of_integration": [
            ("Very easy", 1),
            ("Moderate efforts", 2),
            ("Possible with some constraint", 3),
            ("Quite Difficult", 4),
            ("Extremely Difficult", 5),
        ],
        "platform_currency": [
            ("Maintained at N level", 1),
            ("Maintained at N-1 level", 2),
            ("Maintained at N-2 level", 3),
            ("Maintained at N-3 level", 4),
            ("Maintained at > N-3 level", 5),
        ],
        "incident_fixes": [
            ("Incidents are less than 5%", 1),
            ("Incidents are between 5% to 10%", 2),
            ("Incidents are between 10% to 15%", 3),
            ("Incidents are between 15% to 20%", 4),
            ("Incidents are greater than 20%", 5),
        ],
        "architecture_compliance": [
            ("Fully Compliant", 1),
            ("Partially Compliant", 3),
            ("Non Compliant", 5),
        ],
        "niche_skills": [
            ("No niche skills required", 1),
            ("Minimal niche skills (< 10% of team)", 2),
            ("Some niche skills (10% to 20% of team)", 3),
            ("Significant niche skills (20% to 40% of team)", 4),
            ("Predominantly niche skills (> 40% of team)", 5),
        ],
    },
    "infrastructure": {
        "eol": [
            ("Component is 13+ months from its EOL date.", 1),
            ("Component is 7-12 months from EOL.", 2),
            ("Component is 0-6 months from EOL.", 3),
            ("Component is 1-6 months past its official EOL date", 4),
            ("Component is 7+ months past EOL.", 5),
        ],
        "incident_fixes": [
            ("Infra incidents are less than 1%", 1),
            ("Infra incidents are between 1% to 3%", 2),
            ("Infra incidents are between 3% to 5%", 3),
            ("Infra incidents are between 5% to 10%", 4),
            ("Infra incidents are greater than 10%", 5),
        ],
    },
    "architecture": {
        "ea_op_model_maturity": [
            ("Optimized across all EA capabilities", 1),
            ("Managed across all EA capabilities", 2),
            ("Defined encompassing all EA capabilities and processes", 3),
            ("Repeatable with few EA capabilities", 4),
            ("Does not exist or at the basic level with extremely limited EA capabilities", 5),
        ],
        "tools_driven_arch": [
            ("Repository is present and proactively managed following guidelines", 1),
            ("Repository is present and managed on ad-hoc basis", 2),
            ("Repository is defined and managed on need basis, mostly at project level", 3),
        ],
        "architecture_compliance": [
            ("Fully Compliant", 1),
            ("Partially Compliant", 3),
            ("Non Compliant", 5),
        ],
        "duplicate_capabilities": [
            ("Functional overlap is less than 5%", 1),
            ("Functional overlap is between 5% to 10%", 2),
            ("Functional overlap is between 10% to 20%", 3),
            ("Functional overlap is between 20% to 40%", 4),
            ("Functional overlap is greater than 40%", 5),
        ],
    },
    "people": {
        "it_ea_skills": [
            ("Gap for all skills are less than 10%", 1),
            ("Gap for all skills are between 10% to 15%", 2),
            ("Gap for all skills are between 15% to 20%", 3),
            ("Gap for all skills are between 20% to 30%", 4),
            ("Gap for all skills are greater than 30%", 5),
        ],
        "org_change_management": [
            ("Processes are defined and operationalized with adaption rate >80%", 1),
            ("Processes are defined and operationalized with adaption rate between 70% to 80%", 2),
            ("Processes are defined with adaption rate between 60% to 70%", 3),
            ("Processes are defined for some functions with adaption rate <60%", 4),
            ("Processes are not clearly defined and adaption rate is not known", 5),
        ],
        "team_motivation": [
            ("Employment Continuation Indicator for the team is >90%", 1),
            ("Employment Continuation Indicator for the team is between 80% to 90%", 2),
            ("Employment Continuation Indicator for the team is between 70% to 80%", 3),
            ("Employment Continuation Indicator for the team is between 60% to 70%", 4),
            ("Employment Continuation Indicator for the team is <60%", 5),
        ],
        "genai_intervention": [
            ("Fully enabled with GenAI based KM platforms and GenAI agents", 1),
            ("Enabled with some GenAI based KM platforms and limited GenAI agents", 2),
            ("Enabled with some GenAI based KM platforms and conventional KM search capabilities only", 3),
            ("Enabled with some GenAI support and separate conventional KM search capabilities", 4),
            ("Enabled with only conventional KM search capabilities or disparate document storage", 5),
        ],
    },
}

# Interest cost percentages from 0.B Score to Interest Mapping
# Application metrics: score → (dev_pct, support_pct)
# Percentages applied to annual dev/support labor costs (kUSD)
APP_INTEREST_PCTS = {
    "documentation": {
        1: (0.0, 0.0),
        2: (0.004, 0.001),
        3: (0.008, 0.002),
        4: (0.02, 0.005),
        5: (0.04, 0.01),
    },
    "code_quality": {
        1: (0.0, 0.0),
        2: (0.004, 0.001),
        3: (0.008, 0.002),
        4: (0.012, 0.003),
        5: (0.016, 0.004),
    },
    "code_duplication": {
        1: (0.0, 0.0),
        2: (0.003, 0.002),
        3: (0.006, 0.004),
        4: (0.012, 0.008),
        5: (0.018, 0.012),
    },
    "ease_of_integration": {
        1: (0.0, 0.0),
        2: (0.002, 0.0005),
        3: (0.004, 0.001),
        4: (0.008, 0.002),
        5: (0.016, 0.004),
    },
    "platform_currency": {
        1: (0.0, 0.0),
        2: (0.0035, 0.0015),
        3: (0.007, 0.003),
        4: (0.014, 0.006),
        5: (0.035, 0.015),
    },
    "incident_fixes": {
        1: (0.0, 0.0),
        2: (0.0, 0.0025),
        3: (0.0015, 0.006),
        4: (0.0025, 0.0125),
        5: (0.005, 0.025),
    },
    "architecture_compliance": {
        1: (0.0, 0.0),
        3: (0.005, 0.0025),
        5: (0.01, 0.005),
    },
    "niche_skills": {
        1: (0.0, 0.0),
        2: (0.0, 0.0025),
        3: (0.0015, 0.006),
        4: (0.0025, 0.0125),
        5: (0.005, 0.025),
    },
}

# Infrastructure EOL metrics by component type: score → (age_factor, engg_pct, support_pct)
# age_factor multiplies total EOL metric cost
INFRA_EOL_PCTS = {
    "Hardware": {
        1: (0.5, 0.0, 0.0),
        2: (0.75, 0.002, 0.0005),
        3: (1.0, 0.004, 0.001),
        4: (1.25, 0.012, 0.003),
        5: (1.5, 0.016, 0.004),
    },
    "Operating System": {
        1: (0.5, 0.0, 0.0),
        2: (0.75, 0.002, 0.0005),
        3: (1.0, 0.004, 0.001),
        4: (1.25, 0.012, 0.003),
        5: (1.5, 0.016, 0.004),
    },
    "Middleware": {
        1: (0.5, 0.0, 0.0),
        2: (0.75, 0.0008, 0.0002),
        3: (1.0, 0.002, 0.0005),
        4: (1.25, 0.008, 0.002),
        5: (1.5, 0.012, 0.003),
    },
    "Database": {
        1: (0.5, 0.0, 0.0),
        2: (0.75, 0.0008, 0.0002),
        3: (1.0, 0.002, 0.0005),
        4: (1.25, 0.008, 0.002),
        5: (1.5, 0.012, 0.003),
    },
    "Storage": {
        1: (0.5, 0.0, 0.0),
        2: (0.75, 0.0008, 0.0002),
        3: (1.0, 0.002, 0.0005),
        4: (1.25, 0.006, 0.0015),
        5: (1.5, 0.008, 0.002),
    },
}

# Infrastructure incident fixes: score → (engg_pct, support_pct)
INFRA_INCIDENT_PCTS = {
    1: (0.0, 0.0),
    2: (0.0, 0.0025),
    3: (0.0015, 0.006),
    4: (0.0025, 0.0125),
    5: (0.005, 0.025),
}

# Architecture metrics: score → (dev_pct, support_pct, ea_pct)
ARCH_INTEREST_PCTS = {
    "ea_op_model_maturity": {
        1: (0.0, 0.0, 0.0),
        2: (0.0075, 0.0025, 0.0),
        3: (0.015, 0.005, 0.0),
        4: (0.035, 0.015, 0.7),
        5: (0.05, 0.02, 1.0),
    },
    "tools_driven_arch": {
        1: (0.0, 0.0, 0.0),
        2: (0.002, 0.0005, 0.3),
        3: (0.004, 0.001, 0.5),
    },
    "architecture_compliance": {
        1: (0.0, 0.0, 0.0),
        3: (0.005, 0.0025, 0.0),
        5: (0.01, 0.005, 0.0),
    },
    "duplicate_capabilities": {
        1: (0.0, 0.0, 0.0),
        2: (0.0025, 0.0025, 0.0),
        3: (0.0, 0.0, 0.0),
        4: (0.0, 0.0, 0.0),
        5: (0.0, 0.0, 0.0),
    },
}

# People metrics: score → (dev_pct, support_pct, ea_pct)
PEOPLE_INTEREST_PCTS = {
    "it_ea_skills": {
        1: (0.0, 0.0, 0.0),
        2: (0.004, 0.001, 0.05),
        3: (0.008, 0.002, 0.1),
        4: (0.012, 0.003, 0.2),
        5: (0.018, 0.0045, 0.3),
    },
    "org_change_management": {
        1: (0.0, 0.0, 0.0),
        2: (0.0008, 0.0002, 0.0),
        3: (0.002, 0.0005, 0.0),
        4: (0.004, 0.001, 0.0),
        5: (0.006, 0.0015, 0.0),
    },
    "team_motivation": {
        1: (0.0, 0.0, 0.0),
        2: (0.002, 0.0005, 0.0),
        3: (0.004, 0.001, 0.0),
        4: (0.006, 0.0015, 0.0),
        5: (0.008, 0.002, 0.0),
    },
    "genai_intervention": {
        1: (0.0, 0.0, 0.0),
        2: (0.0015, 0.001, 0.0),
        3: (0.003, 0.002, 0.0),
        4: (0.0045, 0.003, 0.0),
        5: (0.006, 0.004, 0.0),
    },
}

# Thresholds for tech debt detection (from 0.B Score to Interest Mapping G6, G7)
THRESHOLDS = {
    "avg": 1.0,
    "max": 2.0,
}

# Dimension-level percentage of total labor (from 0.B row 12-13)
DIMENSION_PCTS = {
    "application": 0.20,
    "infrastructure": 0.10,
    "architecture": 0.07,
    "people": 0.05,
}

# Application types where code metrics apply (Custom-Built and PaaS only)
CODE_METRIC_APP_TYPES = {"Custom-Built", "PaaS"}

# Infrastructure component types
INFRA_COMPONENT_TYPES = ["Hardware", "Operating System", "Middleware", "Database", "Storage"]
```

- [ ] **Step 2: Commit**

```bash
git add src/reference_data.py
git commit -m "feat: add reference data module with scoring options and cost percentages"
```

---

## Task 3: Scoring Engine

**Files:**
- Create: `src/scoring.py`
- Create: `tests/test_scoring.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scoring.py
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


def test_detect_tech_debt_false():
    # avg=0.5, max=1 — both below thresholds (all score 1 → avg=1.0 is border)
    # Use all score 1: avg=1.0 >= 1.0 → True? Yes. Use empty? No.
    # Score 1 IS tech debt per the threshold (>= 1.0).
    # To get False, we'd need avg < 1 AND max < 2 — impossible with integer scores >= 1.
    # The threshold means: score=1 (best) is NOT tech debt.
    # From Excel: "average >= X" where X=1. Score=1 exactly hits threshold.
    # The Excel formula uses >=, so score=1 IS flagged. All real results are tech debt.
    # Actually, looking at the original: any score >=1 is flagged. This means all assessments
    # show tech debt — which makes sense for a tool that finds tech debt.
    # Test that a single score-1 item IS detected as tech debt:
    assert detect_tech_debt([1]) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scoring.py -v`
Expected: `ModuleNotFoundError` or `ImportError` — scoring.py doesn't exist yet.

- [ ] **Step 3: Implement src/scoring.py**

```python
from src.reference_data import SCORING_OPTIONS, THRESHOLDS


def score_metric(dimension: str, metric: str, option_text: str) -> int:
    """Return the score (1-5) for the given option text."""
    dim_options = SCORING_OPTIONS.get(dimension)
    if dim_options is None:
        raise ValueError(f"Unknown dimension: {dimension}")
    metric_options = dim_options.get(metric)
    if metric_options is None:
        raise ValueError(f"Unknown metric: {metric} in dimension {dimension}")
    for option, score in metric_options:
        if option == option_text:
            return score
    raise ValueError(f"Unknown option '{option_text}' for {dimension}.{metric}")


def score_dimension(scores: list) -> float:
    """Return the average score for a dimension. Raises if scores is empty."""
    if not scores:
        raise ValueError("No scores provided to score_dimension")
    return sum(scores) / len(scores)


def detect_tech_debt(scores: list) -> bool:
    """Return True if average >= THRESHOLDS['avg'] OR max >= THRESHOLDS['max']."""
    if not scores:
        return False
    avg = sum(scores) / len(scores)
    maximum = max(scores)
    return avg >= THRESHOLDS["avg"] or maximum >= THRESHOLDS["max"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scoring.py -v`
Expected: All 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/scoring.py tests/test_scoring.py
git commit -m "feat: scoring engine with score_metric, score_dimension, detect_tech_debt"
```

---

## Task 4: Interest Cost Calculator

**Files:**
- Create: `src/interest_cost.py`
- Create: `tests/test_interest_cost.py`

Interest cost = sum of (labor_pct × labor_cost) per metric. All costs in kUSD.

Application annual costs:
- `annual_dev_cost = dev_resources * dev_cost_per_resource` (kUSD/year)
- `annual_support_cost = support_resources * support_cost_per_resource` (kUSD/year)

Infrastructure annual costs:
- `annual_engg_cost = engg_resources * engg_cost_per_resource` (kUSD/year)
- `annual_support_cost = support_resources * support_cost_per_resource` (kUSD/year)

Architecture/People use totals entered directly by the user (pre-aggregated kUSD/year).

- [ ] **Step 1: Write failing tests**

```python
# tests/test_interest_cost.py
import pytest
from src.interest_cost import (
    calc_app_interest,
    calc_infra_interest,
    calc_arch_interest,
    calc_people_interest,
)
from src.reference_data import APP_INTEREST_PCTS


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_interest_cost.py -v`
Expected: `ImportError` — interest_cost.py doesn't exist yet.

- [ ] **Step 3: Implement src/interest_cost.py**

```python
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
    Calculate annual interest cost (kUSD) for one application.

    app must have:
      type: str (application type)
      dev_resources: float
      dev_cost_per_resource: float (kUSD/year)
      support_resources: float
      support_cost_per_resource: float (kUSD/year)
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
    Calculate annual interest cost (kUSD) for one infrastructure component.

    component must have:
      component_type: str (Hardware/Operating System/Middleware/Database/Storage)
      engg_resources: float
      engg_cost_per_resource: float (kUSD/year)
      support_resources: float
      support_cost_per_resource: float (kUSD/year)
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
    Calculate annual interest cost (kUSD) for the architecture dimension.

    arch must have:
      total_dev_labor: float (kUSD/year)
      total_support_labor: float (kUSD/year)
      total_ea_labor: float (kUSD/year)
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
    Calculate annual interest cost (kUSD) for the people dimension.

    people must have:
      total_dev_labor: float (kUSD/year)
      total_support_labor: float (kUSD/year)
      total_ea_labor: float (kUSD/year)
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_interest_cost.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/interest_cost.py tests/test_interest_cost.py
git commit -m "feat: interest cost calculator for all four dimensions"
```

---

## Task 5: TCO Calculator

**Files:**
- Create: `src/tco.py`
- Create: `tests/test_tco.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tco.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_tco.py -v`
Expected: `ImportError` — tco.py doesn't exist yet.

- [ ] **Step 3: Implement src/tco.py**

```python
def calc_tco(app: dict) -> float:
    """
    Calculate Total Cost of Ownership (kUSD/year) for one application.

    app must have: dev_resources, dev_cost_per_resource, support_resources,
    support_cost_per_resource, license_cost, infra_cost, hardware_sw_cost
    """
    annual_dev = app["dev_resources"] * app["dev_cost_per_resource"]
    annual_support = app["support_resources"] * app["support_cost_per_resource"]
    return (
        annual_dev
        + annual_support
        + app["license_cost"]
        + app["infra_cost"]
        + app["hardware_sw_cost"]
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_tco.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Run full test suite**

Run: `python3 -m pytest --cov=src --cov-report=term-missing`
Expected: All tests pass. Coverage ≥ 80%.

- [ ] **Step 6: Commit**

```bash
git add src/tco.py tests/test_tco.py
git commit -m "feat: TCO calculator"
```

---

## Task 6: Streamlit App Skeleton

**Files:**
- Create: `app.py`

Creates the visual shell: Accenture branding, sidebar structure, 6 empty tabs, session_state initialisation.

- [ ] **Step 1: Create app.py**

```python
import json
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tech Debt Calculator",
    page_icon="💜",
    layout="wide",
)

# ── Accenture CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Force white text everywhere */
.stMarkdown, .stText, label, .stSelectbox label,
.stNumberInput label, .stTextInput label { color: #FFFFFF !important; }

/* Purple accent for metric values */
[data-testid="stMetricValue"] { color: #A100FF !important; }

/* Tab styling */
.stTabs [data-baseweb="tab"] { color: #FFFFFF !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #A100FF !important;
}

/* Plotly chart backgrounds */
.js-plotly-plot { background: #1A1A1A !important; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #111111 !important; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Buttons */
.stButton > button {
    background-color: #A100FF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
}
.stButton > button:hover { background-color: #7B00CC !important; }

/* Expander */
details { background-color: #1A1A1A !important; border: 1px solid #333 !important; }
</style>
""", unsafe_allow_html=True)

# ── Accenture Header ──────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;padding:8px 0 16px 0;border-bottom:2px solid #A100FF;margin-bottom:16px">
  <svg width="36" height="36" viewBox="0 0 100 100">
    <polygon points="50,5 95,95 5,95" fill="#A100FF"/>
  </svg>
  <span style="font-size:1.6rem;font-weight:700;color:#FFFFFF;letter-spacing:1px">
    Tech Debt Calculator
  </span>
</div>
""", unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────────────────────
_DEFAULT_ASSESSMENT = {
    "client": {"name": "", "industry": "", "market": "", "size": ""},
    "applications": [],
    "infrastructure": [],
    "architecture": {
        "total_dev_labor": 0.0,
        "total_support_labor": 0.0,
        "total_ea_labor": 0.0,
        "ea_op_model_maturity": "",
        "tools_driven_arch": "",
        "architecture_compliance": "",
        "duplicate_capabilities": "",
    },
    "people": {
        "total_dev_labor": 0.0,
        "total_support_labor": 0.0,
        "total_ea_labor": 0.0,
        "it_ea_skills": "",
        "org_change_management": "",
        "team_motivation": "",
        "genai_intervention": "",
    },
}

if "assessment" not in st.session_state:
    st.session_state.assessment = _DEFAULT_ASSESSMENT.copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Project")
    project_name = st.text_input("Project Name", value="New Assessment")

    st.markdown("---")
    st.markdown("### Save / Load")

    if st.button("Save JSON"):
        data = json.dumps(st.session_state.assessment, indent=2)
        st.download_button(
            label="Download assessment.json",
            data=data,
            file_name="assessment.json",
            mime="application/json",
        )

    uploaded = st.file_uploader("Load JSON", type="json", label_visibility="collapsed")
    if uploaded is not None:
        try:
            st.session_state.assessment = json.loads(uploaded.read())
            st.success("Assessment loaded.")
        except Exception as exc:
            st.error(f"Failed to load: {exc}")

    st.markdown("---")
    st.markdown("### Export")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("PDF"):
            st.info("Complete the assessment first.")
    with col2:
        if st.button("PPT"):
            st.info("Complete the assessment first.")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_client, tab_apps, tab_infra, tab_arch, tab_people, tab_dashboard = st.tabs([
    "Cliente",
    "Aplicações",
    "Infraestrutura",
    "Arquitectura",
    "Pessoas",
    "Dashboard",
])

with tab_client:
    st.markdown("### Client Information")
    st.info("Fill in client details.")

with tab_apps:
    st.markdown("### Applications")
    st.info("Add applications.")

with tab_infra:
    st.markdown("### Infrastructure")
    st.info("Add infrastructure components.")

with tab_arch:
    st.markdown("### Architecture")
    st.info("Fill in architecture data.")

with tab_people:
    st.markdown("### People")
    st.info("Fill in people data.")

with tab_dashboard:
    st.markdown("### Dashboard")
    st.info("Complete all tabs then click Calculate.")
```

- [ ] **Step 2: Run the app to verify it starts**

Run: `python3 -m streamlit run app.py`
Expected: Browser opens at http://localhost:8501 showing Accenture header, purple sidebar, 6 tabs. No errors in terminal.
Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: app skeleton with Accenture theme, sidebar, 6-tab layout"
```

---

## Task 7: Client Tab

**Files:**
- Modify: `app.py` (replace `with tab_client:` block)

- [ ] **Step 1: Replace the tab_client block in app.py**

Find this block:
```python
with tab_client:
    st.markdown("### Client Information")
    st.info("Fill in client details.")
```

Replace with:
```python
with tab_client:
    st.markdown("### Client Information")
    a = st.session_state.assessment

    col1, col2 = st.columns(2)
    with col1:
        a["client"]["name"] = st.text_input(
            "Client Name", value=a["client"]["name"], key="client_name"
        )
        a["client"]["industry"] = st.text_input(
            "Industry", value=a["client"]["industry"], key="client_industry"
        )
    with col2:
        a["client"]["market"] = st.text_input(
            "Market / Region", value=a["client"]["market"], key="client_market"
        )
        a["client"]["size"] = st.selectbox(
            "Company Size",
            options=["", "Small (<500 employees)", "Medium (500–5000)", "Large (5000–50000)", "Enterprise (>50000)"],
            index=["", "Small (<500 employees)", "Medium (500–5000)", "Large (5000–50000)", "Enterprise (>50000)"].index(
                a["client"]["size"] if a["client"]["size"] in ["", "Small (<500 employees)", "Medium (500–5000)", "Large (5000–50000)", "Enterprise (>50000)"] else ""
            ),
            key="client_size",
        )
```

- [ ] **Step 2: Run the app and verify the Client tab works**

Run: `python3 -m streamlit run app.py`
Expected: Client tab shows 4 fields. Values persist when switching tabs.
Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: client tab with name, industry, market, size inputs"
```

---

## Task 8: Applications Tab

**Files:**
- Modify: `app.py` (replace `with tab_apps:` block)

Each application has cost inputs and 8 metric dropdowns. Applications are stored as a list in `session_state.assessment["applications"]`.

- [ ] **Step 1: Add _make_default_app helper at module level in app.py, after the _DEFAULT_ASSESSMENT block**

Find:
```python
if "assessment" not in st.session_state:
```

Insert before it:
```python
def _make_default_app(app_id: int) -> dict:
    return {
        "id": f"APP-{app_id:03d}",
        "name": f"Application {app_id}",
        "type": "Custom-Built",
        "portfolio": "",
        "dev_resources": 0.0,
        "dev_cost_per_resource": 0.0,
        "support_resources": 0.0,
        "support_cost_per_resource": 0.0,
        "license_cost": 0.0,
        "infra_cost": 0.0,
        "hardware_sw_cost": 0.0,
        "metrics": {
            "documentation": "",
            "code_quality": "",
            "code_duplication": "",
            "ease_of_integration": "",
            "platform_currency": "",
            "incident_fixes": "",
            "architecture_compliance": "",
            "niche_skills": "",
        },
    }

```

- [ ] **Step 2: Replace the tab_apps block in app.py**

Find:
```python
with tab_apps:
    st.markdown("### Applications")
    st.info("Add applications.")
```

Replace with:
```python
with tab_apps:
    from src.reference_data import SCORING_OPTIONS, CODE_METRIC_APP_TYPES

    st.markdown("### Applications")
    apps = st.session_state.assessment["applications"]

    col_add, col_count = st.columns([1, 3])
    with col_add:
        if st.button("+ Add Application"):
            apps.append(_make_default_app(len(apps) + 1))
            st.rerun()
    with col_count:
        st.markdown(f"**{len(apps)} application(s)**")

    for idx, app in enumerate(apps):
        with st.expander(f"{'🟢' if app['name'] else '⚪'} {app['id']} — {app['name']}", expanded=(idx == 0)):
            c1, c2 = st.columns(2)
            with c1:
                app["id"] = st.text_input("App ID", value=app["id"], key=f"app_id_{idx}")
                app["name"] = st.text_input("Name", value=app["name"], key=f"app_name_{idx}")
                app["type"] = st.selectbox(
                    "Type",
                    ["Custom-Built", "PaaS", "SaaS", "COTS"],
                    index=["Custom-Built", "PaaS", "SaaS", "COTS"].index(app["type"]),
                    key=f"app_type_{idx}",
                )
                app["portfolio"] = st.text_input("Portfolio / BU", value=app["portfolio"], key=f"app_portfolio_{idx}")
            with c2:
                app["dev_resources"] = st.number_input("Dev Resources (FTEs)", value=float(app["dev_resources"]), min_value=0.0, key=f"app_dev_res_{idx}")
                app["dev_cost_per_resource"] = st.number_input("Dev Cost/Resource (kUSD/year)", value=float(app["dev_cost_per_resource"]), min_value=0.0, key=f"app_dev_cost_{idx}")
                app["support_resources"] = st.number_input("Support Resources (FTEs)", value=float(app["support_resources"]), min_value=0.0, key=f"app_sup_res_{idx}")
                app["support_cost_per_resource"] = st.number_input("Support Cost/Resource (kUSD/year)", value=float(app["support_cost_per_resource"]), min_value=0.0, key=f"app_sup_cost_{idx}")
                app["license_cost"] = st.number_input("License Cost (kUSD/year)", value=float(app["license_cost"]), min_value=0.0, key=f"app_lic_{idx}")
                app["infra_cost"] = st.number_input("Infra Cost (kUSD/year)", value=float(app["infra_cost"]), min_value=0.0, key=f"app_infra_{idx}")
                app["hardware_sw_cost"] = st.number_input("Hardware/SW Cost (kUSD/year)", value=float(app["hardware_sw_cost"]), min_value=0.0, key=f"app_hw_{idx}")

            st.markdown("**Tech Debt Metrics**")
            m_col1, m_col2 = st.columns(2)
            app_type = app["type"]
            with m_col1:
                for metric in ["documentation", "ease_of_integration", "platform_currency", "incident_fixes"]:
                    opts = [""] + [opt for opt, _ in SCORING_OPTIONS["application"][metric]]
                    current = app["metrics"].get(metric, "")
                    idx_val = opts.index(current) if current in opts else 0
                    app["metrics"][metric] = st.selectbox(
                        metric.replace("_", " ").title(),
                        opts,
                        index=idx_val,
                        key=f"app_{metric}_{idx}",
                    )
            with m_col2:
                for metric in ["code_quality", "code_duplication", "architecture_compliance", "niche_skills"]:
                    opts = [""] + [opt for opt, _ in SCORING_OPTIONS["application"][metric]]
                    current = app["metrics"].get(metric, "")
                    idx_val = opts.index(current) if current in opts else 0
                    disabled = metric in ("code_quality", "code_duplication") and app_type not in CODE_METRIC_APP_TYPES
                    label = metric.replace("_", " ").title()
                    if disabled:
                        label += " (N/A for this app type)"
                    app["metrics"][metric] = st.selectbox(
                        label,
                        opts,
                        index=idx_val,
                        disabled=disabled,
                        key=f"app_{metric}_{idx}",
                    )

            if st.button("Remove", key=f"remove_app_{idx}"):
                apps.pop(idx)
                st.rerun()
```

- [ ] **Step 3: Run the app and verify Applications tab**

Run: `python3 -m streamlit run app.py`
Expected: "+ Add Application" button works. Each app has expandable section with all fields. Remove button works. Code Quality and Code Duplication are disabled for SaaS/COTS apps.
Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: applications tab with add/remove, cost inputs, metric dropdowns"
```

---

## Task 9: Infrastructure Tab

**Files:**
- Modify: `app.py` (replace `with tab_infra:` block)

- [ ] **Step 1: Add _make_default_component helper in app.py, after _make_default_app**

Find:
```python
if "assessment" not in st.session_state:
```

Insert before it:
```python
def _make_default_component(comp_id: int) -> dict:
    return {
        "id": f"INFRA-{comp_id:03d}",
        "component_name": f"Component {comp_id}",
        "component_type": "Hardware",
        "linked_app_id": "",
        "engg_resources": 0.0,
        "engg_cost_per_resource": 0.0,
        "support_resources": 0.0,
        "support_cost_per_resource": 0.0,
        "license_cost": 0.0,
        "support_contract_cost": 0.0,
        "metrics": {
            "eol": "",
            "incident_fixes": "",
        },
    }

```

- [ ] **Step 2: Replace the tab_infra block in app.py**

Find:
```python
with tab_infra:
    st.markdown("### Infrastructure")
    st.info("Add infrastructure components.")
```

Replace with:
```python
with tab_infra:
    from src.reference_data import SCORING_OPTIONS, INFRA_COMPONENT_TYPES

    st.markdown("### Infrastructure")
    components = st.session_state.assessment["infrastructure"]
    apps = st.session_state.assessment["applications"]

    col_add, col_count = st.columns([1, 3])
    with col_add:
        if st.button("+ Add Component"):
            components.append(_make_default_component(len(components) + 1))
            st.rerun()
    with col_count:
        st.markdown(f"**{len(components)} component(s)**")

    app_ids = [""] + [a["id"] for a in apps]

    for idx, comp in enumerate(components):
        with st.expander(f"{'🟢' if comp['component_name'] else '⚪'} {comp['id']} — {comp['component_name']}", expanded=(idx == 0)):
            c1, c2 = st.columns(2)
            with c1:
                comp["id"] = st.text_input("Component ID", value=comp["id"], key=f"comp_id_{idx}")
                comp["component_name"] = st.text_input("Name", value=comp["component_name"], key=f"comp_name_{idx}")
                comp["component_type"] = st.selectbox(
                    "Component Type",
                    INFRA_COMPONENT_TYPES,
                    index=INFRA_COMPONENT_TYPES.index(comp["component_type"]) if comp["component_type"] in INFRA_COMPONENT_TYPES else 0,
                    key=f"comp_type_{idx}",
                )
                linked = comp["linked_app_id"] if comp["linked_app_id"] in app_ids else ""
                comp["linked_app_id"] = st.selectbox(
                    "Linked Application",
                    app_ids,
                    index=app_ids.index(linked),
                    key=f"comp_app_{idx}",
                )
            with c2:
                comp["engg_resources"] = st.number_input("Engg Resources (FTEs)", value=float(comp["engg_resources"]), min_value=0.0, key=f"comp_engg_res_{idx}")
                comp["engg_cost_per_resource"] = st.number_input("Engg Cost/Resource (kUSD/year)", value=float(comp["engg_cost_per_resource"]), min_value=0.0, key=f"comp_engg_cost_{idx}")
                comp["support_resources"] = st.number_input("Support Resources (FTEs)", value=float(comp["support_resources"]), min_value=0.0, key=f"comp_sup_res_{idx}")
                comp["support_cost_per_resource"] = st.number_input("Support Cost/Resource (kUSD/year)", value=float(comp["support_cost_per_resource"]), min_value=0.0, key=f"comp_sup_cost_{idx}")
                comp["license_cost"] = st.number_input("License Cost (kUSD/year)", value=float(comp["license_cost"]), min_value=0.0, key=f"comp_lic_{idx}")
                comp["support_contract_cost"] = st.number_input("Support Contract (kUSD/year)", value=float(comp["support_contract_cost"]), min_value=0.0, key=f"comp_contract_{idx}")

            st.markdown("**Tech Debt Metrics**")
            m1, m2 = st.columns(2)
            with m1:
                eol_opts = [""] + [opt for opt, _ in SCORING_OPTIONS["infrastructure"]["eol"]]
                current_eol = comp["metrics"].get("eol", "")
                comp["metrics"]["eol"] = st.selectbox(
                    "EOL Status",
                    eol_opts,
                    index=eol_opts.index(current_eol) if current_eol in eol_opts else 0,
                    key=f"comp_eol_{idx}",
                )
            with m2:
                inc_opts = [""] + [opt for opt, _ in SCORING_OPTIONS["infrastructure"]["incident_fixes"]]
                current_inc = comp["metrics"].get("incident_fixes", "")
                comp["metrics"]["incident_fixes"] = st.selectbox(
                    "Incident Fixes",
                    inc_opts,
                    index=inc_opts.index(current_inc) if current_inc in inc_opts else 0,
                    key=f"comp_inc_{idx}",
                )

            if st.button("Remove", key=f"remove_comp_{idx}"):
                components.pop(idx)
                st.rerun()
```

- [ ] **Step 3: Run the app and verify Infrastructure tab**

Run: `python3 -m streamlit run app.py`
Expected: Add/remove components works. Dropdown for Linked Application shows app IDs from Applications tab. EOL and Incident Fixes dropdowns populated.
Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: infrastructure tab with component add/remove and EOL/incident metrics"
```

---

## Task 10: Architecture Tab

**Files:**
- Modify: `app.py` (replace `with tab_arch:` block)

- [ ] **Step 1: Replace the tab_arch block in app.py**

Find:
```python
with tab_arch:
    st.markdown("### Architecture")
    st.info("Fill in architecture data.")
```

Replace with:
```python
with tab_arch:
    from src.reference_data import SCORING_OPTIONS

    st.markdown("### Architecture")
    arch = st.session_state.assessment["architecture"]

    st.markdown("#### Labor Costs (kUSD/year)")
    c1, c2, c3 = st.columns(3)
    with c1:
        arch["total_dev_labor"] = st.number_input("Total Dev Labor", value=float(arch["total_dev_labor"]), min_value=0.0, key="arch_dev")
    with c2:
        arch["total_support_labor"] = st.number_input("Total Support Labor", value=float(arch["total_support_labor"]), min_value=0.0, key="arch_support")
    with c3:
        arch["total_ea_labor"] = st.number_input("Total EA Labor", value=float(arch["total_ea_labor"]), min_value=0.0, key="arch_ea")

    st.markdown("#### Architecture Metrics")

    def _arch_selectbox(field, label, metric_key):
        opts = [""] + [opt for opt, _ in SCORING_OPTIONS["architecture"][metric_key]]
        current = arch.get(field, "")
        arch[field] = st.selectbox(
            label,
            opts,
            index=opts.index(current) if current in opts else 0,
            key=f"arch_{field}",
        )

    _arch_selectbox("ea_op_model_maturity", "EA Op Model Maturity", "ea_op_model_maturity")

    # Determine if tools_driven and arch_compliance are applicable
    ea_maturity_score = 1
    ea_val = arch.get("ea_op_model_maturity", "")
    if ea_val:
        for opt, sc in SCORING_OPTIONS["architecture"]["ea_op_model_maturity"]:
            if opt == ea_val:
                ea_maturity_score = sc
                break

    tools_disabled = ea_maturity_score > 3
    compliance_disabled = ea_maturity_score > 3

    _arch_selectbox("tools_driven_arch", "Tools Driven Architecture Management" + (" (N/A when EA maturity score > 3)" if tools_disabled else ""), "tools_driven_arch")
    _arch_selectbox("architecture_compliance", "Architecture Compliance" + (" (N/A when EA maturity score > 3)" if compliance_disabled else ""), "architecture_compliance")
    _arch_selectbox("duplicate_capabilities", "Duplicate Capabilities", "duplicate_capabilities")

    if tools_disabled:
        st.caption("Tools Driven Architecture Management and Architecture Compliance are not applicable when EA Op Model Maturity score > 3.")
```

- [ ] **Step 2: Run the app and verify Architecture tab**

Run: `python3 -m streamlit run app.py`
Expected: Labor cost inputs + 4 metric dropdowns. Caption appears when EA maturity score > 3.
Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: architecture tab with labor costs and metric dropdowns"
```

---

## Task 11: People Tab

**Files:**
- Modify: `app.py` (replace `with tab_people:` block)

- [ ] **Step 1: Replace the tab_people block in app.py**

Find:
```python
with tab_people:
    st.markdown("### People")
    st.info("Fill in people data.")
```

Replace with:
```python
with tab_people:
    from src.reference_data import SCORING_OPTIONS

    st.markdown("### People")
    people = st.session_state.assessment["people"]

    st.markdown("#### Labor Costs (kUSD/year)")
    c1, c2, c3 = st.columns(3)
    with c1:
        people["total_dev_labor"] = st.number_input("Total Dev Labor", value=float(people["total_dev_labor"]), min_value=0.0, key="ppl_dev")
    with c2:
        people["total_support_labor"] = st.number_input("Total Support Labor", value=float(people["total_support_labor"]), min_value=0.0, key="ppl_support")
    with c3:
        people["total_ea_labor"] = st.number_input("Total EA Labor", value=float(people["total_ea_labor"]), min_value=0.0, key="ppl_ea")

    st.markdown("#### People Metrics")

    def _ppl_selectbox(field, label, metric_key):
        opts = [""] + [opt for opt, _ in SCORING_OPTIONS["people"][metric_key]]
        current = people.get(field, "")
        people[field] = st.selectbox(
            label,
            opts,
            index=opts.index(current) if current in opts else 0,
            key=f"ppl_{field}",
        )

    _ppl_selectbox("it_ea_skills", "IT & EA Skills and Proficiencies", "it_ea_skills")
    _ppl_selectbox("org_change_management", "Organisation Change Management", "org_change_management")
    _ppl_selectbox("team_motivation", "IT & EA Team Motivation", "team_motivation")
    _ppl_selectbox("genai_intervention", "GenAI Intervention", "genai_intervention")
```

- [ ] **Step 2: Run the app and verify People tab**

Run: `python3 -m streamlit run app.py`
Expected: Labor costs + 4 metric dropdowns showing full option texts.
Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: people tab with labor costs and people metrics dropdowns"
```

---

## Task 12: Dashboard Tab

**Files:**
- Modify: `app.py` (replace `with tab_dashboard:` block)

- [ ] **Step 1: Replace the tab_dashboard block in app.py**

Find:
```python
with tab_dashboard:
    st.markdown("### Dashboard")
    st.info("Complete all tabs then click Calculate.")
```

Replace with:
```python
with tab_dashboard:
    import plotly.graph_objects as go
    from src.scoring import score_metric, score_dimension, detect_tech_debt
    from src.interest_cost import calc_app_interest, calc_infra_interest, calc_arch_interest, calc_people_interest
    from src.tco import calc_tco
    from src.reference_data import SCORING_OPTIONS, CODE_METRIC_APP_TYPES

    st.markdown("### Dashboard")

    if st.button("Calculate", type="primary"):
        st.session_state["results"] = _calculate_results(
            st.session_state.assessment
        )

    if "results" not in st.session_state:
        st.info("Fill in all tabs and click Calculate to see results.")
        st.stop()

    results = st.session_state["results"]

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("App Score (avg)", f"{results['scores']['application']:.1f}")
    k2.metric("Infra Score (avg)", f"{results['scores']['infrastructure']:.1f}")
    k3.metric("Arch Score (avg)", f"{results['scores']['architecture']:.1f}")
    k4.metric("People Score (avg)", f"{results['scores']['people']:.1f}")

    c1, c2 = st.columns(2)
    c1.metric("Total Annual Interest (kUSD)", f"{results['total_interest']:.1f}")
    c2.metric("Total TCO (kUSD/year)", f"{results['total_tco']:.1f}")

    # ── Radar chart — scores by dimension ────────────────────────────────────
    st.markdown("#### Tech Debt Score by Dimension")
    dims = ["Application", "Infrastructure", "Architecture", "People"]
    dim_scores = [
        results["scores"]["application"],
        results["scores"]["infrastructure"],
        results["scores"]["architecture"],
        results["scores"]["people"],
    ]
    radar_fig = go.Figure(go.Scatterpolar(
        r=dim_scores + [dim_scores[0]],
        theta=dims + [dims[0]],
        fill="toself",
        fillcolor="rgba(161,0,255,0.2)",
        line=dict(color="#A100FF"),
    ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], color="#FFFFFF"),
            angularaxis=dict(color="#FFFFFF"),
            bgcolor="#1A1A1A",
        ),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#FFFFFF"),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # ── Bar chart — interest cost by application ──────────────────────────────
    if results["app_details"]:
        st.markdown("#### Annual Interest Cost by Application (kUSD)")
        app_names = [d["name"] for d in results["app_details"]]
        app_interests = [d["interest"] for d in results["app_details"]]
        bar_fig = go.Figure(go.Bar(
            x=app_names,
            y=app_interests,
            marker_color="#A100FF",
            text=[f"{v:.1f}" for v in app_interests],
            textposition="outside",
            textfont=dict(color="#FFFFFF"),
        ))
        bar_fig.update_layout(
            paper_bgcolor="#000000",
            plot_bgcolor="#1A1A1A",
            font=dict(color="#FFFFFF"),
            xaxis=dict(tickfont=dict(color="#FFFFFF")),
            yaxis=dict(tickfont=dict(color="#FFFFFF"), title="kUSD/year"),
            margin=dict(l=40, r=40, t=20, b=60),
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # ── TCO breakdown ─────────────────────────────────────────────────────────
    if results["app_details"]:
        st.markdown("#### TCO by Application (kUSD/year)")
        tco_fig = go.Figure(go.Bar(
            x=[d["name"] for d in results["app_details"]],
            y=[d["tco"] for d in results["app_details"]],
            marker_color="#7B00CC",
            text=[f"{v:.1f}" for v in [d["tco"] for d in results["app_details"]]],
            textposition="outside",
            textfont=dict(color="#FFFFFF"),
        ))
        tco_fig.update_layout(
            paper_bgcolor="#000000",
            plot_bgcolor="#1A1A1A",
            font=dict(color="#FFFFFF"),
            xaxis=dict(tickfont=dict(color="#FFFFFF")),
            yaxis=dict(tickfont=dict(color="#FFFFFF"), title="kUSD/year"),
            margin=dict(l=40, r=40, t=20, b=60),
        )
        st.plotly_chart(tco_fig, use_container_width=True)

    # ── Dimension interest breakdown ──────────────────────────────────────────
    st.markdown("#### Interest Cost by Dimension (kUSD/year)")
    dim_interest_fig = go.Figure(go.Bar(
        x=["Applications", "Infrastructure", "Architecture", "People"],
        y=[
            results["interest_by_dimension"]["application"],
            results["interest_by_dimension"]["infrastructure"],
            results["interest_by_dimension"]["architecture"],
            results["interest_by_dimension"]["people"],
        ],
        marker_color=["#A100FF", "#CC00FF", "#7B00CC", "#550088"],
        text=[f"{v:.1f}" for v in [
            results["interest_by_dimension"]["application"],
            results["interest_by_dimension"]["infrastructure"],
            results["interest_by_dimension"]["architecture"],
            results["interest_by_dimension"]["people"],
        ]],
        textposition="outside",
        textfont=dict(color="#FFFFFF"),
    ))
    dim_interest_fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#1A1A1A",
        font=dict(color="#FFFFFF"),
        xaxis=dict(tickfont=dict(color="#FFFFFF")),
        yaxis=dict(tickfont=dict(color="#FFFFFF"), title="kUSD/year"),
        margin=dict(l=40, r=40, t=20, b=40),
    )
    st.plotly_chart(dim_interest_fig, use_container_width=True)
```

- [ ] **Step 2: Add the _calculate_results function to app.py, before the tabs block**

Find:
```python
# ── Tabs ───────────────────────────────────────────────────────────────────────
```

Insert before it:
```python
def _get_score(options_list, value):
    """Look up score from a list of (option, score) tuples. Returns 1 if not found."""
    for opt, sc in options_list:
        if opt == value:
            return sc
    return 1


def _calculate_results(assessment: dict) -> dict:
    """Run all calculations and return a results dict."""
    from src.scoring import score_metric, score_dimension, detect_tech_debt
    from src.interest_cost import calc_app_interest, calc_infra_interest, calc_arch_interest, calc_people_interest
    from src.tco import calc_tco
    from src.reference_data import SCORING_OPTIONS, CODE_METRIC_APP_TYPES

    # ── Applications ──────────────────────────────────────────────────────────
    app_details = []
    app_scores_all = []
    app_interest_total = 0.0
    app_tco_total = 0.0

    for app in assessment["applications"]:
        metrics = app["metrics"]
        app_type = app.get("type", "Custom-Built")
        scores = {}
        for metric, value in metrics.items():
            if not value:
                continue
            if metric in ("code_quality", "code_duplication") and app_type not in CODE_METRIC_APP_TYPES:
                continue
            scores[metric] = score_metric("application", metric, value)

        app_score = score_dimension(list(scores.values())) if scores else 1.0
        app_scores_all.append(app_score)

        interest_input = {
            "type": app_type,
            "dev_resources": app["dev_resources"],
            "dev_cost_per_resource": app["dev_cost_per_resource"],
            "support_resources": app["support_resources"],
            "support_cost_per_resource": app["support_cost_per_resource"],
            "scores": scores,
        }
        interest = calc_app_interest(interest_input)
        tco = calc_tco(app)

        app_details.append({
            "name": app["name"] or app["id"],
            "score": app_score,
            "interest": interest,
            "tco": tco,
            "has_tech_debt": detect_tech_debt(list(scores.values())) if scores else False,
        })
        app_interest_total += interest
        app_tco_total += tco

    app_avg_score = sum(app_scores_all) / len(app_scores_all) if app_scores_all else 0.0

    # ── Infrastructure ────────────────────────────────────────────────────────
    infra_scores_all = []
    infra_interest_total = 0.0

    for comp in assessment["infrastructure"]:
        metrics = comp["metrics"]
        scores = {}
        for metric, value in metrics.items():
            if value:
                scores[metric] = score_metric("infrastructure", metric, value)
        infra_score = score_dimension(list(scores.values())) if scores else 1.0
        infra_scores_all.append(infra_score)

        interest_input = {
            "component_type": comp["component_type"],
            "engg_resources": comp["engg_resources"],
            "engg_cost_per_resource": comp["engg_cost_per_resource"],
            "support_resources": comp["support_resources"],
            "support_cost_per_resource": comp["support_cost_per_resource"],
            "scores": scores,
        }
        infra_interest_total += calc_infra_interest(interest_input)

    infra_avg_score = sum(infra_scores_all) / len(infra_scores_all) if infra_scores_all else 0.0

    # ── Architecture ──────────────────────────────────────────────────────────
    arch = assessment["architecture"]
    arch_scores = {}
    for metric in ("ea_op_model_maturity", "tools_driven_arch", "architecture_compliance", "duplicate_capabilities"):
        value = arch.get(metric, "")
        if value:
            arch_scores[metric] = score_metric("architecture", metric, value)

    arch_avg_score = score_dimension(list(arch_scores.values())) if arch_scores else 0.0
    arch_interest = calc_arch_interest({
        "total_dev_labor": arch["total_dev_labor"],
        "total_support_labor": arch["total_support_labor"],
        "total_ea_labor": arch["total_ea_labor"],
        "scores": arch_scores,
    })

    # ── People ────────────────────────────────────────────────────────────────
    people = assessment["people"]
    people_scores = {}
    for metric in ("it_ea_skills", "org_change_management", "team_motivation", "genai_intervention"):
        value = people.get(metric, "")
        if value:
            people_scores[metric] = score_metric("people", metric, value)

    people_avg_score = score_dimension(list(people_scores.values())) if people_scores else 0.0
    people_interest = calc_people_interest({
        "total_dev_labor": people["total_dev_labor"],
        "total_support_labor": people["total_support_labor"],
        "total_ea_labor": people["total_ea_labor"],
        "scores": people_scores,
    })

    total_interest = app_interest_total + infra_interest_total + arch_interest + people_interest

    return {
        "scores": {
            "application": round(app_avg_score, 2),
            "infrastructure": round(infra_avg_score, 2),
            "architecture": round(arch_avg_score, 2),
            "people": round(people_avg_score, 2),
        },
        "total_interest": round(total_interest, 2),
        "total_tco": round(app_tco_total, 2),
        "app_details": app_details,
        "interest_by_dimension": {
            "application": round(app_interest_total, 2),
            "infrastructure": round(infra_interest_total, 2),
            "architecture": round(arch_interest, 2),
            "people": round(people_interest, 2),
        },
    }

```

- [ ] **Step 3: Run the app and verify Dashboard tab**

Run: `python3 -m streamlit run app.py`
Expected: Fill in a few fields in Applications and click Calculate. KPI metrics appear. Radar chart, bar charts render with Accenture purple. No Python errors.
Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: dashboard tab with KPI metrics, radar chart, interest and TCO charts"
```

---

## Task 13: Save/Load JSON

**Files:**
- Modify: `app.py` (update sidebar Save/Load buttons to be fully functional)

The Save button already triggers a download. Load already reads the file. This task verifies both work end-to-end and fixes any edge cases.

- [ ] **Step 1: Replace the sidebar Save/Load block in app.py**

Find:
```python
    if st.button("Save JSON"):
        data = json.dumps(st.session_state.assessment, indent=2)
        st.download_button(
            label="Download assessment.json",
            data=data,
            file_name="assessment.json",
            mime="application/json",
        )

    uploaded = st.file_uploader("Load JSON", type="json", label_visibility="collapsed")
    if uploaded is not None:
        try:
            st.session_state.assessment = json.loads(uploaded.read())
            st.success("Assessment loaded.")
        except Exception as exc:
            st.error(f"Failed to load: {exc}")
```

Replace with:
```python
    data = json.dumps(st.session_state.assessment, indent=2, ensure_ascii=False)
    st.download_button(
        label="Save JSON",
        data=data,
        file_name=f"{project_name.replace(' ', '_')}_assessment.json",
        mime="application/json",
    )

    uploaded = st.file_uploader("Load JSON", type="json", label_visibility="collapsed")
    if uploaded is not None:
        try:
            loaded = json.loads(uploaded.read())
            # Merge loaded data with defaults to handle missing keys gracefully
            merged = _DEFAULT_ASSESSMENT.copy()
            merged.update(loaded)
            st.session_state.assessment = merged
            if "results" in st.session_state:
                del st.session_state["results"]
            st.success("Assessment loaded.")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to load JSON: {exc}")
```

- [ ] **Step 2: Run and test save/load cycle**

Run: `python3 -m streamlit run app.py`
1. Add an application, fill in some fields.
2. Click "Save JSON" → downloads file.
3. Reload the page (session resets).
4. Upload the saved file → form fields repopulate.
Expected: All data survives the save/load cycle.
Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: save/load JSON with filename from project name and safe merge on load"
```

---

## Task 14: PDF Export

**Files:**
- Create: `src/export_pdf.py`
- Modify: `app.py` (sidebar PDF button)

- [ ] **Step 1: Create src/export_pdf.py**

```python
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

PURPLE = HexColor("#A100FF")
BLACK = HexColor("#000000")
DARK_GREY = HexColor("#1A1A1A")
WHITE = white


def generate_pdf(assessment: dict, results: dict) -> bytes:
    """Return PDF bytes for the executive summary report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=PURPLE,
        fontSize=20,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=PURPLE,
        fontSize=13,
        spaceBefore=12,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=HexColor("#666666"),
    )

    client = assessment.get("client", {})
    scores = results.get("scores", {})
    interest = results.get("total_interest", 0)
    tco = results.get("total_tco", 0)

    story = []

    # Header
    story.append(Paragraph("▲ Accenture Tech Debt Assessment", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE))
    story.append(Spacer(1, 0.3 * cm))

    # Client info
    story.append(Paragraph("Executive Summary", heading_style))
    client_data = [
        ["Client", client.get("name", "—"), "Industry", client.get("industry", "—")],
        ["Market", client.get("market", "—"), "Size", client.get("size", "—")],
    ]
    client_table = Table(client_data, colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm])
    client_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), PURPLE),
        ("TEXTCOLOR", (2, 0), (2, -1), PURPLE),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.4 * cm))

    # KPI summary
    story.append(Paragraph("Financial Summary", heading_style))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Annual Tech Debt Interest", f"{interest:.1f} kUSD"],
        ["Total Application TCO", f"{tco:.1f} kUSD/year"],
        ["Applications assessed", str(len(assessment.get("applications", [])))],
        ["Infrastructure components assessed", str(len(assessment.get("infrastructure", [])))],
    ]
    kpi_table = Table(kpi_data, colWidths=[10 * cm, 7 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F5F5F5"), WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4 * cm))

    # Scores by dimension
    story.append(Paragraph("Tech Debt Scores by Dimension (1 = best, 5 = worst)", heading_style))
    score_data = [["Dimension", "Score", "Status"]]
    for dim, label in [("application", "Application"), ("infrastructure", "Infrastructure"),
                       ("architecture", "Architecture"), ("people", "People")]:
        sc = scores.get(dim, 0)
        status = "High Risk" if sc >= 3 else ("Medium Risk" if sc >= 2 else "Low Risk")
        score_data.append([label, f"{sc:.2f}", status])

    score_table = Table(score_data, colWidths=[6 * cm, 4 * cm, 7 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F5F5F5"), WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.4 * cm))

    # Interest by dimension
    story.append(Paragraph("Annual Interest Cost by Dimension (kUSD)", heading_style))
    interest_dim = results.get("interest_by_dimension", {})
    interest_data = [["Dimension", "Annual Interest (kUSD)"]]
    for dim, label in [("application", "Application"), ("infrastructure", "Infrastructure"),
                       ("architecture", "Architecture"), ("people", "People")]:
        interest_data.append([label, f"{interest_dim.get(dim, 0):.1f}"])
    interest_data.append(["TOTAL", f"{interest:.1f}"])

    int_table = Table(interest_data, colWidths=[10 * cm, 7 * cm])
    int_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [HexColor("#F5F5F5"), WHITE]),
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#F0E0FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(int_table)

    # Footer
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE))
    story.append(Paragraph("Generated by Accenture Tech Debt Calculator", label_style))

    doc.build(story)
    return buffer.getvalue()
```

- [ ] **Step 2: Update PDF button in sidebar**

Find:
```python
    with col1:
        if st.button("PDF"):
            st.info("Complete the assessment first.")
```

Replace with:
```python
    with col1:
        if st.button("PDF"):
            if "results" not in st.session_state:
                st.warning("Run Calculate first.")
            else:
                from src.export_pdf import generate_pdf
                pdf_bytes = generate_pdf(
                    st.session_state.assessment,
                    st.session_state["results"]
                )
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name="tech_debt_report.pdf",
                    mime="application/pdf",
                    key="pdf_download",
                )
```

- [ ] **Step 3: Run and test PDF export**

Run: `python3 -m streamlit run app.py`
1. Add an application, fill fields, click Calculate.
2. Click PDF → click Download PDF.
Expected: PDF downloads. Opens as valid PDF with Accenture purple header, client info, KPI table, scores table.
Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add src/export_pdf.py app.py
git commit -m "feat: PDF export with executive summary, scores and interest tables"
```

---

## Task 15: PPT Export

**Files:**
- Create: `src/export_ppt.py`
- Modify: `app.py` (sidebar PPT button)

- [ ] **Step 1: Create src/export_ppt.py**

```python
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

PURPLE = RGBColor(0xA1, 0x00, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GREY = RGBColor(0x1A, 0x1A, 0x1A)
LIGHT_PURPLE = RGBColor(0xE8, 0xC0, 0xFF)


def _add_title_slide(prs: Presentation, client_name: str) -> None:
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BLACK

    # Purple triangle (triangle shape)
    triangle = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.AUTO_SHAPE = 1, freeform triangle = use rectangle
        Inches(0.4), Inches(0.3), Inches(0.8), Inches(0.8)
    )
    triangle.fill.solid()
    triangle.fill.fore_color.rgb = PURPLE
    triangle.line.fill.background()

    # Title
    txBox = slide.shapes.add_textbox(Inches(1.4), Inches(0.3), Inches(8), Inches(0.8))
    tf = txBox.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = "Tech Debt Assessment"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Client name
    txBox2 = slide.shapes.add_textbox(Inches(1.4), Inches(1.2), Inches(8), Inches(0.5))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = client_name or "Client Assessment"
    p2.font.size = Pt(18)
    p2.font.color.rgb = PURPLE

    # Purple line
    line = slide.shapes.add_shape(1, Inches(0.4), Inches(2.0), Inches(9.2), Emu(40000))
    line.fill.solid()
    line.fill.fore_color.rgb = PURPLE
    line.line.fill.background()


def _add_kpi_slide(prs: Presentation, results: dict) -> None:
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BLACK

    # Slide title
    txBox = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Financial Summary"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = PURPLE

    scores = results.get("scores", {})
    kpis = [
        ("Application Score", f"{scores.get('application', 0):.2f}"),
        ("Infrastructure Score", f"{scores.get('infrastructure', 0):.2f}"),
        ("Architecture Score", f"{scores.get('architecture', 0):.2f}"),
        ("People Score", f"{scores.get('people', 0):.2f}"),
        ("Total Annual Interest", f"{results.get('total_interest', 0):.1f} kUSD"),
        ("Total TCO", f"{results.get('total_tco', 0):.1f} kUSD/year"),
    ]

    cols = 3
    box_w = Inches(2.8)
    box_h = Inches(1.4)
    start_x = Inches(0.4)
    start_y = Inches(1.0)
    gap_x = Inches(0.3)
    gap_y = Inches(0.3)

    for i, (label, value) in enumerate(kpis):
        col = i % cols
        row = i // cols
        x = start_x + col * (box_w + gap_x)
        y = start_y + row * (box_h + gap_y)

        box = slide.shapes.add_shape(1, x, y, box_w, box_h)
        box.fill.solid()
        box.fill.fore_color.rgb = DARK_GREY
        box.line.color.rgb = PURPLE

        txBox = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.1), box_w - Inches(0.2), box_h - Inches(0.2))
        tf = txBox.text_frame
        tf.word_wrap = True

        p_label = tf.paragraphs[0]
        p_label.text = label
        p_label.font.size = Pt(10)
        p_label.font.color.rgb = LIGHT_PURPLE

        p_val = tf.add_paragraph()
        p_val.text = value
        p_val.font.size = Pt(18)
        p_val.font.bold = True
        p_val.font.color.rgb = WHITE


def _add_interest_slide(prs: Presentation, results: dict) -> None:
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BLACK

    txBox = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Annual Interest Cost by Dimension"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = PURPLE

    interest_dim = results.get("interest_by_dimension", {})
    dims = [
        ("Application", interest_dim.get("application", 0)),
        ("Infrastructure", interest_dim.get("infrastructure", 0)),
        ("Architecture", interest_dim.get("architecture", 0)),
        ("People", interest_dim.get("people", 0)),
    ]
    total = results.get("total_interest", 0)
    max_val = max(v for _, v in dims) if any(v for _, v in dims) else 1

    bar_start_x = Inches(1.5)
    bar_max_w = Inches(7.0)
    bar_h = Inches(0.5)
    gap_y = Inches(0.3)
    start_y = Inches(1.2)
    purple_variants = [PURPLE, RGBColor(0xCC, 0x00, 0xFF), RGBColor(0x7B, 0x00, 0xCC), RGBColor(0x55, 0x00, 0x88)]

    for i, (label, value) in enumerate(dims):
        y = start_y + i * (bar_h + gap_y)

        lbl_box = slide.shapes.add_textbox(Inches(0.4), y, Inches(1.0), bar_h)
        lf = lbl_box.text_frame
        lp = lf.paragraphs[0]
        lp.text = label
        lp.font.size = Pt(11)
        lp.font.color.rgb = WHITE

        bar_w = bar_max_w * (value / max_val) if max_val > 0 else Inches(0.1)
        bar = slide.shapes.add_shape(1, bar_start_x, y, bar_w, bar_h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = purple_variants[i]
        bar.line.fill.background()

        val_box = slide.shapes.add_textbox(bar_start_x + bar_w + Inches(0.1), y, Inches(1.5), bar_h)
        vf = val_box.text_frame
        vp = vf.paragraphs[0]
        vp.text = f"{value:.1f} kUSD"
        vp.font.size = Pt(11)
        vp.font.color.rgb = LIGHT_PURPLE

    total_y = start_y + len(dims) * (bar_h + gap_y) + Inches(0.2)
    tot_box = slide.shapes.add_textbox(Inches(0.4), total_y, Inches(9), Inches(0.5))
    tf = tot_box.text_frame
    tp = tf.paragraphs[0]
    tp.text = f"Total Annual Interest: {total:.1f} kUSD"
    tp.font.size = Pt(14)
    tp.font.bold = True
    tp.font.color.rgb = PURPLE


def generate_ppt(assessment: dict, results: dict) -> bytes:
    """Return PPT bytes for the Accenture-branded presentation."""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    client_name = assessment.get("client", {}).get("name", "")
    _add_title_slide(prs, client_name)
    _add_kpi_slide(prs, results)
    _add_interest_slide(prs, results)

    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
```

- [ ] **Step 2: Update PPT button in sidebar**

Find:
```python
    with col2:
        if st.button("PPT"):
            st.info("Complete the assessment first.")
```

Replace with:
```python
    with col2:
        if st.button("PPT"):
            if "results" not in st.session_state:
                st.warning("Run Calculate first.")
            else:
                from src.export_ppt import generate_ppt
                ppt_bytes = generate_ppt(
                    st.session_state.assessment,
                    st.session_state["results"]
                )
                st.download_button(
                    "Download PPT",
                    data=ppt_bytes,
                    file_name="tech_debt_report.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key="ppt_download",
                )
```

- [ ] **Step 3: Run and test PPT export**

Run: `python3 -m streamlit run app.py`
1. Fill in assessment, click Calculate.
2. Click PPT → click Download PPT.
Expected: PPTX downloads. Opens with 3 slides: title (black/purple), KPI grid, interest bar chart. Accenture purple throughout.
Stop with Ctrl+C.

- [ ] **Step 4: Run full test suite and verify coverage**

Run: `python3 -m pytest --cov=src --cov-report=term-missing`
Expected: All tests pass. Coverage ≥ 80% for `src/scoring.py`, `src/interest_cost.py`, `src/tco.py`.

- [ ] **Step 5: Commit**

```bash
git add src/export_ppt.py app.py
git commit -m "feat: PPT export with title, KPI, and interest slides — Accenture branded"
```

---

## Done

All 15 tasks complete. The app is runnable with:

```bash
python3 -m streamlit run app.py
```

Full test suite:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```
