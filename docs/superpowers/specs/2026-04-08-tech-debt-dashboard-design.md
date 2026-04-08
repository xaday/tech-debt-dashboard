# Tech Debt Calculator Dashboard — Design Spec

## Overview

Streamlit web application that replaces the Accenture Tech Debt Calculator Excel file. Users fill in assessment data directly on the website across 4 dimensions (Application, Infrastructure, Architecture, People), the app calculates Tech Debt Scores and Annual Interest Costs using the original Excel formulas, and produces an interactive dashboard plus exportable PDF/PPT reports.

---

## Goals

- Replace Excel input workflow with a web form
- Replicate Excel scoring formulas exactly (no approximation)
- Support multiple applications per assessment
- Save/load assessment state as JSON (no server, no login)
- Export: PDF executive summary + PPT Accenture-branded slides
- Accenture brand: black (#000000) background, purple (#A100FF) accent, white (#FFFFFF) text

---

## Users

- Accenture consultants during client engagements
- Clients using self-service
- Both may fill in data together in real time

---

## Score Calculation Logic (faithful to Excel)

### Metric Scores (1–5)

Each dimension has multiple metrics. Each metric receives a score 1–5 via lookup against reference tables from the Excel file (`0.A Ref. and Master Values`). Inputs are dropdowns replicating exact Excel options.

| Dimension | Metrics |
|-----------|---------|
| Application | Documentation, Code Quality, Code Duplication, Ease of Integration, Platform Currency, Incident Fixes, Architecture Compliance, Niche Skills |
| Infrastructure | EOL (Hardware/OS/DB/Middleware/Storage by component type), Incident Fixes |
| Architecture | EA Op Model Maturity, Tools-Driven Arch Management, Architecture Compliance, Duplicate Capabilities |
| People | IT & EA Skills Proficiencies, Organisation Change Management, IT & EA Team Motivation, GenAI Intervention |

### Dimension Score

```
Dimension Score = AVERAGE(all applicable metric scores)
```

Tech Debt detected when: `(average ≥ 1) OR (max ≥ 2)` — thresholds configurable via `0.B Score to Interest Mapping`.

### Annual Interest Cost

Two parallel methods (user selects in report):

- **Absolute Method** — actual labor costs × percentage impact per metric
- **Weighted Method** — percentage of total labor budget based on maturity tables

```
Metric Interest Cost = (Dev Labor %) × Annual Dev Cost
                     + (Support Labor %) × Annual Support Cost
                     + Workaround Costs (if applicable)

Dimension Interest Cost = SUM(all metric interest costs)
```

### Total Cost of Ownership (per application)

```
TCO = Annual Dev Cost + Annual Support Cost + Licences + Infra + Hardware/SW
```

Reference tables are loaded once from the Excel file at app startup and stored as Python dicts.

---

## Application Structure

### Navigation

```
Sidebar                          Main Content
──────────────────────────────────────────────────────
[Project Name input]             Tab 1: Client
[Load JSON]                        → Name, Industry, Market, Size
[Save JSON]
[Export PDF]                     Tab 2: Applications
[Export PPT]                       → Add/remove apps (st.expander per app)
                                   → Per app: quality metrics (dropdowns),
                                              cost inputs (kUSD)

                                 Tab 3: Infrastructure
                                   → Components linked to apps
                                   → Type, EOL, costs

                                 Tab 4: Architecture
                                   → EA labor totals, maturity levels

                                 Tab 5: People
                                   → Skills, Change Mgmt, Motivation, GenAI

                                 Tab 6: Dashboard  ← generated after "Calcular"
                                   → Scores by dimension (radar/bar)
                                   → Interest Cost by app
                                   → Risk heatmap
                                   → TCO breakdown
```

### Session State

All form data lives in `st.session_state` as a single dict matching the JSON schema. Save = `json.dumps(state)`. Load = `json.loads(uploaded_file)`.

### JSON Schema

```json
{
  "client": {
    "name": "",
    "industry": "",
    "market": "",
    "size": ""
  },
  "applications": [
    {
      "id": "",
      "name": "",
      "type": "",
      "portfolio": "",
      "dev_resources": 0,
      "dev_cost_per_hour": 0,
      "support_resources": 0,
      "support_cost_per_hour": 0,
      "license_cost": 0,
      "infra_cost": 0,
      "hardware_sw_cost": 0,
      "metrics": {
        "documentation": "",
        "code_quality": "",
        "code_duplication": "",
        "ease_of_integration": "",
        "platform_currency": "",
        "incident_fixes": "",
        "architecture_compliance": "",
        "niche_skills": ""
      }
    }
  ],
  "infrastructure": [
    {
      "id": "",
      "component_name": "",
      "component_type": "",
      "linked_app_id": "",
      "engg_resources": 0,
      "engg_cost_per_hour": 0,
      "support_resources": 0,
      "support_cost_per_hour": 0,
      "license_cost": 0,
      "support_contract_cost": 0,
      "arch_effort_cost": 0,
      "training_cost": 0,
      "eol_months": 0,
      "incident_fixes_pct": 0
    }
  ],
  "architecture": {
    "total_dev_labor": 0,
    "total_support_labor": 0,
    "total_ea_labor": 0,
    "ea_op_model_maturity": "",
    "tools_driven_arch": "",
    "duplicate_capabilities": ""
  },
  "people": {
    "training_effort_pct": 0,
    "dev_labor_cost": 0,
    "support_labor_cost": 0,
    "ea_labor_cost": 0,
    "training_budget": 0,
    "business_value_potential": 0,
    "it_ea_skills": "",
    "change_management": "",
    "team_motivation": "",
    "genai_intervention": ""
  }
}
```

---

## Source Modules (`src/`)

| Module | Responsibility |
|--------|----------------|
| `reference_loader.py` | Reads `0.A Ref. and Master Values` and `0.B Score to Interest Mapping` from Excel → Python dicts. Called once at startup. |
| `scoring.py` | `score_metric(dimension, metric, value, ref_data) → int`. `score_dimension(metrics_dict) → float`. Pure functions, no I/O. |
| `interest_cost.py` | `calc_interest_absolute(app, scores, ref_data) → float`. `calc_interest_weighted(app, scores, ref_data) → float`. |
| `tco.py` | `calc_tco(app) → float`. |
| `export_pdf.py` | `generate_pdf(assessment, results) → bytes`. Executive summary + charts via reportlab. |
| `export_ppt.py` | `generate_ppt(assessment, results) → bytes`. Accenture-branded slides via python-pptx. |
| `app.py` | Streamlit entry point. Forms, session_state, dashboard, sidebar. |

---

## Styling

- Config: `.streamlit/config.toml` with Accenture theme (identical to FinOps dashboard)
- Custom CSS in `app.py` for white text in charts, Accenture header with triangle SVG
- PDF/PPT use Accenture purple (#A100FF) as accent colour

---

## Tests

| File | Coverage |
|------|----------|
| `tests/test_reference_loader.py` | Reference tables load correctly, all expected keys present |
| `tests/test_scoring.py` | Score 1-5 for known inputs across all dimensions and metrics |
| `tests/test_interest_cost.py` | Absolute and weighted cost calculations match expected values |
| `tests/test_tco.py` | TCO sums correctly from individual cost fields |

Minimum coverage: 80%.

---

## Dependencies

```
streamlit
pandas
plotly
openpyxl
reportlab
python-pptx
pytest
pytest-cov
```

---

## Out of Scope

- Azure API integration
- User authentication / multi-user sessions
- Server-side persistence
- Real-time collaboration
