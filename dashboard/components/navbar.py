import streamlit as st

def render_navbar():
    """Render a sidebar-based vertical navbar with clean styling.
    
    The title block uses white text against the dark green sidebar.
    I added a subtle gold accent line under the brand name to 
    tie in the cricket yellow highlight without overdoing it.
    """
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem; padding-top: 0.5rem;">
        <h2 style="color: #FFFFFF !important; font-weight: 800; letter-spacing: 3px; margin-bottom: 0.25rem; font-size: 1.6rem;">CRICK HUB</h2>
        <div style="width: 40px; height: 3px; background: #FFD700; margin: 0 auto 0.5rem auto; border-radius: 2px;"></div>
        <p style="color: rgba(255,255,255,0.65) !important; font-size: 0.75rem; letter-spacing: 1px; margin: 0;">Cricket Analytics Platform</p>
        <hr style="border-top: 1px solid rgba(255,255,255,0.12); margin-top: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    pages = {
        "Home": "Home",
        "Live Matches": "Live Matches",
        "Series Docs": "Series Docs",
        "Player Records": "Player Records",
        "SQL Analytics": "SQL Analytics",
        "Admin": "Admin"
    }
    
    # Initialize session state for navigation
    if "p" not in st.session_state:
        st.session_state.p = "Home"
        
    for page_name in pages:
        if st.sidebar.button(f"{page_name}", use_container_width=True):
            st.session_state.p = page_name
            st.rerun()

    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer info styled for the green sidebar
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 0.75rem; background: rgba(255,255,255,0.08); border-radius: 8px; margin: 0 0.5rem;">
        <p style="color: rgba(255,255,255,0.7) !important; font-size: 0.7rem; margin: 0; letter-spacing: 0.5px;">CricHub v2.0 | Production</p>
    </div>
    """, unsafe_allow_html=True)
