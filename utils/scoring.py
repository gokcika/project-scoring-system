def calculate_regulatory_score(reg_required, reg_deadline, reg_enforcement):
    """Calculate Section 1 score"""
    if reg_required != "YES":
        return 1.0
    
    score = 0
    
    # Deadline scoring
    deadline_scores = {
        "<3 months": 5,
        "3-6 months": 4,
        "6-12 months": 3,
        ">12 months": 2,
        "No specific deadline": 2
    }
    score = deadline_scores.get(reg_deadline, 1)
    
    # Enforcement adjustment
    if reg_enforcement == "NO":
        score = max(1, score - 1)
    
    return float(score)


def calculate_reputational_score(risk_level, harm_categories, liability):
    """Calculate Section 2 score - UPDATED FOR NEW LIABILITY OPTIONS"""
    risk_mapping = {
        "1 - Minimal risk": 1,
        "2 - Low risk, proactive measure": 2,
        "3 - Moderate risk, potential exposure": 3,
        "4 - High risk, known vulnerability": 4,
        "5 - Critical risk, active issue": 5
    }
    
    score = risk_mapping.get(risk_level, 1)
    
    # Harm adjustment - UPDATED
    if harm_categories:
        harm_list = harm_categories.split(',')
        # Changed "Company reputation only" to "Company reputation"
        if len(harm_list) >= 3 and "Company reputation" not in harm_categories:
            score = min(5, score + 1)
        elif "Company reputation" in harm_categories and len(harm_list) == 1:
            score = max(1, score - 1)
    
    # Liability adjustment
    if liability == ">€1M":
        score = 5
    elif liability == "€100K-€1M":
        score = min(5, score + 1)
    
    return float(score)


def calculate_strategic_score(strat_document, strat_sponsor, strat_budget):
    """Calculate Section 3 score"""
    doc_scores = {
        "CEO/Board strategic plan": 5,
        "Division/BU annual strategy": 4,
        "Departmental objectives": 3,
        "Operational improvement": 2,
        "Not in strategic docs": 1
    }
    
    score = doc_scores.get(strat_document, 1)
    
    # Sponsor adjustment
    if strat_sponsor == "NO":
        score = max(1, score - 1)
    
    # Budget adjustment
    if strat_budget == "NO":
        score = max(1, score - 1)
    
    return float(score)


def calculate_operational_score(efficiency_gain, scope, blocker):
    """Calculate Section 4 score"""
    if efficiency_gain >= 30:
        score = 5
    elif efficiency_gain >= 20:
        score = 4
    elif efficiency_gain >= 10:
        score = 3
    elif efficiency_gain >= 5:
        score = 2
    else:
        score = 1
    
    # Scope adjustment
    if scope == "3+ business units":
        score = min(5, score + 1)
    
    # Blocker adjustment
    if blocker == "YES":
        score = min(5, score + 1)
    
    return float(score)


def calculate_resource_score(approach, total_hours, external_deps):
    """Calculate Section 5 score (inverted - lower hours = higher score)"""
    approach_scores = {
        "Existing tool/platform, configuration only": 5,
        "Extend existing platform": 4,
        "New tool, standard implementation": 3,
        "Custom development": 2,
        "Major system overhaul": 1
    }
    
    score = approach_scores.get(approach, 3)
    
    # Hours adjustment
    if total_hours < 40:
        pass  # Keep score
    elif total_hours < 160:
        score = max(1, score - 1)
    elif total_hours < 400:
        score = max(1, score - 2)
    elif total_hours < 1000:
        score = max(1, score - 3)
    else:
        score = max(1, score - 4)
    
    # External dependencies
    if "Vendor/third-party" in external_deps or "Multiple system integration" in external_deps:
        score = max(1, score - 1)
    
    return float(score)


def calculate_data_score(data_type, third_party, volume):
    """Calculate Section 6 score"""
    type_scores = {
        "GDPR Special Categories": 5,
        "Financial data": 5,
        "Trade secrets/IP": 5,
        "PII with breach notification": 4,
        "Regular PII": 3,
        "Internal confidential": 2,
        "Public/low sensitivity": 1
    }
    
    # Get highest if multiple selected
    if "," in data_type:
        types = data_type.split(',')
        score = max([type_scores.get(t.strip(), 1) for t in types])
    else:
        score = type_scores.get(data_type, 1)
    
    # Third party adjustment
    if third_party == "YES":
        score = max(4, score)
    
    # Volume adjustment
    if volume == ">10,000 data subjects":
        score = min(5, score + 1)
    
    return float(score)


def calculate_stakeholder_score(requestor_level, urgency_clear, requestor_history="Unknown"):
    """Calculate Section 7 score"""
    level_scores = {
        "External audit finding": 5,
        "Regulatory inquiry": 5,
        "Board/C-suite": 4,
        "Multiple BU heads": 3,
        "Single BU leadership": 2,
        "Team/individual": 1
    }
    
    score = level_scores.get(requestor_level, 1)
    
    # Urgency adjustment
    if urgency_clear == "NO":
        score = max(1, score - 1)
    
    return float(score)


def calculate_total_score(scores):
    """Calculate weighted total score"""
    weights = {
        'reg': 0.25,
        'rep': 0.20,
        'strat': 0.15,
        'op': 0.15,
        'res': 0.10,
        'data': 0.10,
        'stake': 0.05
    }
    
    total = (
        scores['reg'] * weights['reg'] +
        scores['rep'] * weights['rep'] +
        scores['strat'] * weights['strat'] +
        scores['op'] * weights['op'] +
        scores['res'] * weights['res'] +
        scores['data'] * weights['data'] +
        scores['stake'] * weights['stake']
    ) * 20  # Scale to 100
    
    return round(total, 2)


def get_priority(total_score):
    """Determine priority level"""
    if total_score >= 70:
        return "🔴 IMMEDIATE"
    elif total_score >= 50:
        return "🟡 PLANNED"
    else:
        return "⚪ DEFER"


def check_red_flags(project_data):
    """Check for automatic rejection criteria"""
    red_flags = []
    
    # Check each red flag condition
    if not project_data.get('op_process_name') or len(project_data.get('op_process_name', '')) < 10:
        red_flags.append("Cannot articulate specific problem")
    
    if not project_data.get('op_current_time') or project_data.get('op_current_time', 0) == 0:
        red_flags.append("No current state metrics")
    
    if project_data.get('reg_required') == "YES" and not project_data.get('reg_citation'):
        red_flags.append("Regulatory claim without citation")
    
    return red_flags
