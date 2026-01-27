def calculate_resource_score(approach, total_hours, external_deps):
    """Calculate Section 5 score - HOURS NO LONGER USED"""
    approach_scores = {
        "Use existing tool/platform with configuration only": 5,
        "Extend or integrate with existing platform": 4,
        "Deploy new tool with standard implementation": 3,
        "Custom development required": 2,
        "Major system overhaul or multiple system integration": 1
    }
    
    score = approach_scores.get(approach, 3)
    
    # REMOVED: Hours adjustment (no longer collected)
    
    # External dependencies adjustment
    if "Third-party vendor" in external_deps or "Multiple system" in external_deps:
        score = max(1, score - 1)
    
    return float(score)


def calculate_operational_score(efficiency_gain, scope, blocker):
    """Calculate Section 4 score - UPDATED FOR 2+ BUSINESS UNITS"""
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
    
    # Scope adjustment - UPDATED
    if "2+ business units" in scope:  # Changed from "3+"
        score = min(5, score + 1)
    
    # Blocker adjustment
    if blocker == "YES":
        score = min(5, score + 1)
    
    return float(score)


def calculate_data_score(data_type, third_party, volume):
    """Calculate Section 6 score - VOLUME NO LONGER USED"""
    type_scores = {
        "Public or low-sensitivity data": 1,
        "Internal confidential business data": 2,
        "Regular PII (name, email, contact info)": 3,
        "Sensitive PII (government IDs, credentials)": 4,
        "Financial transaction data": 5,
        "Trade secrets or intellectual property": 5,
        "GDPR Special Categories (health, biometric, etc.)": 5
    }
    
    score = type_scores.get(data_type, 1)
    
    # Third party adjustment
    if third_party == "YES":
        score = max(4, score)
    
    # REMOVED: Volume adjustment (no longer collected)
    
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
    
    # Harm adjustment
    if harm_categories:
        harm_list = harm_categories.split(',')
        if len(harm_list) >= 3 and "Company reputation only" not in harm_categories:
            score = min(5, score + 1)
        elif "Company reputation only" in harm_categories and len(harm_list) == 1:
            score = max(1, score - 1)
    
    # Liability adjustment - UPDATED
    if liability == ">€1M":
        score = 5
    elif liability == "€100K-€1M":
        score = min(5, score + 1)
    # "No apparent monetary exposure" and "<€100K" = no adjustment
    
    return float(score)
