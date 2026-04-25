import streamlit as st
import sys
import os

# fix path for imports
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.append(root)

from dashboard.utils.style_utils import inject_custom_css
from dashboard.components.navbar import render_navbar
from dashboard.pages import home, live, series, records, analytics, crud

# basic tital header config
st.set_page_config(page_title="CricHub", page_icon="🏏", layout="wide")

def main():
    # session state for navigation
    if "p" not in st.session_state:
        st.session_state.p = "Home"

    inject_custom_css()
    render_navbar()

    # route to page
    s = st.session_state.p
    
    if s == "Home": home.show_home()
    elif s == "Live Matches": live.show_live()
    elif s == "Series Docs": series.show_series()
    elif s == "Player Records": records.show_records()
    elif s == "SQL Analytics": analytics.show_analytics()
    elif s == "Admin": crud.show_crud()

    # sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.caption("v2.0-deadlined")

if __name__ == "__main__":
    main()
