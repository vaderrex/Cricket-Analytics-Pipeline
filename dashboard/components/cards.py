import streamlit as st

def render_stat_card(label, value, delta=None):
    """Render a custom CSS stat card.
    
    I'm keeping the HTML structure simple here - just a label, value, 
    and optional delta. The heavy lifting is done by the CSS classes
    defined in style_utils.py.
    """
    delta_html = ''
    if delta:
        delta_html = f'<div style="color: #22C55E; font-size: 0.8rem; font-weight: 600; margin-top: 0.25rem;">+{delta}</div>'
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_match_card(match):
    """Render a custom CSS match score card.
    
    The format badge uses cricket green instead of the old orange.
    Score values are displayed in the primary green to maintain
    visual consistency across the dashboard.
    """
    st.markdown(f"""
    <div class="match-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="match-format">{match['format']}</span>
            <span class="status-live">{match['status']}</span>
        </div>
        <div class="match-teams">{match['teams']}</div>
        <div class="match-score">{match['score']}</div>
        <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">{match['venue']}</div>
    </div>
    """, unsafe_allow_html=True)

def render_hero():
    """Render the main hero banner.
    
    I switched the gradient from the old ESPN blue to a rich 
    cricket green gradient. The CTA button uses stadium yellow 
    (#FFD700) to pop against the green background.
    """
    st.markdown("""
    <div class="hero-banner">
        <h1 style="font-weight: 800; font-size: 2.8rem; margin-bottom: 0; color: #FFFFFF !important; position: relative; z-index: 1;">CRICKET ANALYTICS HUB</h1>
        <p style="font-size: 1.15rem; opacity: 0.92; color: #FFFFFF; position: relative; z-index: 1;">Real-time scores, deep series analytics, and professional player records.</p>
        <div style="margin-top: 1.5rem; position: relative; z-index: 1;">
            <span style="background: #FFD700; color: #374151; padding: 12px 30px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-block; box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3); transition: transform 0.2s ease;">EXPLORE STATS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
