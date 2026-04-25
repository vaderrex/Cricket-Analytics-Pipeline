import streamlit as st
from dashboard.components.cards import render_hero, render_stat_card
from dashboard.data.mock_data import LIVE_MATCHES, RECORDS

def show_home():
    """Render the main home page."""
    render_hero()
    
    # KPI Stats
    st.subheader("📊 Global Cricket Snapshot")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: render_stat_card("Total Runs (2024)", "1.2M", "12%")
    with kpi2: render_stat_card("Active Matches", "4", "2")
    with kpi3: render_stat_card("Countries", "104", "0")
    with kpi4: render_stat_card("Top Ranked", "IND", "TEST")
    
    # Overview
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Legendary Batting Records")
        st.dataframe(RECORDS["Most Runs"], height=300, use_container_width=True)
        
    with col2:
        st.subheader("💡 Project Insight")
        st.info("""
        This platform integrates **Cricbuzz RapidAPI** with a robust **MongoDB + SQL Server** architecture. 
        It supports full ETL cycles from raw JSON payloads to structured analytics.
        """)
        st.success("**Upcoming:** ICC Champions Trophy Live Tracker!")
