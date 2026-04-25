import streamlit as st

def inject_custom_css():
    """Inject cricket-themed professional CSS into the Streamlit app.
    
    I'm using a cricket-field-inspired palette here:
    - Dark green (#0B6623) for the sidebar, like the outfield
    - Primary green (#1F7A3A) for KPI values and accents
    - Stadium yellow (#FFD700) for highlights and bar charts
    - Light gray (#F5F7FA) background to keep things bright and readable
    
    All selectors use Streamlit's data-testid attributes where possible
    so they survive Streamlit version updates better than class-based ones.
    """
    st.markdown("""
    <style>
    /* ===================================================
       FONTS & GLOBAL RESET
       I'm pulling Inter from Google Fonts for that clean,
       modern dashboard look. Falls back to system sans-serif.
    =================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ===================================================
       MAIN BACKGROUND
       Light gray to mimic daylight cricket field conditions.
       Clean and bright, easy on the eyes for long sessions.
    =================================================== */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F5F7FA;
    }
    .main .block-container {
        background-color: #F5F7FA;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ===================================================
       HIDE DEFAULT STREAMLIT PAGE NAVIGATION
       Streamlit auto-generates page links from the pages/ directory.
       I'm hiding them since we use our own custom sidebar buttons.
    =================================================== */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    section[data-testid="stSidebar"] > div > div > div > ul {
        display: none !important;
    }

    /* ===================================================
       SIDEBAR
       Rich cricket field green (#0B6623) as the base.
       I want this to feel like you're looking at the pitch
       from the pavilion end - authoritative and grounded.
    =================================================== */
    [data-testid="stSidebar"] {
        background-color: #0B6623;
        color: #FFFFFF;
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Sidebar headings should pop against the dark green */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15);
    }
    /* Sidebar caption at the bottom */
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {
        color: rgba(255, 255, 255, 0.7) !important;
    }

    /* Sidebar navigation buttons - these are the menu items */
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        font-weight: 500;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: 4px;
    }
    /* Hover state - lighter green like sunlight hitting the grass */
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2E8B57 !important;
        border-color: #2E8B57 !important;
        transform: translateX(3px);
    }
    /* Active/focused state - the selected menu item */
    [data-testid="stSidebar"] button[kind="secondary"]:focus,
    [data-testid="stSidebar"] .stButton > button:focus,
    [data-testid="stSidebar"] button[kind="secondary"]:active,
    [data-testid="stSidebar"] .stButton > button:active {
        background-color: #1F7A3A !important;
        border-color: #1F7A3A !important;
        border-radius: 8px;
        box-shadow: 0 0 0 2px rgba(31, 122, 58, 0.3);
    }
    /* Sidebar info box needs special treatment */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }

    /* ===================================================
       KPI STAT CARDS
       White background with soft elevation shadow.
       The left border is cricket green to tie it to our theme.
       I want these to feel like scoreboard panels.
    =================================================== */
    .stat-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E7EB;
        border-left: 4px solid #1F7A3A;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    .stat-label {
        font-size: 0.75rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1F7A3A;
        line-height: 1.2;
    }
    /* Delta indicator below the value */
    .stat-card div[style*="color: #28a745"],
    .stat-card div[style*="color: #22C55E"] {
        color: #22C55E !important;
        font-weight: 600;
    }

    /* ===================================================
       MATCH CARDS
       These simulate the live scoreboard feel. White base
       with a subtle gradient, and hover lift effect to
       make them feel interactive.
    =================================================== */
    .match-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .match-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    .match-format {
        background-color: #1F7A3A;
        color: #FFFFFF;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .match-teams {
        font-size: 1.1rem;
        font-weight: 700;
        color: #374151;
        margin-top: 0.5rem;
    }
    .match-score {
        color: #1F7A3A;
        font-weight: 800;
        font-size: 1.3rem;
    }
    /* Live status indicator with blinking dot */
    .status-live {
        color: #EF4444;
        font-weight: 600;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
    }
    .status-live::before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #EF4444;
        border-radius: 50%;
        margin-right: 6px;
        animation: blink 1s infinite;
    }

    /* ===================================================
       HERO BANNER
       I'm using the cricket green as an overlay instead
       of the old ESPN blue. This anchors the whole page
       to the cricket theme immediately.
    =================================================== */
    .hero-banner {
        background: linear-gradient(135deg, #0B6623 0%, #1F7A3A 50%, #2E8B57 100%);
        background-size: cover;
        background-position: center;
        padding: 3.5rem 2rem;
        color: #FFFFFF;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(11, 102, 35, 0.25);
        position: relative;
        overflow: hidden;
    }
    /* Subtle texture overlay for depth */
    .hero-banner::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 80%, rgba(255,215,0,0.08) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.05) 0%, transparent 50%);
        pointer-events: none;
    }

    /* ===================================================
       PRIMARY BUTTONS (main content area)
       Cricket green with smooth hover transition.
       I want these to feel confident and decisive.
    =================================================== */
    .stButton > button,
    button[kind="primary"] {
        background-color: #1F7A3A;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(31, 122, 58, 0.2);
    }
    .stButton > button:hover,
    button[kind="primary"]:hover {
        background-color: #166534 !important;
        box-shadow: 0 4px 12px rgba(22, 101, 52, 0.3);
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 1px 3px rgba(31, 122, 58, 0.2);
    }
    /* Secondary button style - for less important actions */
    button[kind="secondary"] {
        background-color: transparent;
        color: #1F7A3A !important;
        border: 1.5px solid #1F7A3A;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(31, 122, 58, 0.08) !important;
        border-color: #166534;
    }

    /* ===================================================
       DATAFRAMES & TABLES
       Clean white containers with rounded corners.
       Light borders to separate rows without being heavy.
    =================================================== */
    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    div[data-testid="stDataFrame"] table {
        border-collapse: collapse;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #F9FAFB !important;
        color: #374151 !important;
        font-weight: 700;
        border-bottom: 2px solid #E5E7EB !important;
    }
    div[data-testid="stDataFrame"] td {
        color: #374151;
        border-bottom: 1px solid #F3F4F6 !important;
    }

    /* ===================================================
       TEXT INPUTS, SELECT BOXES, TEXT AREAS
       Rounded inputs with light gray borders.
       I want a clean, modern form aesthetic.
    =================================================== */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border: 1.5px solid #D1D5DB;
        border-radius: 8px;
        background-color: #FFFFFF;
        color: #374151;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #1F7A3A;
        box-shadow: 0 0 0 3px rgba(31, 122, 58, 0.1);
    }
    /* Selectbox styling */
    div[data-testid="stSelectbox"] > div > div {
        border: 1.5px solid #D1D5DB;
        border-radius: 8px;
        background-color: #FFFFFF;
    }
    div[data-testid="stMultiSelect"] > div > div {
        border: 1.5px solid #D1D5DB;
        border-radius: 8px;
        background-color: #FFFFFF;
    }

    /* ===================================================
       TABS
       Using cricket green for the active tab indicator.
       Inactive tabs get a muted gray treatment.
    =================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #6B7280;
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1F7A3A !important;
        color: #FFFFFF !important;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }

    /* ===================================================
       HEADINGS & TEXT
       Dark green for headings, neutral grays for body.
       This grounds the text hierarchy in the cricket palette.
    =================================================== */
    h1 {
        color: #0B6623 !important;
        font-weight: 800;
    }
    h2, h3 {
        color: #0B6623 !important;
        font-weight: 700;
    }
    p, span, label, .stMarkdown {
        color: #374151;
    }

    /* ===================================================
       STATUS ALERTS
       Mapping success/warning/error to our cricket palette.
       Green for success, yellow for warning, red for errors.
    =================================================== */
    /* Success alert */
    div[data-testid="stAlert"][data-baseweb*="notification"] {
        border-radius: 8px;
    }
    .stSuccess, [data-testid="stAlert"]:has(.st-emotion-cache-success) {
        background-color: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 8px;
        color: #166534;
    }
    .stWarning {
        background-color: rgba(255, 215, 0, 0.08);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 8px;
        color: #92400E;
    }
    .stError {
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 8px;
        color: #991B1B;
    }
    .stInfo {
        background-color: rgba(0, 174, 239, 0.06);
        border: 1px solid rgba(0, 174, 239, 0.2);
        border-radius: 8px;
        color: #0369A1;
    }

    /* ===================================================
       METRICS (st.metric)
       Streamlit's built-in metric component styling.
       Values in cricket green, labels in muted gray.
    =================================================== */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #6B7280 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #1F7A3A !important;
        font-weight: 800;
    }
    [data-testid="stMetricDelta"] svg {
        fill: #22C55E;
    }

    /* ===================================================
       PROGRESS BARS
       Cricket green fill on a light gray track.
       Used in system health and loading indicators.
    =================================================== */
    .stProgress > div > div {
        background-color: #E5E7EB;
        border-radius: 8px;
    }
    .stProgress > div > div > div {
        background-color: #1F7A3A;
        border-radius: 8px;
    }

    /* ===================================================
       CHARTS CONTAINER
       I want charts to sit inside clean white containers
       so they stand out against the gray background.
    =================================================== */
    [data-testid="stVegaLiteChart"],
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* ===================================================
       CODE BLOCKS
       Clean styling for SQL and code display areas.
    =================================================== */
    .stCodeBlock, pre {
        border-radius: 8px !important;
        border: 1px solid #E5E7EB;
    }

    /* ===================================================
       FORMS
       White card container for form groups.
       Keeps the form inputs visually grouped.
    =================================================== */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* ===================================================
       PIPELINE SECTION
       A subtle green tint for pipeline-related containers.
       This differentiates system-level info from user data.
    =================================================== */
    .pipeline-card {
        background-color: #E8F5E9;
        border: 1px solid #C8E6C9;
        border-radius: 12px;
        padding: 1.25rem;
        color: #0B6623;
    }
    .pipeline-card * {
        color: #0B6623;
    }

    /* ===================================================
       DIVIDERS
       Subtle light gray to not overpower the layout.
       =================================================== */
    hr, .stDivider {
        border-color: #E5E7EB !important;
    }

    /* ===================================================
       RADIO BUTTONS
       Green accent for selected radio items.
    =================================================== */
    .stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(31, 122, 58, 0.05);
        border-radius: 6px;
    }
    .stRadio [data-testid="stMarkdownContainer"] {
        color: #374151;
    }

    /* ===================================================
       SPINNER
       Green spinner to match the theme during loading.
    =================================================== */
    .stSpinner > div > div {
        border-top-color: #1F7A3A !important;
    }

    /* ===================================================
       EXPANDER
       Clean white expander with cricket-themed header.
    =================================================== */
    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    [data-testid="stExpander"] summary {
        color: #0B6623;
        font-weight: 600;
    }

    /* ===================================================
       SCROLLBAR
       Custom scrollbar to match the theme.
       Subtle but consistent with our green palette.
    =================================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F5F7FA;
    }
    ::-webkit-scrollbar-thumb {
        background: #C8E6C9;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #1F7A3A;
    }

    /* ===================================================
       ANIMATIONS
       Blink animation for live status indicators.
    =================================================== */
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)
