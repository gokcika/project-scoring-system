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
    st.error("❌ Access denied. Compliance Officer role required.")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("⚖️ Review Queue - Compliance Officer")

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.selectbox("Filter by Status", 
        ["All", "Submitted", "Under Review", "Approved", "Rejected", "Deleted"])
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

# Filter out deleted projects unless specifically requested
if status_filter != "Deleted":
    if 'deleted' in projects.columns:
        projects = projects[projects['deleted'] == 0]

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
            if project.get('auto_reject') == 1:
                st.error(f"⚠️ **AUTO-REJECT FLAGS:** {project.get('red_flags', 'N/A')}")
            
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
                
                st.markdown("#### 1. Regulatory & Compliance Requirements")
                st.text_input("Regulatory Required?", project['reg_required'], disabled=True)
                if project['reg_required'] == "YES":
                    st.text_area("Citation", project.get('reg_citation', ''), disabled=True)
                    st.text_input("Deadline", project.get('reg_deadline', ''), disabled=True)
                    st.text_input("Enforcement Evidence", project.get('reg_enforcement', ''), disabled=True)
                
                st.markdown("#### 2. Risk Assessment")
                st.text_input("Primary Risk/Impact", project.get('rep_headline', ''), disabled=True)
                st.text_input("Risk Level", project.get('rep_risk_level', ''), disabled=True)
                st.text_input("Affected Parties", project.get('rep_harm_categories', ''), disabled=True)
                st.text_input("Liability Exposure", project.get('rep_liability', ''), disabled=True)
                
                st.markdown("#### 3. Strategic Alignment")
                st.text_input("Documentation Level", project.get('strat_document', ''), disabled=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Executive Sponsor?", project.get('strat_sponsor', ''), disabled=True)
                with col2:
                    st.text_input("Budget Allocated?", project.get('strat_budget', ''), disabled=True)
                
                st.markdown("#### 4. Operational Impact")
                st.text_input("Process Name", project.get('op_process_name', ''), disabled=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.number_input("Current Time (hrs)", value=float(project.get('op_current_time', 0) or 0), disabled=True)
                with col2:
                    st.number_input("Projected Time (hrs)", value=float(project.get('op_projected_time', 0) or 0), disabled=True)
                with col3:
                    st.metric("Efficiency Gain", f"{project.get('op_efficiency_gain', 0):.1f}%")
                st.text_input("Scope", project.get('op_scope', ''), disabled=True)
                st.text_input("Blocking Other Initiatives?", project.get('op_blocker', ''), disabled=True if 'op_blocker' in project else True)
                
                st.markdown("#### 5. Implementation Approach")

col1, col2 = st.columns(2)
with col1:
    st.text_input("Approach", project.get('res_approach', ''), disabled=True)
with col2:
    # External Dependencies - Compliance Officer can edit
    current_deps = project.get('res_external_deps', '')
    if not current_deps or current_deps == '':
        st.info("⚠️ External dependencies not yet assessed by Compliance Officer")
    else:
        st.text_input("External Dependencies", current_deps, disabled=True)

# Add edit form for external dependencies
with st.expander("✏️ Edit External Dependencies (Compliance Officer Only)"):
    st.markdown("**Note:** This assessment is performed by Compliance Officers only, not visible to requestors.")
    
    with st.form(f"external_deps_form_{selected_id}"):
        new_external_deps = st.multiselect(
            "External dependencies for this project",
            ["None", "Third-party vendor required", "Multiple system integrations needed"],
            default=[d.strip() for d in current_deps.split(',') if d.strip()] if current_deps else [],
            help="Select all dependencies identified during review"
        )
        
        deps_notes = st.text_area(
            "Notes on external dependencies",
            placeholder="Document specific vendors, integrations, or external factors...",
            help="Optional: provide context for future reference"
        )
        
        submit_deps = st.form_submit_button("💾 Save Dependencies Assessment")
        
        if submit_deps:
            update_data = {
                'res_external_deps': ','.join(new_external_deps),
                'co_reviewed_by': st.session_state.user['username'],
                'co_reviewed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Recalculate resource score with new dependencies
            from utils.scoring import calculate_resource_score
            new_res_score = calculate_resource_score(
                project.get('res_approach', ''),
                0,
                ','.join(new_external_deps)
            )
            update_data['res_score'] = new_res_score
            
            # Recalculate total if no override exists
            if not project.get('co_final_score'):
                from utils.scoring import calculate_total_score, get_priority
                scores = {
                    'reg': project.get('reg_score', 0),
                    'rep': project.get('rep_score', 0),
                    'strat': project.get('strat_score', 0),
                    'op': project.get('op_score', 0),
                    'res': new_res_score,
                    'data': project.get('data_score', 0),
                    'stake': project.get('stake_score', 0)
                }
                new_total = calculate_total_score(scores)
                new_priority = get_priority(new_total)
                update_data['total_score'] = new_total
                update_data['priority'] = new_priority
            
            st.session_state.db.update_project(selected_id, update_data)
            st.success("✅ External dependencies assessment saved and score updated")
            
            import time
            time.sleep(1)
            st.rerun()
                
            st.markdown("#### 6. Data & Privacy Considerations")
                st.text_input("Data Type", project.get('data_type', ''), disabled=True)
                st.text_input("Third Party Access?", project.get('data_third_party', ''), disabled=True)
                
                st.markdown("#### 7. Stakeholder Context")
                st.text_input("Requestor Level", project.get('stake_requestor_level', ''), disabled=True)
                st.text_area("Urgency Justification", project.get('stake_urgency', ''), disabled=True)
            
            with tab2:
                st.markdown("#### Current Scoring Breakdown")
                
                score_data = {
                    'Criterion': ['Regulatory', 'Reputational', 'Strategic', 'Operational', 
                                 'Resources', 'Data', 'Stakeholder'],
                    'Raw Score': [
                        project.get('reg_score', 0),
                        project.get('rep_score', 0),
                        project.get('strat_score', 0),
                        project.get('op_score', 0),
                        project.get('res_score', 0),
                        project.get('data_score', 0),
                        project.get('stake_score', 0)
                    ],
                    'Weight': ['25%', '20%', '15%', '15%', '10%', '10%', '5%'],
                    'Weighted': [
                        project.get('reg_score', 0) * 5,
                        project.get('rep_score', 0) * 4,
                        project.get('strat_score', 0) * 3,
                        project.get('op_score', 0) * 3,
                        project.get('res_score', 0) * 2,
                        project.get('data_score', 0) * 2,
                        project.get('stake_score', 0) * 1
                    ]
                }
                
                df_scores = pd.DataFrame(score_data)
                st.dataframe(df_scores, use_container_width=True, hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Score", f"{project.get('total_score', 0):.1f}/100")
                with col2:
                    st.metric("Priority", project.get('priority', 'N/A'))
            
            with tab3:
                st.markdown("#### Override Scores")
                
                st.info("""
                **When to override:** If the automatic scoring does not accurately reflect the true priority or risk level based on your expert judgment.
                
                **Original scores** are shown below. You can increase (+) or decrease (-) any score, or leave it unchanged.
                """)
                
                with st.form(f"override_form_{selected_id}"):
                    st.markdown("---")
                    
                    # Regulatory
                    st.markdown("##### 1. Regulatory Risk")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('reg_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_reg = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_reg') or project.get('reg_score', 3.0)),
                            step=0.5,
                            key="override_reg",
                            help="Move slider to adjust score"
                        )
                        if override_reg > project.get('reg_score', 0):
                            st.success(f"↑ Increased by {override_reg - project.get('reg_score', 0):.1f}")
                        elif override_reg < project.get('reg_score', 0):
                            st.warning(f"↓ Decreased by {project.get('reg_score', 0) - override_reg:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Reputational
                    st.markdown("##### 2. Reputational Risk")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('rep_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_rep = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_rep') or project.get('rep_score', 3.0)),
                            step=0.5,
                            key="override_rep"
                        )
                        if override_rep > project.get('rep_score', 0):
                            st.success(f"↑ Increased by {override_rep - project.get('rep_score', 0):.1f}")
                        elif override_rep < project.get('rep_score', 0):
                            st.warning(f"↓ Decreased by {project.get('rep_score', 0) - override_rep:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Strategic
                    st.markdown("##### 3. Strategic Alignment")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('strat_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_strat = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_strat') or project.get('strat_score', 3.0)),
                            step=0.5,
                            key="override_strat"
                        )
                        if override_strat > project.get('strat_score', 0):
                            st.success(f"↑ Increased by {override_strat - project.get('strat_score', 0):.1f}")
                        elif override_strat < project.get('strat_score', 0):
                            st.warning(f"↓ Decreased by {project.get('strat_score', 0) - override_strat:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Operational
                    st.markdown("##### 4. Operational Impact")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('op_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_op = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_op') or project.get('op_score', 3.0)),
                            step=0.5,
                            key="override_op"
                        )
                        if override_op > project.get('op_score', 0):
                            st.success(f"↑ Increased by {override_op - project.get('op_score', 0):.1f}")
                        elif override_op < project.get('op_score', 0):
                            st.warning(f"↓ Decreased by {project.get('op_score', 0) - override_op:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Resources
                    st.markdown("##### 5. Implementation Complexity")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('res_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_res = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_res') or project.get('res_score', 3.0)),
                            step=0.5,
                            key="override_res"
                        )
                        if override_res > project.get('res_score', 0):
                            st.success(f"↑ Increased by {override_res - project.get('res_score', 0):.1f}")
                        elif override_res < project.get('res_score', 0):
                            st.warning(f"↓ Decreased by {project.get('res_score', 0) - override_res:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Data Sensitivity
                    st.markdown("##### 6. Data Sensitivity")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('data_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_data = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_data') or project.get('data_score', 3.0)),
                            step=0.5,
                            key="override_data"
                        )
                        if override_data > project.get('data_score', 0):
                            st.success(f"↑ Increased by {override_data - project.get('data_score', 0):.1f}")
                        elif override_data < project.get('data_score', 0):
                            st.warning(f"↓ Decreased by {project.get('data_score', 0) - override_data:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Stakeholder
                    st.markdown("##### 7. Stakeholder Pressure")
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.metric("Original Score", f"{project.get('stake_score', 0):.1f} / 5.0")
                    with col2:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'>→</div>", unsafe_allow_html=True)
                    with col3:
                        override_stake = st.slider(
                            "Adjusted Score",
                            min_value=1.0,
                            max_value=5.0,
                            value=float(project.get('co_override_stake') or project.get('stake_score', 3.0)),
                            step=0.5,
                            key="override_stake"
                        )
                        if override_stake > project.get('stake_score', 0):
                            st.success(f"↑ Increased by {override_stake - project.get('stake_score', 0):.1f}")
                        elif override_stake < project.get('stake_score', 0):
                            st.warning(f"↓ Decreased by {project.get('stake_score', 0) - override_stake:.1f}")
                        else:
                            st.info("= No change")
                    
                    st.markdown("---")
                    
                    # Override Justification
                    st.markdown("##### Justification for Changes")
                    override_notes = st.text_area(
                        "Explain why you are adjusting these scores",
                        value=project.get('co_notes') or "",
                        placeholder="Example: Regulatory deadline is more flexible than stated; enforcement pattern is weak in our jurisdiction...",
                        help="Required if any scores are changed"
                    )
                    
                    # Summary of changes
                    changes = []
                    if override_reg != project.get('reg_score', 0):
                        changes.append(f"Regulatory: {project.get('reg_score', 0):.1f} → {override_reg:.1f}")
                    if override_rep != project.get('rep_score', 0):
                        changes.append(f"Reputational: {project.get('rep_score', 0):.1f} → {override_rep:.1f}")
                    if override_strat != project.get('strat_score', 0):
                        changes.append(f"Strategic: {project.get('strat_score', 0):.1f} → {override_strat:.1f}")
                    if override_op != project.get('op_score', 0):
                        changes.append(f"Operational: {project.get('op_score', 0):.1f} → {override_op:.1f}")
                    if override_res != project.get('res_score', 0):
                        changes.append(f"Resources: {project.get('res_score', 0):.1f} → {override_res:.1f}")
                    if override_data != project.get('data_score', 0):
                        changes.append(f"Data: {project.get('data_score', 0):.1f} → {override_data:.1f}")
                    if override_stake != project.get('stake_score', 0):
                        changes.append(f"Stakeholder: {project.get('stake_score', 0):.1f} → {override_stake:.1f}")
                    
                    if changes:
                        st.info("**Changes Summary:**\n" + "\n".join([f"• {c}" for c in changes]))
                    else:
                        st.success("✓ No changes made to original scores")
                    
                    submit_override = st.form_submit_button("💾 Save Adjustments", use_container_width=True, type="primary")
                    
                    if submit_override:
                        # Validation
                        if changes and (not override_notes or len(override_notes) < 10):
                            st.error("❌ Justification is required when changing scores (minimum 10 characters)")
                        else:
                            # Calculate new total
                            final_scores = {
                                'reg': override_reg,
                                'rep': override_rep,
                                'strat': override_strat,
                                'op': override_op,
                                'res': override_res,
                                'data': override_data,
                                'stake': override_stake
                            }
                            
                            final_total = calculate_total_score(final_scores)
                            final_priority = get_priority(final_total)
                            
                            # Update database
                            update_data = {
                                'co_reviewed_by': st.session_state.user['username'],
                                'co_reviewed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'co_override_reg': override_reg if override_reg != project.get('reg_score', 0) else None,
                                'co_override_rep': override_rep if override_rep != project.get('rep_score', 0) else None,
                                'co_override_strat': override_strat if override_strat != project.get('strat_score', 0) else None,
                                'co_override_op': override_op if override_op != project.get('op_score', 0) else None,
                                'co_override_res': override_res if override_res != project.get('res_score', 0) else None,
                                'co_override_data': override_data if override_data != project.get('data_score', 0) else None,
                                'co_override_stake': override_stake if override_stake != project.get('stake_score', 0) else None,
                                'co_final_score': final_total,
                                'priority': final_priority,
                                'co_notes': override_notes,
                                'status': 'Under Review'
                            }
                            
                            st.session_state.db.update_project(selected_id, update_data)
                            
                            # Show results
                            original_total = project.get('total_score', 0)
                            st.success(f"✅ Adjustments saved successfully!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Original Total", f"{original_total:.1f}", delta=None)
                            with col2:
                                delta_val = final_total - original_total
                                st.metric("New Total", f"{final_total:.1f}", delta=f"{delta_val:+.1f}")
                            
                            st.info(f"Priority: {final_priority}")
                            
                            import time
                            time.sleep(2)
                            st.rerun()
            
            with tab4:
                st.markdown("#### Final Decision")
                
                # Calculate final score safely
                try:
                    if project.get('co_final_score') is not None and project['co_final_score'] != '':
                        final_score = float(project['co_final_score'])
                    elif project.get('total_score') is not None and project['total_score'] != '':
                        final_score = float(project['total_score'])
                    else:
                        st.error("⚠️ Score not calculated. Please check Override tab.")
                        final_score = 0.0
                except (ValueError, TypeError):
                    st.error("⚠️ Invalid score value in database.")
                    final_score = 0.0
                
                # Get priority
                current_priority = get_priority(final_score)
                
                # Display score
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Final Score", f"{final_score:.1f}/100")
                with col2:
                    st.metric("Priority", current_priority)
                
                # Decision form
                with st.form(f"decision_form_{selected_id}"):
                    decision = st.radio("Decision", 
                        ["Approve", "Approve with Conditions", "Request More Info", "Reject"])
                    
                    decision_notes = st.text_area(
                        "Decision Notes/Feedback for Requestor",
                        placeholder="Provide clear feedback on your decision and any next steps required..."
                    )
                    
                    submit_decision = st.form_submit_button("✅ Submit Decision", type="primary", use_container_width=True)
                    
                    if submit_decision:
                        if not decision_notes or len(decision_notes) < 10:
                            st.error("❌ Decision notes are required (minimum 10 characters)")
                        else:
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
                            
                            import time
                            time.sleep(2)
                            st.rerun()
                
                # Delete section
                st.markdown("---")
                st.markdown("### ⚠️ Delete Project")
                
                with st.expander("🗑️ Delete This Project", expanded=False):
                    st.warning("""
                    **Caution:** Deleting a project will remove it from active queues. 
                    The project will be archived and can be restored by administrators.
                    """)
                    
                    with st.form(f"delete_form_{selected_id}"):
                        st.markdown("**Why are you deleting this project?** (Required)")
                        
                        deletion_reason = st.text_area(
                            "Deletion Reason",
                            placeholder="Example: Duplicate of project #45, requestor withdrew, merged into larger initiative...",
                            help="This will be logged for audit purposes",
                            label_visibility="collapsed"
                        )
                        
                        delete_confirm = st.checkbox("I confirm that I want to delete this project")
                        
                        submit_delete = st.form_submit_button("🗑️ Delete Project", type="secondary")
                        
                        if submit_delete:
                            if not delete_confirm:
                                st.error("❌ Please check the confirmation box")
                            elif not deletion_reason or len(deletion_reason) < 10:
                                st.error("❌ Please provide a detailed reason (minimum 10 characters)")
                            else:
                                # Soft delete
                                st.session_state.db.soft_delete_project(
                                    selected_id, 
                                    st.session_state.user['username'],
                                    deletion_reason
                                )
                                st.success(f"✅ Project #{selected_id} has been deleted and archived")
                                st.info("The project has been removed from active queues but is retained for audit purposes.")
                                
                                # Wait 2 seconds then rerun
                                import time
                                time.sleep(2)
                                st.rerun()
