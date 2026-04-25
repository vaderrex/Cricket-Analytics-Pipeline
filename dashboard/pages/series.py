import streamlit as st
from dashboard.data.mock_data import SERIES_LIST
from database.sql_db import SqlDB

def show_series():
    """Render the series and tournaments page."""
    st.title("📅 Series & Tournaments")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.subheader("Select Series")
        selected_series = st.radio("Active Series", [s['name'] for s in SERIES_LIST])
        
    with col2:
        st.subheader("Tournament Details")
        series_info = next(s for s in SERIES_LIST if s['name'] == selected_series)
        st.markdown(f"### {series_info['name']}")
        st.write(f"**Teams:** {series_info['teams']}")
        st.write(f"**Format:** {series_info['format']}")
        st.write(f"**Matches Scheduled:** {series_info['matches']}")
        
        st.info("Match schedules are managed via the MongoDB `matches_raw` collection.")
        
    with col3:
        st.subheader("Top Performers")
        db = SqlDB()
        top_perf = db.run_query("SELECT TOP 5 name, SUM(runs) as total_runs FROM batting_stats GROUP BY name ORDER BY total_runs DESC")
        if not top_perf.empty:
            st.dataframe(top_perf, use_container_width=True)
        else:
            st.info("No stats available yet.")
