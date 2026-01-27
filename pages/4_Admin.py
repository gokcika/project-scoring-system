import streamlit as st
from utils.database import Database
import pandas as pd

st.set_page_config(page_title="Admin", page_icon="⚙️", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

if st.session_state.user['role'] != 'compliance_officer':
    st.error("Access denied. Admin privileges required.")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("⚙️ System Administration")

tab1, tab2, tab3 = st.tabs(["Users", "System Config", "Database"])

with tab1:
    st.markdown("### 👥 User Management")
    st.info("Simple auth - In production, use proper authentication (OAuth, SAML, etc.)")
    
    # Add user form
    with st.expander("➕ Add New User"):
        with st.form("add_user"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["requestor", "compliance_officer"])
            new_email = st.text_input("Email")
            
            if st.form_submit_button("Add User"):
                # Would add to database - simplified for demo
                st.success(f"User {new_username} would be added (not implemented in demo)")

with tab2:
    st.markdown("### ⚙️ Scoring Configuration")
    
    st.markdown("#### Current Weights")
    weights_df = pd.DataFrame({
        'Criterion': ['Regulatory', 'Reputational', 'Strategic', 'Operational', 
                     'Resources', 'Data', 'Stakeholder'],
        'Weight': ['25%', '20%', '15%', '15%', '10%', '10%', '5%']
    })
    st.dataframe(weights_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### Priority Thresholds")
    st.info("""
    - 🔴 IMMEDIATE: Score ≥ 70
    - 🟡 PLANNED: Score 50-69
    - ⚪ DEFER: Score < 50
    """)
    
    st.warning("⚠️ To change weights/thresholds, modify `utils/scoring.py`")

with tab3:
    st.markdown("### 🗄️ Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Info")
        projects = st.session_state.db.get_projects()
        st.metric("Total Records", len(projects))
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        st.markdown("#### Maintenance")
        st.warning("Dangerous operations!")
        
        if st.button("🗑️ Clear All Test Data", type="secondary"):
            st.error("Not implemented - would delete all projects marked as test")
    
    # Show raw data
    with st.expander("📋 View Raw Database"):
        if len(projects) > 0:
            st.dataframe(projects, use_container_width=True)
        else:
            st.info("No data")
