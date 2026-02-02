import streamlit as st
import pandas as pd
from utils.database import *

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login first")
    st.stop()

if st.session_state.get('role') not in ['compliance', 'admin']:
    st.error("Access denied. Compliance Officer access required.")
    st.stop()

st.title("Review Queue")

conn = get_db_connection()
c = conn.cursor()
c.execute("SELECT * FROM projects WHERE status = 'Pending Review' AND deleted = 0 ORDER BY submission_date DESC")
projects = [dict(row) for row in c.fetchall()]
conn.close()

if not projects:
    st.info("No projects pending review")
    st.stop()

st.write(f"**{len(projects)} projects** awaiting review")
st.divider()

for project in projects:
    priority_colors = {
        "IMMEDIATE": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢"
    }
    priority_icon = priority_colors.get(project.get('priority', 'MEDIUM'), "⚪")
    
    title_display = project['title'][:80] + '...' if len(project['title']) > 80 else project['title']
    
    with st.expander(f"{priority_icon} **#{project['id']}** - {title_display}"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.caption(f"**Requestor:** {project['requestor_name']} | **Department:** {project['department']}")
            st.caption(f"**Submitted:** {project['submission_date']}")
        
        with col2:
            st.metric("Score", f"{project.get('total_score', 0):.1f}")
        
        with col3:
            st.metric("Priority", project.get('priority', 'N/A'))
        
        st.divider()
        
        st.text_area("Full Title and Description", value=project['title'], height=120, disabled=True, key=f"full_title_{project['id']}")
        
        st.divider()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Details", "📊 Scoring", "✏️ Override", "✅ Decision"])
        
        with tab1:
            st.markdown("#### Full Project Information")
            
            with st.expander("**1. Regulatory & Compliance**", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Has Requirement:** {project.get('reg_has_requirement', 'N/A')}")
                    st.write(f"**Due Date:** {project.get('reg_due_date', 'N/A')}")
                with col2:
                    st.write(f"**Sanctions:** {project.get('reg_has_sanctions', 'N/A')}")
                    st.write(f"**Score:** {project.get('reg_score', 0):.1f}/5.0")
                
                if project.get('reg_citation'):
                    st.text_area("Citation", value=project['reg_citation'], height=80, disabled=True, key=f"cit_{project['id']}")
            
            with st.expander("**2. Reputational Risk**"):
                st.write(f"**Risk Level:** {project.get('rep_risk_level', 'N/A')}")
                st.write(f"**Liability:** {project.get('rep_liability', 'N/A')}")
                st.write(f"**Score:** {project.get('rep_score', 0):.1f}/5.0")
                
                if project.get('rep_headline'):
                    st.text_area("Risk Description", value=project['rep_headline'], height=80, disabled=True, key=f"risk_{project['id']}")
            
            with st.expander("**3. Strategic Alignment**"):
                st.write(f"**Documentation:** {project.get('strat_documentation', 'N/A')}")
                st.write(f"**Sponsor Confirmed:** {project.get('strat_sponsor_confirmed', 'N/A')}")
                st.write(f"**Budget Allocated:** {project.get('strat_budget_allocated', 'N/A')}")
                st.write(f"**Score:** {project.get('strat_score', 0):.1f}/5.0")
            
            with st.expander("**4. Operational Impact**"):
                st.write(f"**Current Time:** {project.get('op_current_time', 'N/A')} hours")
                st.write(f"**Projected Time:** {project.get('op_projected_time', 'N/A')} hours")
                st.write(f"**Affected Groups:** {project.get('op_affected_groups', 'N/A')}")
                st.write(f"**Blocking:** {project.get('op_is_blocking', 'N/A')}")
                st.write(f"**Score:** {project.get('op_score', 0):.1f}/5.0")
            
            with st.expander("**5. Resources**"):
                st.write(f"**Approach:** {project.get('res_implementation_approach', 'N/A')}")
                st.write(f"**External Dependencies:** {project.get('res_external_deps', 'Not assessed')}")
                st.write(f"**Score:** {project.get('res_score', 0):.1f}/5.0")
            
            with st.expander("**6. Data & Privacy**"):
                st.write(f"**Sensitivity:** {project.get('data_sensitivity', 'N/A')}")
                st.write(f"**Third-party Access:** {project.get('data_third_party_access', 'N/A')}")
                st.write(f"**Score:** {project.get('data_score', 0):.1f}/5.0")
            
            with st.expander("**7. Stakeholder Urgency**"):
                st.write(f"**Champion:** {project.get('stake_champion_level', 'N/A')}")
                st.write(f"**Score:** {project.get('stake_score', 0):.1f}/5.0")
                
                if project.get('stake_urgency_description'):
                    st.text_area("Urgency Details", value=project['stake_urgency_description'], height=80, disabled=True, key=f"urg_{project['id']}")
        
        with tab2:
            st.markdown("#### Score Breakdown")
            
            scores = {
                "Regulatory": (project.get('reg_score', 0), 0.25),
                "Reputational": (project.get('rep_score', 0), 0.20),
                "Strategic": (project.get('strat_score', 0), 0.15),
                "Operational": (project.get('op_score', 0), 0.15),
                "Resources": (project.get('res_score', 0), 0.10),
                "Data": (project.get('data_score', 0), 0.10),
                "Stakeholder": (project.get('stake_score', 0), 0.05)
            }
            
            for criterion, (score, weight) in scores.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{criterion}**")
                with col2:
                    st.write(f"{score:.1f}/5.0")
                with col3:
                    st.write(f"Weight: {weight*100:.0f}%")
                st.progress(score / 5.0)
            
            st.divider()
            st.metric("Total Score", f"{project.get('total_score', 0):.1f}/100")
        
        with tab3:
            st.markdown("#### Manual Score Override")
            st.info("Override functionality - existing code from your original file")
        
        with tab4:
            st.markdown("#### Review Decision")
            
            notes = st.text_area("Review Notes", key=f"notes_{project['id']}", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve", key=f"approve_{project['id']}", use_container_width=True):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("UPDATE projects SET status = 'Approved', co_decision = 'Approved', co_notes = ?, co_reviewed_by = ?, co_reviewed_date = datetime('now') WHERE id = ?", 
                             (notes, st.session_state.username, project['id']))
                    conn.commit()
                    conn.close()
                    st.success(f"Project #{project['id']} approved")
                    st.rerun()
            
            with col2:
                if st.button("❌ Reject", key=f"reject_{project['id']}", use_container_width=True):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("UPDATE projects SET status = 'Rejected', co_decision = 'Rejected', co_notes = ?, co_reviewed_by = ?, co_reviewed_date = datetime('now') WHERE id = ?", 
                             (notes, st.session_state.username, project['id']))
                    conn.commit()
                    conn.close()
                    st.error(f"Project #{project['id']} rejected")
                    st.rerun()
