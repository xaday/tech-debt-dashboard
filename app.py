import copy
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
    st.session_state.assessment = copy.deepcopy(_DEFAULT_ASSESSMENT)

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
            merged = copy.deepcopy(_DEFAULT_ASSESSMENT)
            for key in merged:
                if key in loaded:
                    if isinstance(merged[key], dict) and isinstance(loaded[key], dict):
                        merged[key].update(loaded[key])
                    else:
                        merged[key] = loaded[key]
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
        _size_options = ["", "Small (<500 employees)", "Medium (500–5000)", "Large (5000–50000)", "Enterprise (>50000)"]
        _current_size = a["client"]["size"] if a["client"]["size"] in _size_options else ""
        a["client"]["size"] = st.selectbox(
            "Company Size",
            options=_size_options,
            index=_size_options.index(_current_size),
            key="client_size",
        )

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
                    index=["Custom-Built", "PaaS", "SaaS", "COTS"].index(app["type"]) if app["type"] in ["Custom-Built", "PaaS", "SaaS", "COTS"] else 0,
                    key=f"app_type_{idx}",
                )
                app["portfolio"] = st.text_input("Portfolio / BU", value=app["portfolio"], key=f"app_portfolio_{idx}")
            with c2:
                app["dev_resources"] = st.number_input("Dev Resources (FTEs)", value=float(app["dev_resources"]), min_value=0.0, key=f"app_dev_res_{idx}")
                app["dev_cost_per_resource"] = st.number_input("Dev Cost/Resource (k€/year)", value=float(app["dev_cost_per_resource"]), min_value=0.0, key=f"app_dev_cost_{idx}")
                app["support_resources"] = st.number_input("Support Resources (FTEs)", value=float(app["support_resources"]), min_value=0.0, key=f"app_sup_res_{idx}")
                app["support_cost_per_resource"] = st.number_input("Support Cost/Resource (k€/year)", value=float(app["support_cost_per_resource"]), min_value=0.0, key=f"app_sup_cost_{idx}")
                app["license_cost"] = st.number_input("License Cost (k€/year)", value=float(app["license_cost"]), min_value=0.0, key=f"app_lic_{idx}")
                app["infra_cost"] = st.number_input("Infra Cost (k€/year)", value=float(app["infra_cost"]), min_value=0.0, key=f"app_infra_{idx}")
                app["hardware_sw_cost"] = st.number_input("Hardware/SW Cost (k€/year)", value=float(app["hardware_sw_cost"]), min_value=0.0, key=f"app_hw_{idx}")

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
                comp["engg_cost_per_resource"] = st.number_input("Engg Cost/Resource (k€/year)", value=float(comp["engg_cost_per_resource"]), min_value=0.0, key=f"comp_engg_cost_{idx}")
                comp["support_resources"] = st.number_input("Support Resources (FTEs)", value=float(comp["support_resources"]), min_value=0.0, key=f"app_sup_res_c_{idx}")
                comp["support_cost_per_resource"] = st.number_input("Support Cost/Resource (k€/year)", value=float(comp["support_cost_per_resource"]), min_value=0.0, key=f"app_sup_cost_c_{idx}")
                comp["license_cost"] = st.number_input("License Cost (k€/year)", value=float(comp["license_cost"]), min_value=0.0, key=f"comp_lic_{idx}")
                comp["support_contract_cost"] = st.number_input("Support Contract (k€/year)", value=float(comp["support_contract_cost"]), min_value=0.0, key=f"comp_contract_{idx}")

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

with tab_arch:
    from src.reference_data import SCORING_OPTIONS

    st.markdown("### Architecture")
    arch = st.session_state.assessment["architecture"]

    st.markdown("#### Labor Costs (k€/year)")
    c1, c2, c3 = st.columns(3)
    with c1:
        arch["total_dev_labor"] = st.number_input("Total Dev Labor", value=float(arch["total_dev_labor"]), min_value=0.0, key="arch_dev")
    with c2:
        arch["total_support_labor"] = st.number_input("Total Support Labor", value=float(arch["total_support_labor"]), min_value=0.0, key="arch_support")
    with c3:
        arch["total_ea_labor"] = st.number_input("Total EA Labor", value=float(arch["total_ea_labor"]), min_value=0.0, key="arch_ea")

    st.markdown("#### Architecture Metrics")

    def _arch_selectbox(field, label, metric_key, disabled=False):
        opts = [""] + [opt for opt, _ in SCORING_OPTIONS["architecture"][metric_key]]
        current = arch.get(field, "")
        arch[field] = st.selectbox(
            label,
            opts,
            index=opts.index(current) if current in opts else 0,
            disabled=disabled,
            key=f"arch_{field}",
        )

    _arch_selectbox("ea_op_model_maturity", "EA Op Model Maturity", "ea_op_model_maturity")

    ea_maturity_score = 1
    ea_val = arch.get("ea_op_model_maturity", "")
    if ea_val:
        for opt, sc in SCORING_OPTIONS["architecture"]["ea_op_model_maturity"]:
            if opt == ea_val:
                ea_maturity_score = sc
                break

    tools_disabled = ea_maturity_score > 3
    _arch_selectbox("tools_driven_arch", "Tools Driven Architecture Management" + (" (N/A when EA maturity score > 3)" if tools_disabled else ""), "tools_driven_arch", disabled=tools_disabled)
    _arch_selectbox("architecture_compliance", "Architecture Compliance" + (" (N/A when EA maturity score > 3)" if tools_disabled else ""), "architecture_compliance", disabled=tools_disabled)
    _arch_selectbox("duplicate_capabilities", "Duplicate Capabilities", "duplicate_capabilities")

    if tools_disabled:
        st.caption("Tools Driven Architecture Management and Architecture Compliance are not applicable when EA Op Model Maturity score > 3.")

with tab_people:
    from src.reference_data import SCORING_OPTIONS

    st.markdown("### People")
    people = st.session_state.assessment["people"]

    st.markdown("#### Labor Costs (k€/year)")
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

with tab_dashboard:
    import plotly.graph_objects as go

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
    c1.metric("Total Annual Interest (k€)", f"{results['total_interest']:.1f}")
    c2.metric("Total TCO (k€/year)", f"{results['total_tco']:.1f}")

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
        st.markdown("#### Annual Interest Cost by Application (k€)")
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
            yaxis=dict(tickfont=dict(color="#FFFFFF"), title="k€/year"),
            margin=dict(l=40, r=40, t=20, b=60),
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # ── TCO breakdown ─────────────────────────────────────────────────────────
    if results["app_details"]:
        st.markdown("#### TCO by Application (k€/year)")
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
            yaxis=dict(tickfont=dict(color="#FFFFFF"), title="k€/year"),
            margin=dict(l=40, r=40, t=20, b=60),
        )
        st.plotly_chart(tco_fig, use_container_width=True)

    # ── Dimension interest breakdown ──────────────────────────────────────────
    st.markdown("#### Interest Cost by Dimension (k€/year)")
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
        yaxis=dict(tickfont=dict(color="#FFFFFF"), title="k€/year"),
        margin=dict(l=40, r=40, t=20, b=40),
    )
    st.plotly_chart(dim_interest_fig, use_container_width=True)
