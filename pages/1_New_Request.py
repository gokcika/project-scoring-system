import streamlit as st
from datetime import datetime
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

with st.form("project_request"):
    st.markdown("### Basic Information")
    
    col1, col2 = st.columns(2)
    with col1:
        project_title = st.text_input("Project Title *", help="Brief descriptive title")
        requestor_name = st.text_input("Your Name *", value=st.session_state.user['username'])
    with col2:
        requestor_email = st.text_input("Your Email *", value=st.session_state.user['email'])
        department = st.selectbox("Department *", 
            ["IT", "Finance", "HR", "Operations", "Sales", "Legal", "Compliance", "Other"])
    
    st.markdown("---")
    st.markdown("### Section 1: Regulatory Risk (Weight: 25%)")
    
    reg_required = st.radio("Is this driven by a specific regulatory requirement?", ["YES", "NO"])
    
    if reg_required == "YES":
        reg_citation = st.text_area("Cite the specific regulation/directive", 
            help="Include regulation name, article/section, and link")
        reg_deadline = st.selectbox("Compliance deadline", 
            ["<3 months", "3-6 months", "6-12 months", ">12 months", "No specific deadline"])
        reg_enforcement = st.radio("Has the regulatory authority issued fines/sanctions in your sector for this?", 
            ["YES", "NO"])
    else:
        reg_citation = ""
        reg_deadline = "No specific deadline"
        reg_enforcement = "NO"
    
    st.markdown("---")
    st.markdown("### Section 2: Reputational/Ethical Risk (Weight: 20%)")
    
    rep_headline = st.text_input("If this issue became public tomorrow, what's the headline?",
        help="Be specific about the scenario")
    
    rep_risk_level = st.select_slider("Current risk level",
        options=[
            "1 - Minimal dimension",
            "2 - Proactive positioning",
            "3 - Potential exposure",
            "4 - Known vulnerability",
            "5 - Active issue (media/complaints)"
        ])
    
    rep_harm_categories = st.multiselect("Who is harmed if this fails?",
        ["Customers/clients", "Employees", "Shareholders", "Community/environment", "Company reputation only"])
    
    rep_liability = st.selectbox("Potential liability exposure",
        [">€1M", "€100K-€1M", "<€100K or uncertain"])
    
    st.markdown("---")
    st.markdown("### Section 3: Strategic Alignment (Weight: 15%)")
    
    strat_document = st.selectbox("Where does this appear in corporate documentation?",
        ["CEO/Board strategic plan", "Division/BU annual strategy", "Departmental objectives",
         "Operational improvement", "Not in strategic docs"])
    
    strat_sponsor = st.radio("Do you have executive sponsor confirmation in writing?", ["YES", "NO"])
    strat_budget = st.radio("Has budget been pre-allocated?", ["YES", "NO"])
    
    st.markdown("---")
    st.markdown("### Section 4: Operational Impact (Weight: 15%)")
    
    op_process_name = st.text_input("What specific process/operation is impacted?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        op_current_time = st.number_input("Current: Time per iteration (hours)", min_value=0.0, step=0.5)
    with col2:
        op_projected_time = st.number_input("Projected: Time per iteration (hours)", min_value=0.0, step=0.5)
    with col3:
        if op_current_time > 0:
            op_efficiency_gain = ((op_current_time - op_projected_time) / op_current_time) * 100
            st.metric("Efficiency Gain", f"{op_efficiency_gain:.1f}%")
        else:
            op_efficiency_gain = 0
    
    op_scope = st.radio("Scope of impact", ["Single team", "Single business unit", "3+ business units"])
    op_blocker = st.radio("Is current process blocking other initiatives?", ["YES", "NO"])
    
    st.markdown("---")
    st.markdown("### Section 5: Resource Requirements (Weight: 10%, Inverted)")
    
    res_approach = st.selectbox("Implementation approach",
        ["Existing tool/platform, configuration only",
         "Extend existing platform",
         "New tool, standard implementation",
         "Custom development",
         "Major system overhaul"])
    
    col1, col2 = st.columns(2)
    with col1:
        res_it_hours = st.number_input("IT/Development hours", min_value=0, step=10)
        res_compliance_hours = st.number_input("Compliance/Legal hours", min_value=0, step=5)
    with col2:
        res_sme_hours = st.number_input("Business SME hours", min_value=0, step=5)
        res_testing_hours = st.number_input("Testing/Training hours", min_value=0, step=5)
    
    res_total_hours = res_it_hours + res_compliance_hours + res_sme_hours + res_testing_hours
    st.info(f"**Total estimated hours: {res_total_hours}**")
    
    res_external_deps = st.multiselect("External dependencies",
        ["None", "Vendor/third-party", "Multiple system integration"])
    
    st.markdown("---")
    st.markdown("### Section 6: Data Sensitivity (Weight: 10%)")
    
    data_type = st.selectbox("What type of data is involved?",
        ["Public/low sensitivity",
         "Internal confidential",
         "Regular PII",
         "PII with breach notification",
         "Financial data",
         "Trade secrets/IP",
         "GDPR Special Categories"])
    
    data_third_party = st.radio("Will third-party vendor access this data?", ["YES", "NO"])
    data_volume = st.selectbox("Data volume", ["<10,000 data subjects", ">10,000 data subjects"])
    
    st.markdown("---")
    st.markdown("### Section 7: Stakeholder Pressure (Weight: 5%)")
    
    stake_requestor_level = st.selectbox("Who is requesting this?",
        ["Team/individual", "Single BU leadership", "Multiple BU heads",
         "Board/C-suite", "Regulatory inquiry", "External audit finding"])
    
    stake_urgency = st.text_area("Specific consequence of delay (be concrete)")
    stake_urgency_clear = "YES" if len(stake_urgency) > 20 else "NO"
    
    st.markdown("---")
    
    submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)
    
    if submitted:
        # Validate required fields
        if not project_title or not requestor_name or not requestor_email:
            st.error("Please fill all required fields marked with *")
        else:
            # Calculate scores
            scores = {
                'reg': calculate_regulatory_score(reg_required, reg_deadline, reg_enforcement),
                'rep': calculate_reputational_score(rep_risk_level, ','.join(rep_harm_categories), rep_liability),
                'strat': calculate_strategic_score(strat_document, strat_sponsor, strat_budget),
                'op': calculate_operational_score(op_efficiency_gain, op_scope, op_blocker),
                'res': calculate_resource_score(res_approach, res_total_hours, ','.join(res_external_deps)),
                'data': calculate_data_score(data_type, data_third_party, data_volume),
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
                'res_total_hours': res_total_hours,
                'res_external_deps': ','.join(res_external_deps),
                'res_score': scores['res'],
                
                'data_type': data_type,
                'data_third_party': data_third_party,
                'data_volume': data_volume,
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
            project_id = st.session_state.db.submit_project(project_data)
            
            st.success(f"✅ Project submitted successfully! ID: {project_id}")
            
            # Show scoring result
            st.markdown("### Preliminary Scoring Result")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Score", f"{total_score}/100")
            with col2:
                st.metric("Priority", priority)
            
            with st.expander("Detailed Breakdown"):
                score_df = pd.DataFrame({
                    'Criterion': ['Regulatory', 'Reputational', 'Strategic', 'Operational', 'Resources', 'Data', 'Stakeholder'],
                    'Raw Score': [scores['reg'], scores['rep'], scores['strat'], scores['op'], scores['res'], scores['data'], scores['stake']],
                    'Weight': ['25%', '20%', '15%', '15%', '10%', '10%', '5%']
                })
                st.dataframe(score_df, use_container_width=True, hide_index=True)
            
            if red_flags:
                st.warning(f"⚠️ **Red Flags Detected:** {', '.join(red_flags)}")
                st.info("This project will require special review by Compliance Officer.")
            
            st.info("A Compliance Officer will review your submission soon.")
