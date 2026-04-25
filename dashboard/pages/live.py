import streamlit as st
import logging
from dashboard.components.cards import render_match_card
from api.cric_api import CricApi
from dashboard.data.mock_data import LIVE_MATCHES

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)
def fetch_live_matches():
    """Cache API calls for 5 minutes to avoid hitting limits."""
    api = CricApi()
    try:
        live_data = api.get_live_matches()
        if live_data:
            logger.info(f"Successfully fetched {len(live_data)} live matches from API")
            return live_data
        else:
            logger.warning("API returned empty data, using mock data")
            return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        st.warning(f"⚠️ Could not fetch live data from API: {str(e)}")
        return None

def show_live():
    """Render the live matches dashboard."""
    st.title("🔴 Live Cricket Scoreboards")
    st.markdown("Real-time data synchronization with Cricbuzz API")
    
    raw_matches = fetch_live_matches()
    
    # Use mock data if API fails
    if raw_matches is None or len(raw_matches) == 0:
        st.info("📊 Using sample data - API unavailable. Please verify your API credentials in .env file")
        formatted_matches = LIVE_MATCHES
    else:
        # Transform raw API data to component format
        formatted_matches = []
        for m in raw_matches:
            info = m.get("matchInfo", {})
            score = m.get("matchScore", {})
            
            # Build score string
            t1 = info.get("team1", {}).get("teamName", "Team 1")
            t2 = info.get("team2", {}).get("teamName", "Team 2")
            
            s1 = score.get("team1Score", {}).get("inngs1", {})
            s2 = score.get("team2Score", {}).get("inngs1", {})
            
            score_str = f"{t1}: {s1.get('runs', 0)}/{s1.get('wickets', 0)} ({s1.get('overs', 0)} ov)"
            if s2:
                 score_str += f" | {t2}: {s2.get('runs', 0)}/{s2.get('wickets', 0)} ({s2.get('overs', 0)} ov)"

            formatted_matches.append({
                "teams": f"{t1} vs {t2}",
                "format": info.get("matchFormat", "N/A").upper(),
                "score": score_str,
                "status": info.get("status", "Unknown"),
                "venue": info.get("venue", {}).get("name", "Unknown Venue")
            })

    # Filter bar
    formats = st.multiselect("Filter by Format:", ["TEST", "ODI", "T20"], default=["TEST", "ODI", "T20"])
    
    st.divider()
    
    if not formatted_matches:
        st.info("No live matches found at the moment.")
        return

    # 2-column layout
    col1, col2 = st.columns(2)
    
    display_index = 0
    for match in formatted_matches:
        if match['format'] in formats or not formats:
            target_col = col1 if display_index % 2 == 0 else col2
            with target_col:
                render_match_card(match)
            display_index += 1
                
    if st.button("🔄 Force Refresh API Data"):
        st.cache_data.clear()
        st.rerun()
