import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import Database
from utils.scoring import calculate_total_score, get_priority

st.set_page_config(page_title="Review Queue", page_icon="⚖️", layout="wide")

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

if st.session_state.user['role'] != 'compliance_officer':
    st.error("Access denied. Compliance Officer role required.")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("⚖️ Review Queue - Compliance Officer")

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.selectbox("Filter by Status", 
        ["All", "Submitted", "Under Review", "Approved", "Rejected"])
with col2:
    priority_filter = st.selectbox("Filter by Priority",
        ["All", "🔴 IMMEDIATE", "🟡 PLANNED", "⚪ DEFER"])
with col3:
    dept_filter = st.selectbox("Filter by Department",
        ["All", "IT", "Finance", "HR", "Operations", "Sales", "Legal", "Compliance", "Other"])

# Get projects
if status_filter == "All":
    projects = st.session_state.db.get_projects()
else:
    projects = st.session_state.db.get_projects(status=status_filter)

# Apply additional filters
if priority_filter != "All":
    projects = projects[projects['priority'] == priority_filter]
if dept_filter != "All":
    projects = projects[projects['department'] == dept_filter]

st.markdown(f"### Found {len(projects)} projects")

if len(projects) == 0:
    st.info("No projects found with selected filters.")
else:
    # Display projects table
    display_cols = ['id', 'project_title', 'requestor_name', 'department', 
                    'total_score', 'priority', 'status', 'submission_date']
    
    st.dataframe(
        projects[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "total_score": st.column_config.NumberColumn("Score", format="%.1f"),
            "submission_date": st.column_config.DatetimeColumn("Submitted", format="DD/MM/YYYY HH:mm")
        }
    )
    
    st.markdown("---")
    
    # Project review section
    st.markdown("### 📋 Review Project Details")
    
    project_ids = projects['id'].tolist()
    selected_id = st.selectbox("Select Project ID to Review", project_ids)
    
    if selected_id:
        project = st.session_state.db.get_project(selected_id)
        
        if project:
            # Display project info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{project['total_score']:.1f}/100")
            with col2:
                st.metric("Priority", project['priority'])
            with col3:
                st.metric("Status", project['status'])
            
            # Red flags warning
            if project['auto_reject'] == 1:
                st.error(f"⚠️ **AUTO-REJECT FLAGS:** {project['red_flags']}")
            
            # Tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Details", "📊 Scoring", "✏️ Override", "✅ Decision"])
            
            with tab1:
                st.markdown("#### Basic Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Project Title", project['project_title'], disabled=True)
                    st.text_input("Requestor", project['requestor_name'], disabled=True)
                    st.text_input("Email", project['requestor_email'], disabled=True)
                with col2:
                    st.text_input("Department", project['department'], disabled=True)
                    st.text_input("Submitted", project['submission_date'], disabled=True)
                
                st.markdown("#### Section 1: Regulatory Risk")
                st.text_input("Regulatory Required?", project['reg_required'], disabled=True)
                if project['reg_required'] == "YES":
                    st.text_area("Citation", project['reg_citation'], disabled=True)
                    st.text_input("Deadline", project['reg_deadline'], disabled=True)
                
                st.markdown("#### Section 2: Reputational Risk")
                st.text_input("Hypothetical Headline", project['rep_headline'], disabled=True)
                st.text_input("Risk Level", project['rep_risk_level'], disabled=True)
                st.text_input("Harm Categories", project['rep_harm_categories'], disabled=True)
                
                st.markdown("#### Section 3: Strategic Alignment")
                st.text_input("Document Reference", project['strat_document'], disabled=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Executive Sponsor?", project['strat_sponsor'], disabled=True)
                with col2:
                    st.text_input("Budget Allocated?", project['strat_budget'], disabled=True)
                
                st.markdown("#### Section 4: Operational Impact")
                st.text_input("Process Name", project['op_process_name'], disabled=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.number_input("Current Time (hrs)", value=float(project['op_current_time'] or 0), disabled=True)
                with col2:
                    st.number_input("Projected Time (hrs)", value=float(project['op_projected_time'] or 0), disabled=True)
                with col3:
                    st.metric("Efficiency Gain", f"{project['op_efficiency_gain']:.1f}%")
                
                st.markdown("#### Section 5: Implementation Approach")
                st.text_input("Approach", project['res_approach'], disabled=True)
                st.number_input("External Dependencies", project['res_external_deps'] , disabled=True)
                
                st.markdown("#### Section 6: Data Sensitivity")
                st.text_input("Data Type", project['data_type'], disabled=True)
                st.text_input("Third Party Access?", project['data_third_party'], disabled=True)
                
                st.markdown("#### Section 7: Stakeholder Pressure")
                st.text_input("Requestor Level", project['stake_requestor_level'], disabled=True)
                st.text_area("Urgency Justification", project['stake_urgency'], disabled=True)
            
            with tab2:
                st.markdown("#### Current Scoring Breakdown")
                
                score_data = {
                    'Criterion': ['Regulatory', 'Reputational', 'Strategic', 'Operational', 
                                 'Resources', 'Data', 'Stakeholder'],
                    'Raw Score': [
                        project['reg_score'],
                        project['rep_score'],
                        project['strat_score'],
                        project['op_score'],
                        project['res_score'],
                        project['data_score'],
                        project['stake_score']
                    ],
                    'Weight': ['25%', '20%', '15%', '15%', '10%', '10%', '5%'],
                    'Weighted': [
                        project['reg_score'] * 5,  # *5 to show weighted score out of 25
                        project['rep_score'] * 4,
                        project['strat_score'] * 3,
                        project['op_score'] * 3,
                        project['res_score'] * 2,
                        project['data_score'] * 2,
                        project['stake_score'] * 1
                    ]
                }
                
                df_scores = pd.DataFrame(score_data)
                st.dataframe(df_scores, use_container_width=True, hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Score", f"{project['total_score']:.1f}/100")
                with col2:
                    st.metric("Priority", project['priority'])
            
            with tab3:
                st.markdown("#### Override Scores (if needed)")
                st.info("Leave blank to keep original score. Enter 1-5 to override.")
                
                with st.form(f"override_form_{selected_id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        override_reg = st.number_input("Regulatory", 
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_reg'] or 0),
                            help="Current: " + str(project['reg_score']))
                        
                        override_rep = st.number_input("Reputational",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_rep'] or 0),
                            help="Current: " + str(project['rep_score']))
                        
                        override_strat = st.number_input("Strategic",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_strat'] or 0),
                            help="Current: " + str(project['strat_score']))
                        
                        override_op = st.number_input("Operational",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_op'] or 0),
                            help="Current: " + str(project['op_score']))
                    
                    with col2:
                        override_res = st.number_input("Resources",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_res'] or 0),
                            help="Current: " + str(project['res_score']))
                        
                        override_data = st.number_input("Data Sensitivity",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_data'] or 0),
                            help="Current: " + str(project['data_score']))
                        
                        override_stake = st.number_input("Stakeholder",
                            min_value=0.0, max_value=5.0, step=0.5,
                            value=float(project['co_override_stake'] or 0),
                            help="Current: " + str(project['stake_score']))
                    
                    override_notes = st.text_area("Override Justification", 
                        value=project['co_notes'] or "")
                    
                    submit_override = st.form_submit_button("💾 Save Overrides")
                    
                    if submit_override:
                        # Calculate new scores
                        final_scores = {
                            'reg': override_reg if override_reg > 0 else project['reg_score'],
                            'rep': override_rep if override_rep > 0 else project['rep_score'],
                            'strat': override_strat if override_strat > 0 else project['strat_score'],
                            'op': override_op if override_op > 0 else project['op_score'],
                            'res': override_res if override_res > 0 else project['res_score'],
                            'data': override_data if override_data > 0 else project['data_score'],
                            'stake': override_stake if override_stake > 0 else project['stake_score']
                        }
                        
                        final_total = calculate_total_score(final_scores)
                        final_priority = get_priority(final_total)
                        
                        # Update database
                        update_data = {
                            'co_reviewed_by': st.session_state.user['username'],
                            'co_reviewed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'co_override_reg': override_reg if override_reg > 0 else None,
                            'co_override_rep': override_rep if override_rep > 0 else None,
                            'co_override_strat': override_strat if override_strat > 0 else None,
                            'co_override_op': override_op if override_op > 0 else None,
                            'co_override_res': override_res if override_res > 0 else None,
                            'co_override_data': override_data if override_data > 0 else None,
                            'co_override_stake': override_stake if override_stake > 0 else None,
                            'co_final_score': final_total,
                            'priority': final_priority,
                            'co_notes': override_notes,
                            'status': 'Under Review'
                        }
                        
                        st.session_state.db.update_project(selected_id, update_data)
                        st.success(f"✅ Overrides saved! New score: {final_total:.1f}, Priority: {final_priority}")
                        st.rerun()
            
            with tab4:
                st.markdown("#### Final Decision")
                
                # Show current or overridden score
                final_score = project['co_final_score'] if project['co_final_score'] else project['total_score']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Final Score", f"{final_score:.1f}/100")
                with col2:
                    current_priority = get_priority(final_score)
                    st.metric("Priority", current_priority)
                
                with st.form(f"decision_form_{selected_id}"):
                    decision = st.radio("Decision", 
                        ["Approve", "Approve with Conditions", "Request More Info", "Reject"])
                    
                    decision_notes = st.text_area("Decision Notes/Feedback for Requestor")
                    
                    submit_decision = st.form_submit_button("✅ Submit Decision", type="primary")
                    
                    if submit_decision:
                        status_map = {
                            "Approve": "Approved",
                            "Approve with Conditions": "Approved",
                            "Request More Info": "Info Requested",
                            "Reject": "Rejected"
                        }
                        
                        update_data = {
                            'status': status_map[decision],
                            'co_decision': decision,
                            'co_notes': decision_notes,
                            'co_reviewed_by': st.session_state.user['username'],
                            'co_reviewed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.session_state.db.update_project(selected_id, update_data)
                        st.success(f"✅ Decision submitted: {decision}")
                        st.balloons()
                        st.rerun()
