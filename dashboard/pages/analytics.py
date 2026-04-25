import streamlit as st
import pandas as pd
from database.sql_db import SqlDB
from dashboard.data.mock_data import SQL_QUERIES

def show_analytics():
    """Render the SQL analytical engine page."""
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3em;
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #1b5e20;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: translateY(-2px);
        }
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #c8e6c9;
            font-family: 'Courier New', Courier, monospace;
        }
        .css-1r6slb0 {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 SQL Analytics Engine")
    st.markdown("Execute pre-defined or custom queries against the Cricket Data Warehouse.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📚 Query Library")
        category = st.selectbox("Complexity", list(SQL_QUERIES.keys()))
        selected_q = st.selectbox("Selection", [q['title'] for q in SQL_QUERIES[category]])
        
        query_text = next(q['query'] for q in SQL_QUERIES[category] if q['title'] == selected_q)
        st.code(query_text, language="sql")
        
    with col2:
        st.subheader("⚙️ Custom Query Runner")
        sql_input = st.text_area("Write your T-SQL here:", value=query_text, height=150)
        
        if st.button("🚀 Run Analysis"):
            with st.spinner("Querying SQL Server..."):
                db = SqlDB()
                results = db.run_query(sql_input)
                
                if not results.empty:
                    st.write(f"**Results ({len(results)} rows):**")
                    st.dataframe(results, use_container_width=True)
                    st.success("Query executed successfully!")
                else:
                    st.warning("No data found for this query. Check if the tables are populated.")
                
    st.divider()
    st.markdown("### 🧬 Data Lineage & Pipeline Flow")
    
    import os
    asset_path = os.path.join(os.getcwd(), "dashboard", "assets", "lineage.png")
    if os.path.exists(asset_path):
        st.image(asset_path, use_container_width=True)
    else:
        st.info("Lineage diagram is being generated...")
        
    st.info("The data flows from CricBuzz API -> SQL Warehouse -> Analytical Views (stats/scores) -> This Dashboard.")
