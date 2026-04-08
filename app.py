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


if "assessment" not in st.session_state:
    st.session_state.assessment = _DEFAULT_ASSESSMENT.copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Project")
    project_name = st.text_input("Project Name", value="New Assessment")

    st.markdown("---")
    st.markdown("### Save / Load")

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
            merged = _DEFAULT_ASSESSMENT.copy()
            merged.update(loaded)
            st.session_state.assessment = merged
            if "results" in st.session_state:
                del st.session_state["results"]
            st.success("Assessment loaded.")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to load JSON: {exc}")

    st.markdown("---")
    st.markdown("### Export")
    col1, col2 = st.columns(2)
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

# ── _calculate_results helper ─────────────────────────────────────────────────
def _calculate_results(assessment: dict) -> dict:
    """Run all calculations and return a results dict."""
    from src.scoring import score_metric, score_dimension, detect_tech_debt
    from src.interest_cost import calc_app_interest, calc_infra_interest, calc_arch_interest, calc_people_interest
    from src.tco import calc_tco
    from src.reference_data import CODE_METRIC_APP_TYPES

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
