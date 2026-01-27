import streamlit as st
from utils.database import Database
import pandas as pd

st.set_page_config(page_title="Admin", page_icon="⚙️", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

if st.session_state.user['role'] != 'compliance_officer':
    st.error("❌ Access denied. Admin privileges required.")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("⚙️ System Administration")

tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "⚙️ System Config", "🗄️ Database", "📋 Audit Log"])

with tab1:
    st.markdown("### 👥 User Management")
    
    st.info("""
    **Note:** Current implementation uses simple authentication for demo purposes.  
    For production, implement proper authentication (OAuth, SAML, Active Directory integration).
    """)
    
    # Current users display
    st.markdown("#### Current System Users")
    
    users_data = {
        'Username': ['admin', 'requestor'],
        'Role': ['Compliance Officer', 'Requestor'],
        'Email': ['admin@company.com', 'requestor@company.com'],
        'Status': ['Active', 'Active']
    }
    users_df = pd.DataFrame(users_data)
    st.dataframe(users_df, use_container_width=True, hide_index=True)
    
    # Add user form
    with st.expander("➕ Add New User", expanded=False):
        st.warning("⚠️ User management functionality is simplified for demo. In production, integrate with your organization's identity provider.")
        
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username *")
                new_password = st.text_input("Password *", type="password")
            with col2:
                new_role = st.selectbox("Role *", ["requestor", "compliance_officer"])
                new_email = st.text_input("Email *")
            
            submit_user = st.form_submit_button("Add User")
            
            if submit_user:
                if new_username and new_password and new_email:
                    st.info(f"✓ User '{new_username}' would be added with role '{new_role}'")
                    st.warning("Note: This is a demo. In production, use proper user management system.")
                else:
                    st.error("Please fill all required fields")
    
    # User roles explanation
    with st.expander("ℹ️ Role Permissions"):
        st.markdown("""
        **Compliance Officer:**
        - Full access to Review Queue
        - Can approve/reject projects
        - Can override scores
        - Can delete projects
        - Access to Dashboard and Admin panel
        - Can view deleted projects archive
        
        **Requestor:**
        - Can submit new project requests
        - Can view own submissions
        - Can view Dashboard (read-only)
        - Cannot access Review Queue or Admin panel
        - Cannot see scoring details
        """)

with tab2:
    st.markdown("### ⚙️ Scoring Configuration")
    
    st.markdown("#### Current Scoring Weights")
    
    weights_data = {
        'Criterion': [
            '1. Regulatory Risk',
            '2. Reputational Risk',
            '3. Strategic Alignment',
            '4. Operational Impact',
            '5. Implementation Complexity',
            '6. Data Sensitivity',
            '7. Stakeholder Pressure'
        ],
        'Weight': ['25%', '20%', '15%', '15%', '10%', '10%', '5%'],
        'Description': [
            'Compliance deadlines, enforcement',
            'Stakeholder harm, liability exposure',
            'Corporate strategy linkage',
            'Efficiency gains, scope of impact',
            'Technical approach, dependencies',
            'Data types, third-party access',
            'Executive/regulatory pressure'
        ]
    }
    weights_df = pd.DataFrame(weights_data)
    st.dataframe(weights_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### Priority Thresholds")
    
    thresholds_data = {
        'Priority Level': ['🔴 IMMEDIATE', '🟡 PLANNED', '⚪ DEFER'],
        'Score Range': ['≥ 70 points', '50-69 points', '< 50 points'],
        'Expected Action': [
            'Fast-track approval, assign resources within 5 business days',
            'Add to quarterly plan, assign within 30 days',
            'Defer or reject, revisit in 6 months'
        ]
    }
    thresholds_df = pd.DataFrame(thresholds_data)
    st.dataframe(thresholds_df, use_container_width=True, hide_index=True)
    
    st.warning("""
    ⚠️ **To modify weights or thresholds:**
    - Edit `utils/scoring.py` → `calculate_total_score()` function
    - Edit `utils/scoring.py` → `get_priority()` function
    - Changes require code deployment
    - Test thoroughly before production changes
    """)
    
    # Calibration notes
    with st.expander("📊 Calibration Guidance"):
        st.markdown("""
        **When to adjust weights:**
        
        1. **After first 20-30 projects:**
           - Analyze if high-scored projects are truly high priority
           - Check if low-scored projects are appropriately deferred
           - Look for systematic over/under-weighting
        
        2. **Regulatory landscape changes:**
           - If regulatory environment intensifies → increase Regulatory weight
           - If moving to more strategic focus → increase Strategic weight
        
        3. **Organizational priorities shift:**
           - New CEO focus on operational efficiency → increase Operational weight
           - Data privacy incidents → increase Data Sensitivity weight
        
        **Example adjustment scenarios:**
        
        - "Too many regulatory projects scoring high" → Reduce Regulatory from 25% to 20%
        - "Strategic projects not prioritized" → Increase Strategic from 15% to 20%
        - "Everything scores 60-70" → Adjust thresholds: IMMEDIATE >75, PLANNED 55-75
        
        **Best practice:**
        - Document all changes in git commit messages
        - Notify stakeholders before changes
        - Re-score existing pending projects after weight changes
        """)

with tab3:
    st.markdown("### 🗄️ Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Statistics")
        
        projects = st.session_state.db.get_projects()
        
        # Active projects
        if 'deleted' in projects.columns:
            active_projects = projects[projects['deleted'] == 0]
            deleted_count = len(projects[projects['deleted'] == 1])
        else:
            active_projects = projects
            deleted_count = 0
        
        st.metric("Active Projects", len(active_projects))
        st.metric("Deleted Projects (Archive)", deleted_count)
        
        # Status breakdown
        if len(active_projects) > 0:
            status_counts = active_projects['status'].value_counts()
            for status, count in status_counts.items():
                st.metric(f"Status: {status}", count)
        
        if st.button("🔄 Refresh Statistics"):
            st.rerun()
    
    with col2:
        st.markdown("#### Maintenance Operations")
        
        st.info("Administrative database operations")
        
        # View deleted projects
        if st.button("🗑️ View Deleted Projects Archive", use_container_width=True):
            st.session_state['show_deleted'] = True
        
        # Database info
        with st.expander("💾 Database Information"):
            st.markdown("""
            **Current Setup:**
            - **Database:** SQLite (local file)
            - **Location:** `/home/claude/project_scoring.db`
            - **Persistence:** Ephemeral (resets on restart)
            
            **For Production:**
            - Migrate to PostgreSQL or MySQL
            - Set up regular backups
            - Implement connection pooling
            - Enable audit logging
            
            **Current Limitations:**
            - Data lost on app restart (Streamlit Cloud)
            - Single concurrent connection
            - No automated backups
            """)
    
    # Show deleted projects archive
    if st.session_state.get('show_deleted', False):
        st.markdown("---")
        st.markdown("### 🗑️ Deleted Projects Archive")
        
        deleted_projects = st.session_state.db.get_deleted_projects()
        
        if len(deleted_projects) > 0:
            st.markdown(f"**Total Deleted Projects:** {len(deleted_projects)}")
            
            # Display deleted projects
            display_cols = ['id', 'project_title', 'requestor_name', 'department', 
                          'deleted_by', 'deleted_date', 'deletion_reason']
            
            # Check which columns exist
            available_cols = [col for col in display_cols if col in deleted_projects.columns]
            
            st.dataframe(
                deleted_projects[available_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "deleted_date": st.column_config.DatetimeColumn("Deleted On", format="DD/MM/YYYY HH:mm")
                }
            )
            
            # Restore functionality
            st.markdown("#### ♻️ Restore Deleted Project")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                restore_id = st.selectbox(
                    "Select Project ID to Restore",
                    deleted_projects['id'].tolist(),
                    help="Restoring will move the project back to 'Submitted' status"
                )
                
                if restore_id:
                    # Show project details
                    restore_project = deleted_projects[deleted_projects['id'] == restore_id].iloc[0]
                    st.info(f"""
                    **Project:** {restore_project['project_title']}  
                    **Deleted by:** {restore_project.get('deleted_by', 'Unknown')}  
                    **Reason:** {restore_project.get('deletion_reason', 'No reason provided')}
                    """)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                if st.button("♻️ Restore", type="primary", use_container_width=True):
                    try:
                        st.session_state.db.restore_project(restore_id)
                        st.success(f"✅ Project #{restore_id} has been restored to active queue")
                        import time
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error restoring project: {str(e)}")
        else:
            st.info("📭 No deleted projects in archive")
        
        # Back button
        st.markdown("---")
        if st.button("← Back to Database Management"):
            st.session_state['show_deleted'] = False
            st.rerun()
    
    # Raw database view (for debugging)
    if not st.session_state.get('show_deleted', False):
        with st.expander("📋 View Raw Database (Active Projects)", expanded=False):
            if len(active_projects) > 0:
                st.dataframe(active_projects, use_container_width=True)
                
                # Download raw data
                csv_raw = active_projects.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Raw Data (CSV)",
                    data=csv_raw,
                    file_name=f"raw_projects_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No active projects in database")

with tab4:
    st.markdown("### 📋 Audit Log")
    
    st.info("""
    **Audit logging tracks:**
    - Project submissions (who, when, what)
    - Score overrides (original → new, justification)
    - Approval/rejection decisions
    - Project deletions (who, when, why)
    - Project restorations
    """)
    
    # Get recent activity
    projects = st.session_state.db.get_projects()
    
    if len(projects) > 0:
        st.markdown("#### Recent Activity")
        
        # Create activity log from existing data
        activity_log = []
        
        for _, project in projects.iterrows():
            # Submission
            activity_log.append({
                'Date': project['submission_date'],
                'Action': 'Project Submitted',
                'User': project['requestor_name'],
                'Project': f"#{project['id']} - {project['project_title']}",
                'Details': f"Department: {project['department']}"
            })
            
            # Review
            if project.get('co_reviewed_by') and project.get('co_reviewed_date'):
                activity_log.append({
                    'Date': project['co_reviewed_date'],
                    'Action': 'Project Reviewed',
                    'User': project['co_reviewed_by'],
                    'Project': f"#{project['id']} - {project['project_title']}",
                    'Details': f"Decision: {project.get('co_decision', 'N/A')}"
                })
            
            # Override
            if project.get('co_override_reg') or project.get('co_override_rep'):
                activity_log.append({
                    'Date': project.get('co_reviewed_date', 'N/A'),
                    'Action': 'Scores Overridden',
                    'User': project.get('co_reviewed_by', 'N/A'),
                    'Project': f"#{project['id']} - {project['project_title']}",
                    'Details': 'Compliance officer adjusted scoring'
                })
            
            # Deletion
            if project.get('deleted') == 1 and project.get('deleted_date'):
                activity_log.append({
                    'Date': project['deleted_date'],
                    'Action': 'Project Deleted',
                    'User': project.get('deleted_by', 'Unknown'),
                    'Project': f"#{project['id']} - {project['project_title']}",
                    'Details': f"Reason: {project.get('deletion_reason', 'N/A')}"
                })
        
        # Convert to dataframe and sort
        if activity_log:
            audit_df = pd.DataFrame(activity_log)
            audit_df['Date'] = pd.to_datetime(audit_df['Date'], errors='coerce')
            audit_df = audit_df.sort_values('Date', ascending=False)
            
            # Display recent 50 activities
            st.dataframe(
                audit_df.head(50),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DatetimeColumn("Timestamp", format="DD/MM/YYYY HH:mm:ss")
                }
            )
            
            # Export audit log
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                csv_audit = audit_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Audit Log (CSV)",
                    data=csv_audit,
                    file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Filter options
                if st.button("🔍 Advanced Filters", use_container_width=True):
                    st.session_state['show_audit_filters'] = not st.session_state.get('show_audit_filters', False)
            
            # Advanced filters
            if st.session_state.get('show_audit_filters', False):
                st.markdown("---")
                st.markdown("#### Filter Audit Log")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    action_filter = st.multiselect(
                        "Action Type",
                        audit_df['Action'].unique().tolist()
                    )
                
                with col2:
                    user_filter = st.multiselect(
                        "User",
                        audit_df['User'].unique().tolist()
                    )
                
                with col3:
                    date_range = st.date_input(
                        "Date Range",
                        value=[]
                    )
                
                # Apply filters
                filtered_df = audit_df.copy()
                
                if action_filter:
                    filtered_df = filtered_df[filtered_df['Action'].isin(action_filter)]
                
                if user_filter:
                    filtered_df = filtered_df[filtered_df['User'].isin(user_filter)]
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_df = filtered_df[
                        (filtered_df['Date'].dt.date >= start_date) & 
                        (filtered_df['Date'].dt.date <= end_date)
                    ]
                
                st.markdown(f"**Filtered Results:** {len(filtered_df)} activities")
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.info("No audit activity recorded yet")
    else:
        st.info("No projects in system yet - audit log will appear after first submission")
    
    # Audit configuration
    with st.expander("⚙️ Audit Configuration"):
        st.markdown("""
        **Current Audit Settings:**
        - ✅ Project submissions logged
        - ✅ Reviews and decisions logged
        - ✅ Score overrides logged
        - ✅ Deletions logged
        - ❌ Login attempts (not implemented)
        - ❌ Failed actions (not implemented)
        - ❌ System changes (not implemented)
        
        **For Production:**
        - Implement comprehensive audit trail
        - Log all authentication attempts
        - Track configuration changes
        - Store logs in separate audit database
        - Enable log retention policies (7 years for compliance)
        - Implement log tampering protection
        - Set up automated log analysis and alerts
        """)

# System information footer
st.markdown("---")
st.markdown("### 💻 System Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Application Version:**  
    Version 1.0.0  
    Last Updated: 2025-01-27
    """)

with col2:
    st.markdown("""
    **Environment:**  
    Streamlit Cloud  
    Python 3.13  
    SQLite Database
    """)

with col3:
    st.markdown("""
    **Support:**  
    IT Helpdesk  
    compliance@company.com  
    [Documentation](#)
    """)
