import streamlit as st
import pandas as pd
from database.sql_db import SqlDB

def show_crud():
    """Render the admin CRUD interface for player management."""
    st.title("⚙️ Admin - Player Management")
    st.markdown("Direct interface for the `dim_players` table.")
    
    db = SqlDB()
    # Initialize DB schema if needed
    db.init_db()
    
    tab1, tab2, tab3 = st.tabs(["📝 Add/Update Player", "🔍 View All", "🗑 Delete Record"])
    
    with tab1:
        st.subheader("Create or Edit")
        with st.form("player_form", clear_on_submit=True):
            p_id = st.number_input("Player ID", min_value=1, step=1)
            name = st.text_input("Name")
            country = st.text_input("Country")
            role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Keeper"])
            
            submitted = st.form_submit_button("💾 Save to SQL Server")
            if submitted:
                with db:
                    cur = db.conn.cursor()
                    merge_sql = """
                        MERGE INTO dim_players AS t
                        USING (SELECT ? as id, ? as n, ? as c, ? as r) AS s
                        ON t.id = s.id
                        WHEN MATCHED THEN
                            UPDATE SET name = s.n, country = s.c, role = s.r, updated_at = GETDATE()
                        WHEN NOT MATCHED THEN
                            INSERT (id, name, country, role) VALUES (s.id, s.n, s.c, s.r);
                    """
                    cur.execute(merge_sql, (p_id, name, country, role))
                st.success(f"Player {name} saved to SQL Server.")
                
    with tab2:
        st.subheader("Player Directory")
        player_df = db.run_query("SELECT * FROM dim_players")
        if not player_df.empty:
            st.dataframe(player_df, use_container_width=True)
        else:
            st.info("No players found in database.")
        
    with tab3:
        st.subheader("Remove Entry")
        player_df_list = db.run_query("SELECT id, name FROM dim_players")
        if not player_df_list.empty:
            id_to_del = st.selectbox("Select Player to Delete", 
                                     options=player_df_list['id'].tolist(),
                                     format_func=lambda x: f"ID {x}: {player_df_list[player_df_list['id']==x]['name'].values[0]}")
            
            if st.button("❌ Confirm Delete", type="primary"):
                with db:
                    cur = db.conn.cursor()
                    cur.execute("DELETE FROM dim_players WHERE id = ?", (id_to_del,))
                st.warning(f"Record {id_to_del} removed.")
                st.rerun()
        else:
            st.info("No players available to delete.")
