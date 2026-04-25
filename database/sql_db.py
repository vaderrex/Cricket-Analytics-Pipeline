import pyodbc
import logging
import pandas as pd
from typing import List, Tuple
from config.config import cfg

logger = logging.getLogger(__name__)

class SqlDB:
    def __init__(self):
        self.c_str = cfg.conn_str
        self.conn = None

    def __enter__(self):
        try:
            self.conn = pyodbc.connect(self.c_str)
            return self
        except pyodbc.Error as e:
            logger.error(f"SQL Connection failure: {e}")
            raise

    def __exit__(self, exc_type, *args):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()

    def init_db(self):
        """Ensures the target database and schema are initialized."""
        try:
            with pyodbc.connect(cfg.master_conn, autocommit=True) as a_conn:
                cur = a_conn.cursor()
                cur.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{cfg.SQL_DB}') CREATE DATABASE [{cfg.SQL_DB}]")
        except pyodbc.Error as e:
            logger.error(f"Failed to ensure database exists: {e}")

        with self:
            cur = self.conn.cursor()

            # Drop FK constraints from ETL tables — the pipeline manages insertion
            # order in code. FK constraints on fact tables cause pipeline failures
            # when data arrives out of order from the API.
            cur.execute("""
                DECLARE @sql NVARCHAR(MAX) = '';
                SELECT @sql += 'ALTER TABLE [' + OBJECT_NAME(parent_object_id) + '] DROP CONSTRAINT [' + name + '];'
                FROM sys.foreign_keys
                WHERE OBJECT_NAME(parent_object_id) IN ('batting_stats', 'bowling_stats', 'fielding_stats', 'matches');
                EXEC sp_executesql @sql;
            """)

            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='etl_log' AND xtype='U')
                CREATE TABLE etl_log (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    b_id UNIQUEIDENTIFIER,
                    ts DATETIME DEFAULT GETDATE(),
                    rows INT,
                    status NVARCHAR(50),
                    msg NVARCHAR(MAX)
                )
            ''')
            # Dimension tables
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='teams' AND xtype='U')
                CREATE TABLE teams (
                    team_id INT PRIMARY KEY, team_name NVARCHAR(100), country NVARCHAR(50)
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='venues' AND xtype='U')
                CREATE TABLE venues (
                    venue_id INT PRIMARY KEY, venue_name NVARCHAR(100),
                    city NVARCHAR(50), country NVARCHAR(50), capacity INT
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='series' AND xtype='U')
                CREATE TABLE series (
                    series_id INT PRIMARY KEY, series_name NVARCHAR(100),
                    host_country NVARCHAR(50), match_type NVARCHAR(20),
                    start_date DATE, total_matches INT
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='matches' AND xtype='U')
                CREATE TABLE matches (
                    match_id VARCHAR(64) PRIMARY KEY,
                    series_id INT, match_description NVARCHAR(200),
                    team1_id INT, team2_id INT, venue_id INT,
                    match_date DATE, format VARCHAR(20),
                    winning_team_id INT, victory_margin INT,
                    victory_type VARCHAR(20), toss_winner_id INT,
                    toss_decision VARCHAR(20)
                )
            ''')
            # Fact tables
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='dim_players' AND xtype='U')
                CREATE TABLE dim_players (
                    id INT PRIMARY KEY, name NVARCHAR(255),
                    country NVARCHAR(100), role NVARCHAR(50),
                    updated_at DATETIME DEFAULT GETDATE()
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='players' AND xtype='U')
                CREATE TABLE players (
                    player_id INT PRIMARY KEY, full_name NVARCHAR(255),
                    country NVARCHAR(100), playing_role NVARCHAR(50),
                    batting_style NVARCHAR(50), bowling_style NVARCHAR(50)
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='batting_stats' AND xtype='U')
                CREATE TABLE batting_stats (
                    match_id VARCHAR(64), player_id INT, innings_id INT,
                    batting_position INT, runs_scored INT, balls_faced INT,
                    fours INT, sixes INT, dismissal_type NVARCHAR(100),
                    PRIMARY KEY (match_id, player_id, innings_id)
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='bowling_stats' AND xtype='U')
                CREATE TABLE bowling_stats (
                    match_id VARCHAR(64), player_id INT,
                    overs_bowled DECIMAL(4,1), maidens INT,
                    runs_conceded INT, wickets_taken INT,
                    PRIMARY KEY (match_id, player_id)
                )
            ''')
            cur.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='fielding_stats' AND xtype='U')
                CREATE TABLE fielding_stats (
                    match_id VARCHAR(64), player_id INT,
                    catches INT DEFAULT 0, stumpings INT DEFAULT 0,
                    PRIMARY KEY (match_id, player_id)
                )
            ''')

            # Analytical Views
            cur.execute('''
                IF EXISTS (SELECT * FROM sys.views WHERE name = 'stats') DROP VIEW stats;
            ''')
            cur.execute('''
                CREATE VIEW stats AS
                SELECT 
                    p.full_name as name,
                    p.country,
                    SUM(bs.runs_scored) as runs,
                    AVG(CAST(bs.runs_scored AS FLOAT)) as avg,
                    COUNT(bs.match_id) as matches_played
                FROM players p
                JOIN batting_stats bs ON p.player_id = bs.player_id
                GROUP BY p.player_id, p.full_name, p.country
            ''')

            cur.execute('''
                IF EXISTS (SELECT * FROM sys.views WHERE name = 'scores') DROP VIEW scores;
            ''')
            cur.execute('''
                CREATE VIEW scores AS
                SELECT 
                    p.full_name as name,
                    m.match_date as date,
                    bs.runs_scored as runs,
                    p.player_id
                FROM players p
                JOIN batting_stats bs ON p.player_id = bs.player_id
                JOIN matches m ON bs.match_id = m.match_id
            ''')

    def upsert_teams(self, teams: List[Tuple]):
        """UPSERT team dimension records. Each tuple: (team_id, team_name, country)"""
        cur = self.conn.cursor()
        for t in teams:
            cur.execute('''
                MERGE INTO teams AS tgt USING (VALUES (?,?,?)) AS src(team_id, team_name, country)
                ON tgt.team_id = src.team_id
                WHEN NOT MATCHED THEN INSERT (team_id, team_name, country) VALUES (src.team_id, src.team_name, src.country);
            ''', t)
        logger.info(f"Upserted {len(teams)} teams.")

    def upsert_venues(self, venues: List[Tuple]):
        """UPSERT venue dimension records. Each tuple: (venue_id, name, city, country, capacity)"""
        cur = self.conn.cursor()
        for v in venues:
            cur.execute('''
                MERGE INTO venues AS tgt USING (VALUES (?,?,?,?,?)) AS src(venue_id, venue_name, city, country, capacity)
                ON tgt.venue_id = src.venue_id
                WHEN NOT MATCHED THEN INSERT (venue_id, venue_name, city, country, capacity)
                VALUES (src.venue_id, src.venue_name, src.city, src.country, src.capacity);
            ''', v)
        logger.info(f"Upserted {len(venues)} venues.")

    def upsert_series(self, series: List[Tuple]):
        """UPSERT series dimension records. Each tuple: (series_id, name, host, type, start_date, total)"""
        cur = self.conn.cursor()
        for s in series:
            cur.execute('''
                MERGE INTO series AS tgt USING (VALUES (?,?,?,?,?,?)) AS src(series_id, series_name, host_country, match_type, start_date, total_matches)
                ON tgt.series_id = src.series_id
                WHEN NOT MATCHED THEN INSERT (series_id, series_name, host_country, match_type, start_date, total_matches)
                VALUES (src.series_id, src.series_name, src.host_country, src.match_type, src.start_date, src.total_matches);
            ''', s)
        logger.info(f"Upserted {len(series)} series.")

    def upsert_match(self, match: Tuple):
        """UPSERT a single match record.
        Tuple: (match_id, series_id, desc, t1, t2, venue_id, date, fmt, winner, margin, v_type, toss_w, toss_d)"""
        cur = self.conn.cursor()
        cur.execute('''
            MERGE INTO matches AS tgt
            USING (VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)) AS src(
                match_id, series_id, match_description, team1_id, team2_id, venue_id,
                match_date, format, winning_team_id, victory_margin, victory_type,
                toss_winner_id, toss_decision
            ) ON tgt.match_id = src.match_id
            WHEN NOT MATCHED THEN INSERT (
                match_id, series_id, match_description, team1_id, team2_id, venue_id,
                match_date, format, winning_team_id, victory_margin, victory_type,
                toss_winner_id, toss_decision
            ) VALUES (
                src.match_id, src.series_id, src.match_description, src.team1_id, src.team2_id,
                src.venue_id, src.match_date, src.format, src.winning_team_id, src.victory_margin,
                src.victory_type, src.toss_winner_id, src.toss_decision
            );
        ''', match)

    def upsert_players(self, players: List[Tuple]):
        """UPSERT player records. Each tuple: (player_id, full_name, country, role)"""
        cur = self.conn.cursor()
        for pl in players:
            cur.execute('''
                MERGE INTO players AS tgt
                USING (VALUES (?,?,?,?,?,?)) AS src(player_id, full_name, country, playing_role, batting_style, bowling_style)
                ON tgt.player_id = src.player_id
                WHEN NOT MATCHED THEN
                    INSERT (player_id, full_name, country, playing_role, batting_style, bowling_style)
                    VALUES (src.player_id, src.full_name, src.country, src.playing_role, src.batting_style, src.bowling_style);
            ''', pl)
        logger.info(f"Upserted {len(players)} players.")

    def check_match_exists(self, match_id: str) -> bool:
        """Returns True if a match is already in SQL — avoids redundant API calls."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1 FROM matches WHERE match_id = ?", (str(match_id),))
            return cur.fetchone() is not None
        except Exception:
            return False


    def sync_data(self, df, b_id):
        """UPSERTs transformed data into the new Snowflake batting_stats schema."""
        if df.empty:
            return

        cur = self.conn.cursor()
        cur.execute("IF OBJECT_ID('tempdb..#bs') IS NOT NULL DROP TABLE #bs")
        cur.execute(
            "CREATE TABLE #bs ("
            "match_id VARCHAR(64), player_id INT, innings_id INT, "
            "batting_position INT, runs_scored INT, balls_faced INT, "
            "fours INT, sixes INT, dismissal_type NVARCHAR(100))"
        )

        recs = [
            (
                str(r.match_id) if r.match_id else "",
                int(r.player_id) if r.player_id else 0,
                int(r.innings_id),
                0,
                int(r.runs),
                int(r.balls),
                int(r.fours),
                int(r.sixes),
                str(r.dismissal)[:100]
            )
            for _, r in df.iterrows()
        ]

        cur.executemany("INSERT INTO #bs VALUES (?,?,?,?,?,?,?,?,?)", recs)

        merge_sql = '''
            MERGE INTO batting_stats AS t
            USING #bs AS s
            ON t.match_id = s.match_id AND t.player_id = s.player_id AND t.innings_id = s.innings_id
            WHEN MATCHED THEN
                UPDATE SET runs_scored=s.runs_scored, balls_faced=s.balls_faced,
                           fours=s.fours, sixes=s.sixes, dismissal_type=s.dismissal_type
            WHEN NOT MATCHED THEN
                INSERT (match_id, player_id, innings_id, batting_position,
                        runs_scored, balls_faced, fours, sixes, dismissal_type)
                VALUES (s.match_id, s.player_id, s.innings_id, s.batting_position,
                        s.runs_scored, s.balls_faced, s.fours, s.sixes, s.dismissal_type);
        '''
        cur.execute(merge_sql)

        cur.execute("INSERT INTO etl_log (b_id, rows, status, msg) VALUES (?, ?, 'SUCCESS', 'Batch loaded')", (b_id, len(df)))
        logger.info(f"Synchronized {len(df)} records to SQL Server.")

    def run_query(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """Executes a SELECT query and returns the results as a pandas DataFrame."""
        with self:
            try:
                if params:
                    return pd.read_sql(sql, self.conn, params=params)
                else:
                    return pd.read_sql(sql, self.conn)
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                return pd.DataFrame()
