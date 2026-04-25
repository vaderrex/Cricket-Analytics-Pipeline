import streamlit as st
from database.sql_db import SqlDB

def fetch_records(category):
    """Fetch aggregated records from the SQL database."""
    db = SqlDB()
    if category == "Most Runs":
        query = "SELECT name as Player, SUM(runs) as Runs, AVG(sr) as [Avg SR] FROM batting_stats GROUP BY name ORDER BY Runs DESC"
    elif category == "Most Wickets":
        # Note: Current schema focuses on batting, but I'll add a placeholder or filter
        query = "SELECT name as Player, COUNT(*) as Innings, SUM(runs) as [Runs Allowed] FROM batting_stats GROUP BY name" # Placeholder
    else: # Highest Score
        query = "SELECT TOP 10 name as Player, runs as Score, dismissal as Against FROM batting_stats ORDER BY runs DESC"
    
    return db.run_query(query)

def show_records():
    """Render the all-time cricket records page."""
    st.title("🏆 All-Time Cricket Records")
    st.markdown("Aggregated historical data across all formats.")
    
    format_tab = st.selectbox("Select Format:", ["All Formats", "Test", "ODI", "T20I"])
    
    tab1, tab2, tab3 = st.tabs(["Most Runs", "Most Wickets", "Highest Scores"])
    
    with tab1:
        st.subheader("🏏 Batting Legends")
        df_runs = fetch_records("Most Runs")
        if not df_runs.empty:
            st.dataframe(df_runs, use_container_width=True)
        else:
            st.info("No run records found in database.")
        
    with tab2:
        st.subheader("🥎 Bowling Masters")
        df_wickets = fetch_records("Most Wickets")
        if not df_wickets.empty:
            st.dataframe(df_wickets, use_container_width=True)
        else:
            st.info("No wicket records found in database.")
        
    with tab3:
        st.subheader("🔥 Record Individual Innings")
        df_scores = fetch_records("Highest Score")
        if not df_scores.empty:
            st.dataframe(df_scores, use_container_width=True)
        else:
            st.info("No high score records found in database.")
