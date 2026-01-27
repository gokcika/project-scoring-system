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

# Filter out deleted projects
if 'deleted' in projects.columns:
    projects = projects[projects['deleted'] == 0]

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", len(projects))

with col2:
    if 'deleted' in stats['by_status'].columns:
        pending = stats['by_status'][
            (stats['by_status']['status'] == 'Submitted') & 
            (stats['by_status'].get('deleted', 0) == 0)
        ]['count'].sum() if 'Submitted' in stats['by_status']['status'].values else 0
    else:
        pending = stats['by_status'][stats['by_status']['status'] == 'Submitted']['count'].sum() if 'Submitted' in stats['by_status']['status'].values else 0
    st.metric("Pending Review", pending)

with col3:
    if len(projects) > 0:
        avg_score = projects['total_score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")
    else:
        st.metric("Avg Score", "N/A")

with col4:
    if not stats['by_priority'].empty and '🔴 IMMEDIATE' in stats['by_priority']['priority'].values:
        immediate = stats['by_priority'][stats['by_priority']['priority'] == '🔴 IMMEDIATE']['count'].sum()
    else:
        immediate = 0
    st.metric("High Priority", immediate)

st.markdown("---")

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Projects by Status")
    if not stats['by_status'].empty:
        # Filter out deleted from chart
        status_data = stats['by_status']
        if 'deleted' in status_data.columns:
            status_data = status_data[status_data['deleted'] == 0]
        
        fig = px.pie(
            status_data, 
            values='count', 
            names='status',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

with col2:
    st.markdown("### Projects by Priority")
    if not stats['by_priority'].empty:
        colors = {
            '🔴 IMMEDIATE': '#FF4B4B', 
            '🟡 PLANNED': '#FFA500', 
            '⚪ DEFER': '#D3D3D3'
        }
        fig = px.bar(
            stats['by_priority'], 
            x='priority', 
            y='count',
            color='priority', 
            color_discrete_map=colors,
            text='count'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

st.markdown("---")

# Charts row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Average Score by Department")
    if not stats['avg_by_dept'].empty:
        fig = px.bar(
            stats['avg_by_dept'], 
            x='department', 
            y='avg_score',
            text='count',
            color='avg_score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        fig.update_traces(
            texttemplate='%{text} projects', 
            textposition='outside'
        )
        fig.update_layout(
            xaxis_title="Department", 
            yaxis_title="Average Score",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

with col2:
    st.markdown("### Score Distribution")
    if len(projects) > 0:
        fig = px.histogram(
            projects, 
            x='total_score', 
            nbins=20,
            labels={'total_score': 'Score'},
            color_discrete_sequence=['#636EFA']
        )
        # Add threshold lines
        fig.add_vline(
            x=70, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Immediate (70)",
            annotation_position="top"
        )
        fig.add_vline(
            x=50, 
            line_dash="dash", 
            line_color="orange",
            annotation_text="Planned (50)",
            annotation_position="top"
        )
        fig.update_layout(
            xaxis_title="Score", 
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")

st.markdown("---")

# Recent high priority table
st.markdown("### 🔴 High Priority Projects")
if not stats['high_priority'].empty:
    # Format the dataframe
    high_priority_display = stats['high_priority'].copy()
    high_priority_display['total_score'] = high_priority_display['total_score'].round(1)
    
    st.dataframe(
        high_priority_display[['project_title', 'requestor_name', 'department', 'total_score', 'submission_date']], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "project_title": "Project Title",
            "requestor_name": "Requestor",
            "department": "Department",
            "total_score": st.column_config.NumberColumn("Score", format="%.1f"),
            "submission_date": st.column_config.DatetimeColumn("Submitted", format="DD/MM/YYYY")
        }
    )
else:
    st.info("No high priority projects currently")

# Timeline view
st.markdown("---")
st.markdown("### 📅 Submission Timeline")
if len(projects) > 0 and 'submission_date' in projects.columns:
    try:
        projects_timeline = projects.copy()
        projects_timeline['submission_date'] = pd.to_datetime(projects_timeline['submission_date'])
        timeline_data = projects_timeline.groupby(
            projects_timeline['submission_date'].dt.date
        ).size().reset_index()
        timeline_data.columns = ['date', 'count']
        
        fig = px.line(
            timeline_data, 
            x='date', 
            y='count', 
            markers=True,
            labels={'count': 'Projects Submitted', 'date': 'Date'}
        )
        fig.update_traces(
            line_color='#636EFA',
            marker=dict(size=8)
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Projects",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Unable to generate timeline: {str(e)}")
else:
    st.info("No projects submitted yet")

# Export data
st.markdown("---")
st.markdown("### 📥 Export Data")

if len(projects) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv = projects.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"project_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel Export with openpyxl
        try:
            from io import BytesIO
            from openpyxl.styles import Font, PatternFill, Alignment
            
            excel_buffer = BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Sheet 1: All Projects
                projects.to_excel(writer, index=False, sheet_name='All Projects')
                
                # Sheet 2: Summary Statistics
                summary_data = {
                    'Metric': [
                        'Total Projects',
                        'Submitted',
                        'Under Review',
                        'Approved',
                        'Rejected',
                        'High Priority (Immediate)',
                        'Medium Priority (Planned)',
                        'Low Priority (Defer)',
                        'Average Score'
                    ],
                    'Count': [
                        len(projects),
                        len(projects[projects['status'] == 'Submitted']) if 'Submitted' in projects['status'].values else 0,
                        len(projects[projects['status'] == 'Under Review']) if 'Under Review' in projects['status'].values else 0,
                        len(projects[projects['status'] == 'Approved']) if 'Approved' in projects['status'].values else 0,
                        len(projects[projects['status'] == 'Rejected']) if 'Rejected' in projects['status'].values else 0,
                        len(projects[projects['priority'] == '🔴 IMMEDIATE']) if '🔴 IMMEDIATE' in projects['priority'].values else 0,
                        len(projects[projects['priority'] == '🟡 PLANNED']) if '🟡 PLANNED' in projects['priority'].values else 0,
                        len(projects[projects['priority'] == '⚪ DEFER']) if '⚪ DEFER' in projects['priority'].values else 0,
                        f"{projects['total_score'].mean():.1f}" if len(projects) > 0 else "N/A"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
                
                # Format All Projects sheet
                workbook = writer.book
                worksheet = writer.sheets['All Projects']
                
                # Header formatting
                header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add filters
                worksheet.auto_filter.ref = worksheet.dimensions
                
                # Format Summary sheet
                summary_sheet = writer.sheets['Summary']
                for cell in summary_sheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                for column in summary_sheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 30)
                    summary_sheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_data,
                file_name=f"project_data_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.info("Excel export requires openpyxl. Add to requirements.txt: openpyxl==3.1.2")
        except Exception as e:
            st.error(f"Excel export error: {str(e)}")
else:
    st.info("No data available to export")

# Additional insights
if len(projects) > 0:
    st.markdown("---")
    st.markdown("### 📈 Additional Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Approval rate
        if 'Approved' in projects['status'].values:
            approved_count = len(projects[projects['status'] == 'Approved'])
            total_reviewed = len(projects[projects['status'].isin(['Approved', 'Rejected'])])
            if total_reviewed > 0:
                approval_rate = (approved_count / total_reviewed) * 100
                st.metric("Approval Rate", f"{approval_rate:.1f}%")
            else:
                st.metric("Approval Rate", "N/A")
        else:
            st.metric("Approval Rate", "N/A")
    
    with col2:
        # Average review time (if you have reviewed_date)
        st.metric("Avg Review Time", "Coming Soon")
    
    with col3:
        # Top requesting department
        if not projects.empty:
            top_dept = projects['department'].mode()[0] if len(projects['department'].mode()) > 0 else "N/A"
            dept_count = len(projects[projects['department'] == top_dept])
            st.metric("Top Department", f"{top_dept} ({dept_count})")
        else:
            st.metric("Top Department", "N/A")
