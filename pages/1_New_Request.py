import streamlit as st
from datetime import datetime
import pandas as pd
from utils.database import Database
from utils.scoring import *

st.set_page_config(page_title="New Request", page_icon="📝", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("📝 Submit New Project Request")

st.info("""
**Welcome!** Please complete all sections below to submit your project for review. 
Your submission will be evaluated by the Compliance team and you will be notified of the decision.
""")

with st.form("project_request"):
    st.markdown("### Basic Information")
    
    col1, col2 = st.columns(2)
    with col1:
        project_title = st.text_input("Project Title *", 
            help="Brief descriptive title for your project")
        requestor_name = st.text_input("Your Name *", 
            value=st.session_state.user['username'])
    with col2:
        requestor_email = st.text_input("Your Email *", 
            value=st.session_state.user.get('email', ''))
        department = st.selectbox("Department *", 
            ["IT", "Finance", "HR", "Operations", "Sales", "Legal", "Compliance", "Other"])
    
    st.markdown("---")
    st.markdown("### 1. Regulatory & Compliance Requirements")
    
    reg_required = st.radio(
        "Is this project driven by a specific regulatory or compliance requirement?", 
        ["YES", "NO"]
    )
    
    if reg_required == "YES":
        reg_citation = st.text_area(
            "Cite the specific regulation, directive, or compliance standard", 
            help="Include regulation name, article/section, and link to official text if available",
            placeholder="Example: 1_D_6 Global Compliance 2.3.1.1"
        )
        reg_deadline = st.selectbox(
            ""What is the required compliance due date to meet regulatory or legal obligations?", 
            ["<3 months", "3-6 months", "6-12 months", ">12 months", "No specific deadline"])
            help="Select the timeframe by which compliance must be achieved"
        reg_enforcement = st.radio(
            "Has the regulatory authority issued fines or sanctions in your sector for non-compliance with this requirement?", 
            ["YES", "NO"]
        )
    else:
        reg_citation = ""
        reg_deadline = "No specific deadline"
        reg_enforcement = "NO"
    
    st.markdown("---")
    st.markdown("### 2. Risk Assessment")
    
    st.info("""
    **Guidance:** Consider reputational, operational, legal, and ethical risks if this project 
    is not completed or if current gaps are exposed.
    """)
    
    rep_headline = st.text_input(
        "Describe the primary risk or impact if this issue remains unaddressed",
        help="Focus on concrete business impacts",
        placeholder="Example: Customer data breach exposing PII of 10,000+ users"
    )
    
    rep_risk_level = st.select_slider(
        "Current risk level",
        options=[
            "1 - Minimal risk",
            "2 - Low risk, proactive measure",
            "3 - Moderate risk, potential exposure",
            "4 - High risk, known vulnerability",
            "5 - Critical risk, active issue"
        ],
        help="""
        **How to assess:**
        - **Level 1:** No current exposure, future-proofing
        - **Level 2:** Best practice, competitive positioning
        - **Level 3:** Could cause issues if not addressed
        - **Level 4:** Known issues, documented complaints
        - **Level 5:** Active incidents, media attention, or ongoing harm
        """
    )
    
    rep_harm_categories = st.multiselect(
        "Who could be negatively affected?",
        ["Customers/clients", "Employees", "Shareholders", "Community/environment", "Company reputation"],
        help="Select all that apply"
    )
    
    rep_liability = st.selectbox(
        "Potential liability or financial exposure",
        ["No apparent monetary exposure", "<€100K", "€100K-€1M", ">€1M"],
        help="Include potential fines, penalties, legal costs, and business disruption"
    )
    
    st.markdown("---")
    st.markdown("### 3. Strategic Alignment")
    
    strat_document = st.selectbox(
        "Where is this initiative documented in company planning?",
        ["CEO/Board strategic plan", "Division/BU annual strategy", "Departmental objectives",
         "Operational improvement", "Not in strategic documentation"],
        help="Select the highest-level document where this appears"
    )
    
    strat_sponsor = st.radio(
        "Do you have executive sponsor confirmation in writing?", 
        ["YES", "NO"],
        help="Email or memo from VP-level or above"
    )
    
    strat_budget = st.radio(
        "Has budget been pre-allocated for this initiative?", 
        ["YES", "NO"],
        help="Approved budget code or funding commitment"
    )
    
    st.markdown("---")
    st.markdown("### 4. Operational Impact")
    
    op_process_name = st.text_input(
        "What specific process or operation will be improved?",
        placeholder="Example: Customer onboarding verification process"
    )
    
    st.info("""
    **Guidance for time estimates:**
    - Measure a complete cycle from start to finish
    - Include all hands-on time, waiting time, and rework
    - Use averages if the process varies
    - Be realistic about current state
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        op_current_time = st.number_input(
            "Current: Time per iteration (hours)", 
            min_value=0.0, 
            step=0.5,
            help="How long does one complete cycle take today?"
        )
    with col2:
        op_projected_time = st.number_input(
            "Projected: Time per iteration (hours)", 
            min_value=0.0, 
            step=0.5,
            help="How long will it take after this project?"
        )
    with col3:
        if op_current_time > 0:
            op_efficiency_gain = ((op_current_time - op_projected_time) / op_current_time) * 100
            st.metric("Efficiency Gain", f"{op_efficiency_gain:.1f}%")
        else:
            op_efficiency_gain = 0
            st.metric("Efficiency Gain", "N/A")
    
    op_scope = st.radio(
        "How many groups will be affected?",
        ["Single team", "Single business unit", "2+ business units", "2+ business units plus external stakeholders"],
        help="Consider both internal teams and external stakeholders (customers, vendors, partners)"
    )
    
    op_blocker = st.radio(
        "Is the current process blocking other planned initiatives?",
        ["YES", "NO"],
        help="Are other projects waiting for this to be resolved?"
    )
    
    st.markdown("---")
    st.markdown("### 5. Implementation Approach")
    
    res_approach = st.selectbox(
        "What implementation approach is anticipated?",
        ["Use existing tool/platform with configuration only",
         "Extend or integrate with existing platform",
         "Deploy new tool with standard implementation",
         "Custom development required",
         "Major system overhaul or multiple system integration"],
        help="Select the option that best describes the technical complexity"
    )
    
    st.markdown("---")
    st.markdown("### 6. Data & Privacy Considerations")
    
    st.info("""
    **Data Type Definitions:**
    - **Public/Low Sensitivity:** Already publicly available or non-confidential
    - **Internal Confidential:** Business-sensitive but not personal data
    - **Regular PII:** Name, email, phone, address
    - **Sensitive PII:** ID numbers, credentials, financial account details requiring breach notification
    - **Financial Data:** Payment cards, bank accounts, transaction data
    - **Trade Secrets/IP:** Proprietary formulas, strategic plans, customer lists
    - **GDPR Special Categories:** Health, biometric, genetic, race/ethnicity, political/religious views, union membership
    """)
    
    data_type = st.selectbox(
        "What is the most sensitive type of data involved?",
        ["Public or low-sensitivity data",
         "Internal confidential business data",
         "Regular PII (name, email, contact info)",
         "Sensitive PII (government IDs, credentials)",
         "Financial transaction data",
         "Trade secrets or intellectual property",
         "GDPR Special Categories (health, biometric, etc.)"],
        help="Select the highest sensitivity level applicable"
    )
    
    data_third_party = st.radio(
        "Will a third-party vendor or processor have access to this data?", 
        ["YES", "NO"],
        help="Including cloud services, SaaS platforms, contractors"
    )
    
    st.markdown("---")
    st.markdown("### 7. Stakeholder Context")
    
    stake_requestor_level = st.selectbox(
        "Who is championing or requesting this initiative?",
        ["Team or individual contributor", 
         "Department or business unit leadership", 
         "Multiple business unit heads",
         "Board member or C-suite executive", 
         "Regulatory inquiry or audit finding",
         "External audit finding"],
        help="Select the highest-level stakeholder driving this request"
    )
    
    stake_urgency = st.text_area(
        "What is the specific business consequence if this is delayed?",
        help="Be concrete: revenue impact, compliance deadline, customer commitments, etc.",
        placeholder="Example: Failure to remediate by Q2 may result in $5M+ penalty under FCPA"
    )
    stake_urgency_clear = "YES" if len(stake_urgency) > 20 else "NO"
    
    st.markdown("---")
    
    submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True, type="primary")
    
    if submitted:
        # Validate required fields
        if not project_title or not requestor_name or not requestor_email:
            st.error("❌ Please fill all required fields marked with *")
        else:
            # Calculate scores
            scores = {
                'reg': calculate_regulatory_score(reg_required, reg_deadline, reg_enforcement),
                'rep': calculate_reputational_score(rep_risk_level, ','.join(rep_harm_categories), rep_liability),
                'strat': calculate_strategic_score(strat_document, strat_sponsor, strat_budget),
                'op': calculate_operational_score(op_efficiency_gain, op_scope, op_blocker),
                'res': calculate_resource_score(res_approach, 0, ''),  # No external deps from requestor,
                'data': calculate_data_score(data_type, data_third_party, "N/A"),
                'stake': calculate_stakeholder_score(stake_requestor_level, stake_urgency_clear)
            }
            
            total_score = calculate_total_score(scores)
            priority = get_priority(total_score)
            
            # Prepare data
            project_data = {
                'project_title': project_title,
                'requestor_name': requestor_name,
                'requestor_email': requestor_email,
                'department': department,
                'submission_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'Submitted',
                
                'reg_required': reg_required,
                'reg_citation': reg_citation,
                'reg_deadline': reg_deadline,
                'reg_enforcement': reg_enforcement,
                'reg_score': scores['reg'],
                
                'rep_headline': rep_headline,
                'rep_risk_level': rep_risk_level,
                'rep_harm_categories': ','.join(rep_harm_categories),
                'rep_liability': rep_liability,
                'rep_score': scores['rep'],
                
                'strat_document': strat_document,
                'strat_sponsor': strat_sponsor,
                'strat_budget': strat_budget,
                'strat_score': scores['strat'],
                
                'op_process_name': op_process_name,
                'op_current_time': op_current_time,
                'op_projected_time': op_projected_time,
                'op_efficiency_gain': op_efficiency_gain,
                'op_scope': op_scope,
                'op_score': scores['op'],
                
                'res_approach': res_approach,
                'res_total_hours': 0,
                'res_external_deps': '',  # Empty - will be filled by Compliance Officer
                'res_score': scores['res'],
                
                'data_type': data_type,
                'data_third_party': data_third_party,
                'data_volume': 'N/A',
                'data_score': scores['data'],
                
                'stake_requestor_level': stake_requestor_level,
                'stake_urgency': stake_urgency,
                'stake_score': scores['stake'],
                
                'total_score': total_score,
                'priority': priority
            }
            
            # Check red flags
            red_flags = check_red_flags(project_data)
            project_data['red_flags'] = ', '.join(red_flags) if red_flags else None
            project_data['auto_reject'] = 1 if red_flags else 0
            
            # Submit to database
            try:
                project_id = st.session_state.db.submit_project(project_data)
                
                st.success(f"✅ Project submitted successfully! (Reference ID: {project_id})")
                st.info("""
                **Next Steps:**
                - Your request will be reviewed by the Compliance team
                - You will be notified of the decision via email
                - Typical review time: 3-5 business days
                """)
                
                # DO NOT show scoring to requestor
                
            except Exception as e:
                st.error(f"❌ Error submitting project: {str(e)}")
                st.info("Please try again or contact IT support if the problem persists.")
