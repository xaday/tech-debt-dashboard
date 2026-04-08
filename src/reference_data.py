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
# Percentages applied to annual dev/support labor costs (€)
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
