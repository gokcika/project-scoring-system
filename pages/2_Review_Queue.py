st.title("Review Queue")

projects = get_pending_projects()

if not projects:
    st.info("No projects pending review")
    st.stop()

# Create dataframe
df = pd.DataFrame(projects)

# Truncate for table
def short_title(text):
    if not text or len(str(text)) <= 60:
        return str(text)
    return str(text)[:60] + "..."

df['title_short'] = df['title'].apply(short_title)

# TABLE - truncated
st.dataframe(
    df[['id', 'title_short', 'requestor_name', 'submission_date', 'total_score', 'priority']],
    column_config={
        "id": "ID",
        "title_short": "Project Title",
        "requestor_name": "Requestor",
        "submission_date": "Submitted",
        "total_score": st.column_config.NumberColumn("Score", format="%.1f"),
        "priority": "Priority"
    },
    hide_index=True,
    use_container_width=True
)

st.divider()

# DETAIL VIEW - full text
st.subheader("Project Details")

selected_id = st.selectbox("Select project", df['id'].tolist())

if selected_id:
    project = get_project_by_id(selected_id)
    
    # FULL TITLE HERE
    st.text_area("Title and Description", project['title'], height=150, disabled=True)
    
    # Your existing tabs...
    tab1, tab2, tab3, tab4 = st.tabs(["Details", "Scoring", "Override", "Decision"])
    # ... rest of code
