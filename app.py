import streamlit as st
from utils.database import Database
import pandas as pd

# Page config
st.set_page_config(
    page_title="Project Prioritization System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

if not st.session_state.authenticated:
    st.markdown('<p class="big-font">🔐 Login</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("### Digitalization Project Scoring System")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = st.session_state.db.authenticate(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Welcome {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.info("""
        **Demo Credentials:**
        - Requestor: `requestor` / `req123`
        - Compliance Officer: `admin` / `admin123`
        """)

else:
    # Main page after login
    st.markdown(f'<p class="big-font">📊 Project Scoring System</p>', unsafe_allow_html=True)
    
    # User info
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.markdown(f"**User:** {st.session_state.user['username']} ({st.session_state.user['role']})")
    with col3:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    stats = st.session_state.db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", stats['total'])
    
    with col2:
        submitted = stats['by_status'][stats['by_status']['status'] == 'Submitted']['count'].sum() if 'Submitted' in stats['by_status']['status'].values else 0
        st.metric("Pending Review", submitted)
    
    with col3:
        approved = stats['by_status'][stats['by_status']['status'] == 'Approved']['count'].sum() if 'Approved' in stats['by_status']['status'].values else 0
        st.metric("Approved", approved)
    
    with col4:
        immediate = stats['by_priority'][stats['by_priority']['priority'] == '🔴 IMMEDIATE']['count'].sum() if not stats['by_priority'].empty else 0
        st.metric("High Priority", immediate)
    
    st.markdown("---")
    
    # Navigation guide
    st.markdown("### 🧭 Quick Navigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📝 For Requestors:
        - Submit new project request
        - Track your submissions
        - View scoring results
        """)
        
        if st.session_state.user['role'] == 'requestor':
            if st.button("➡️ Submit New Request", key="new_req"):
                st.switch_page("pages/1_📝_New_Request.py")
    
    with col2:
        st.markdown("""
        #### ⚖️ For Compliance Officers:
        - Review pending requests
        - Override scoring
        - Approve/reject projects
        """)
        
        if st.session_state.user['role'] == 'compliance_officer':
            if st.button("➡️ Review Queue", key="review_q"):
                st.switch_page("pages/2_⚖️_Review_Queue.py")
    
    st.markdown("---")
    
    # Recent high-priority projects
    if not stats['high_priority'].empty:
        st.markdown("### 🔴 High Priority Projects Awaiting Review")
        st.dataframe(
            stats['high_priority'][['project_title', 'requestor_name', 'department', 'total_score', 'submission_date']],
            use_container_width=True,
            hide_index=True
        )
    
    # System info
    with st.expander("ℹ️ About This System"):
        st.markdown("""
        **Scoring Criteria & Weights:**
        - 🏛️ Regulatory Risk: 25%
        - 🛡️ Reputational/Ethical Risk: 20%
        - 🎯 Strategic Alignment: 15%
        - ⚙️ Operational Impact: 15%
        - 💰 Resource Requirements: 10%
        - 🔒 Data Sensitivity: 10%
        - 👥 Stakeholder Pressure: 5%
        
        **Priority Thresholds:**
        - 🔴 IMMEDIATE: Score ≥ 70
        - 🟡 PLANNED: Score 50-69
        - ⚪ DEFER: Score < 50
        """)
