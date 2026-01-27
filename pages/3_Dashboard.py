import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import Database

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.title("📊 Analytics Dashboard")

# Get statistics
stats = st.session_state.db.get_statistics()
projects = st.session_state.db.get_projects()

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", stats['total'])

with col2:
    pending = stats['by_status'][stats['by_status']['status'] == 'Submitted']['count'].sum() if 'Submitted' in stats['by_status']['status'].values else 0
    st.metric("Pending Review", pending)

with col3:
    if stats['total'] > 0 and len(projects) > 0:
        avg_score = projects['total_score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")
    else:
        st.metric("Avg Score", "N/A")

with col4:
    immediate = stats['by_priority'][stats['by_priority']['priority'] == '🔴 IMMEDIATE']['count'].sum() if not stats['by_priority'].empty and '🔴 IMMEDIATE' in stats['by_priority']['priority'].values else 0
    st.metric("High Priority", immediate)

st.markdown("---")

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Projects by Status")
    if not stats['by_status'].empty:
        fig = px.pie(stats['by_status'], values='count', names='status', 
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

with col2:
    st.markdown("### Projects by Priority")
    if not stats['by_priority'].empty:
        colors = {'🔴 IMMEDIATE': '#FF4B4B', '🟡 PLANNED': '#FFA500', '⚪ DEFER': '#D3D3D3'}
        fig = px.bar(stats['by_priority'], x='priority', y='count',
                     color='priority', color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

st.markdown("---")

# Charts row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Average Score by Department")
    if not stats['avg_by_dept'].empty:
        fig = px.bar(stats['avg_by_dept'], x='department', y='avg_score',
                     text='count', labels={'avg_score': 'Avg Score', 'count': 'Projects'})
        fig.update_traces(texttemplate='%{text} projects', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

with col2:
    st.markdown("### Score Distribution")
    if len(projects) > 0:
        fig = px.histogram(projects, x='total_score', nbins=20,
                          labels={'total_score': 'Score'})
        fig.add_vline(x=70, line_dash="dash", line_color="red", 
                     annotation_text="Immediate Threshold")
        fig.add_vline(x=50, line_dash="dash", line_color="orange",
                     annotation_text="Planned Threshold")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

st.markdown("---")

# Recent high priority table
st.markdown("### 🔴 High Priority Projects")
if not stats['high_priority'].empty:
    st.dataframe(stats['high_priority'], use_container_width=True, hide_index=True)
else:
    st.info("No high priority projects currently")

# Timeline view
st.markdown("---")
st.markdown("### 📅 Submission Timeline")
if len(projects) > 0:
    projects['submission_date'] = pd.to_datetime(projects['submission_date'])
    timeline_data = projects.groupby(projects['submission_date'].dt.date).size().reset_index()
    timeline_data.columns = ['date', 'count']
    
    fig = px.line(timeline_data, x='date', y='count', markers=True,
                  labels={'count': 'Projects Submitted', 'date': 'Date'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No projects submitted yet")

# Export data
st.markdown("---")
st.markdown("### 📥 Export Data")

if len(projects) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        csv = projects.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"project_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel download would require openpyxl, keeping it simple for now
        st.info("Excel export: Add openpyxl to requirements.txt")
