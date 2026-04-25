-- Schema Definition for Cricket Analytics

-- Handle clashes with old schema if necessary
-- Check if matches table has INT match_id (system_type_id = 56)
IF OBJECT_ID('dbo.matches', 'U') IS NOT NULL 
    AND EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.matches') AND name = 'match_id' AND system_type_id = 56)
BEGIN
    PRINT 'Dropping old tables due to INT/VARCHAR mismatch...';
    -- Must drop children first due to foreign keys
    IF OBJECT_ID('dbo.batting_stats', 'U') IS NOT NULL DROP TABLE batting_stats;
    IF OBJECT_ID('dbo.bowling_stats', 'U') IS NOT NULL DROP TABLE bowling_stats;
    IF OBJECT_ID('dbo.fielding_stats', 'U') IS NOT NULL DROP TABLE fielding_stats;
    IF OBJECT_ID('dbo.matches', 'U') IS NOT NULL DROP TABLE matches;
END

IF OBJECT_ID('dbo.batting_stats', 'U') IS NOT NULL 
    AND NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.batting_stats') AND name = 'runs_scored')
BEGIN
    PRINT 'Renaming old legacy batting_stats to batting_stats_old';
    EXEC sp_rename 'batting_stats', 'batting_stats_old';
END

-- Tables
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[players]') AND type in (N'U'))
BEGIN
CREATE TABLE players (
    player_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    country VARCHAR(50),
    playing_role VARCHAR(50),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50)
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[teams]') AND type in (N'U'))
BEGIN
CREATE TABLE teams (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(100),
    country VARCHAR(50)
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[venues]') AND type in (N'U'))
BEGIN
CREATE TABLE venues (
    venue_id INT PRIMARY KEY,
    venue_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    capacity INT
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[series]') AND type in (N'U'))
BEGIN
CREATE TABLE series (
    series_id INT PRIMARY KEY,
    series_name VARCHAR(100),
    host_country VARCHAR(50),
    match_type VARCHAR(20),
    start_date DATE,
    total_matches INT
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[matches]') AND type in (N'U'))
BEGIN
CREATE TABLE matches (
    match_id VARCHAR(64) PRIMARY KEY,
    series_id INT,
    match_description VARCHAR(200),
    team1_id INT,
    team2_id INT,
    venue_id INT,
    match_date DATE,
    format VARCHAR(20), -- Test, ODI, T20I
    winning_team_id INT,
    victory_margin INT,
    victory_type VARCHAR(20), -- runs, wickets
    toss_winner_id INT,
    toss_decision VARCHAR(20), -- bat, bowl
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (winning_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (toss_winner_id) REFERENCES teams(team_id)
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[batting_stats]') AND type in (N'U'))
BEGIN
CREATE TABLE batting_stats (
    match_id VARCHAR(64),
    player_id INT,
    innings_id INT,
    batting_position INT,
    runs_scored INT,
    balls_faced INT,
    fours INT,
    sixes INT,
    dismissal_type VARCHAR(50),
    PRIMARY KEY (match_id, player_id, innings_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[bowling_stats]') AND type in (N'U'))
BEGIN
CREATE TABLE bowling_stats (
    match_id VARCHAR(64),
    player_id INT,
    overs_bowled DECIMAL(4,1),
    maidens INT,
    runs_conceded INT,
    wickets_taken INT,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[fielding_stats]') AND type in (N'U'))
BEGIN
CREATE TABLE fielding_stats (
    match_id VARCHAR(64),
    player_id INT,
    catches INT DEFAULT 0,
    stumpings INT DEFAULT 0,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
END

-- ==========================================
-- Data Migration from Old Schema
-- ==========================================

-- 1. Migrate Players from old dim_players
INSERT INTO players (player_id, full_name, country, playing_role, batting_style, bowling_style)
SELECT id, name, country, role, 'Unknown', 'Unknown' 
FROM dim_players
WHERE id NOT IN (SELECT player_id FROM players);

-- 1.5 Auto-fill missing players from batting_stats_old to satisfy Foreign Keys
IF OBJECT_ID('dbo.batting_stats_old', 'U') IS NOT NULL
BEGIN
    EXEC('
    INSERT INTO players (player_id, full_name, country, playing_role, batting_style, bowling_style)
    SELECT DISTINCT p_id, name, ''Unknown'', ''Unknown'', ''Unknown'', ''Unknown''
    FROM batting_stats_old
    WHERE p_id IS NOT NULL AND p_id NOT IN (SELECT player_id FROM players);
    ');
END

-- 2. Migrate Matches from old batting_stats
-- Using dynamic SQL (EXEC) to avoid parser errors with column names
IF OBJECT_ID('dbo.batting_stats_old', 'U') IS NOT NULL
BEGIN
    EXEC('
    INSERT INTO matches (match_id, match_description, format, match_date)
    SELECT DISTINCT match_id, ''Legacy Match Data'', ''Unknown'', GETDATE()
    FROM batting_stats_old
    WHERE match_id IS NOT NULL
      AND match_id NOT IN (SELECT match_id FROM matches);
    ');
END

-- 3. Migrate Batting Stats from legacy table
IF OBJECT_ID('dbo.batting_stats_old', 'U') IS NOT NULL
BEGIN
    EXEC('
    INSERT INTO batting_stats (match_id, player_id, innings_id, batting_position, runs_scored, balls_faced, fours, sixes, dismissal_type)
    SELECT 
        match_id, 
        p_id, 
        i_id, 
        0, -- Unknown position
        runs, 
        balls, 
        fours, 
        sixes, 
        dismissal
    FROM batting_stats_old
    WHERE valid = 1
      AND NOT EXISTS (
          SELECT 1 FROM batting_stats bs 
          WHERE bs.match_id = batting_stats_old.match_id 
            AND bs.player_id = batting_stats_old.p_id 
            AND bs.innings_id = batting_stats_old.i_id
      );
    ');
END

-- ==========================================
-- Beginner Level (Questions 1-8)
-- ==========================================

-- Question 1: Find all players who represent India.
SELECT full_name, playing_role, batting_style, bowling_style 
FROM players 
WHERE country = 'India';

-- Question 2: Matches played in the last 30 days.
SELECT m.match_description, t1.team_name AS team1, t2.team_name AS team2, 
       CONCAT(v.venue_name, ', ', v.city) AS venue, m.match_date
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.match_date >= DATEADD(day, -30, GETDATE())
ORDER BY m.match_date DESC;

-- Question 3: Top 10 highest run scorers in ODI cricket.
SELECT p.full_name, 
       SUM(b.runs_scored) AS total_runs, 
       CAST(SUM(b.runs_scored) AS FLOAT) / NULLIF(SUM(CASE WHEN b.dismissal_type != 'Not Out' THEN 1 ELSE 0 END), 0) AS batting_average,
       SUM(CASE WHEN b.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE m.format = 'ODI'
GROUP BY p.player_id, p.full_name
ORDER BY total_runs DESC
OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;

-- Question 4: Venues with seating capacity > 50,000.
SELECT venue_name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;

-- Question 5: Total wins per team.
SELECT t.team_name, COUNT(m.winning_team_id) AS total_wins
FROM teams t
LEFT JOIN matches m ON t.team_id = m.winning_team_id
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;

-- Question 6: Count players by role.
SELECT playing_role, COUNT(*) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;

-- Question 7: Highest individual batting score per format.
SELECT m.format, MAX(b.runs_scored) AS highest_score
FROM matches m
JOIN batting_stats b ON m.match_id = b.match_id
GROUP BY m.format;

-- Question 8: Series starting in 2024.
SELECT series_name, host_country, match_type, start_date, total_matches
FROM series
WHERE YEAR(start_date) = 2024;

-- ==========================================
-- Intermediate Level (Questions 9-16)
-- ==========================================

-- Question 9: All-rounders with > 1000 runs and > 50 wickets.
SELECT p.full_name, m.format,
       SUM(bat.runs_scored) AS total_runs, 
       SUM(bow.wickets_taken) AS total_wickets
FROM players p
JOIN matches m ON 1=1 -- to link formats appropriately we group by format per player
LEFT JOIN batting_stats bat ON p.player_id = bat.player_id AND m.match_id = bat.match_id
LEFT JOIN bowling_stats bow ON p.player_id = bow.player_id AND m.match_id = bow.match_id
WHERE p.playing_role = 'All-rounder'
GROUP BY p.player_id, p.full_name, m.format
HAVING SUM(bat.runs_scored) > 1000 AND SUM(bow.wickets_taken) > 50;

-- Question 10: Details of last 20 completed matches.
SELECT TOP 20 m.match_description, t1.team_name AS team1, t2.team_name AS team2, 
       wt.team_name AS winning_team, m.victory_margin, m.victory_type, v.venue_name
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN teams wt ON m.winning_team_id = wt.team_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.winning_team_id IS NOT NULL
ORDER BY m.match_date DESC;

-- Question 11: Compare player performance across formats (pivoted).
WITH FormatRuns AS (
    SELECT p.player_id, p.full_name, m.format,
           SUM(b.runs_scored) as format_runs,
           SUM(CASE WHEN b.dismissal_type != 'Not Out' THEN 1 ELSE 0 END) as format_outs
    FROM players p
    JOIN batting_stats b ON p.player_id = b.player_id
    JOIN matches m ON b.match_id = m.match_id
    GROUP BY p.player_id, p.full_name, m.format
)
SELECT full_name,
       SUM(CASE WHEN format = 'Test' THEN format_runs ELSE 0 END) AS test_runs,
       SUM(CASE WHEN format = 'ODI' THEN format_runs ELSE 0 END) AS odi_runs,
       SUM(CASE WHEN format = 'T20I' THEN format_runs ELSE 0 END) AS t20i_runs,
       CAST(SUM(format_runs) AS FLOAT) / NULLIF(SUM(format_outs), 0) AS overall_avg
FROM FormatRuns
GROUP BY player_id, full_name
HAVING COUNT(DISTINCT format) >= 2;

-- Question 12: Team performance home vs away.
WITH HomeAwayWins AS (
    SELECT t.team_id, t.team_name,
           CASE WHEN t.country = v.country THEN 'Home' ELSE 'Away' END as condition,
           COUNT(m.winning_team_id) as wins
    FROM teams t
    JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id) AND m.winning_team_id = t.team_id
    JOIN venues v ON m.venue_id = v.venue_id
    GROUP BY t.team_id, t.team_name, CASE WHEN t.country = v.country THEN 'Home' ELSE 'Away' END
)
SELECT team_name,
       SUM(CASE WHEN condition = 'Home' THEN wins ELSE 0 END) AS home_wins,
       SUM(CASE WHEN condition = 'Away' THEN wins ELSE 0 END) AS away_wins
FROM HomeAwayWins
GROUP BY team_id, team_name;

-- Question 13: Batting partnerships >= 100 runs.
SELECT p1.full_name AS batter1, p2.full_name AS batter2, 
       (b1.runs_scored + b2.runs_scored) AS combined_runs,
       b1.match_id, b1.innings_id
FROM batting_stats b1
JOIN batting_stats b2 ON b1.match_id = b2.match_id 
     AND b1.innings_id = b2.innings_id 
     AND b2.batting_position = b1.batting_position + 1
JOIN players p1 ON b1.player_id = p1.player_id
JOIN players p2 ON b2.player_id = p2.player_id
WHERE (b1.runs_scored + b2.runs_scored) >= 100;

-- Question 14: Bowling performance at different venues.
SELECT p.full_name, v.venue_name,
       COUNT(DISTINCT m.match_id) as matches_played,
       SUM(b.wickets_taken) as total_wickets,
       CAST(SUM(b.runs_conceded) AS FLOAT) / NULLIF(SUM(FLOOR(b.overs_bowled) + (b.overs_bowled - FLOOR(b.overs_bowled))*10/6.0), 0) as avg_economy
FROM bowling_stats b
JOIN matches m ON b.match_id = m.match_id
JOIN venues v ON m.venue_id = v.venue_id
JOIN players p ON b.player_id = p.player_id
WHERE b.overs_bowled >= 4
GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name
HAVING COUNT(DISTINCT m.match_id) >= 3;

-- Question 15: Players performing well in close matches.
WITH CloseMatches AS (
    SELECT match_id, winning_team_id
    FROM matches
    WHERE (victory_type = 'runs' AND victory_margin < 50)
       OR (victory_type = 'wickets' AND victory_margin < 5)
)
SELECT p.full_name,
       COUNT(DISTINCT c.match_id) as close_matches_played,
       AVG(b.runs_scored) as avg_runs_in_close,
       SUM(CASE WHEN m.winning_team_id = t.team_id THEN 1 ELSE 0 END) as close_match_wins
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN CloseMatches c ON b.match_id = c.match_id
JOIN matches m ON c.match_id = m.match_id
JOIN teams t ON p.country = t.country
GROUP BY p.player_id, p.full_name;

-- Question 16: Player batting performance by year since 2020.
SELECT p.full_name, YEAR(m.match_date) as match_year,
       AVG(CAST(b.runs_scored AS FLOAT)) as avg_runs_per_match,
       AVG(CAST(b.runs_scored AS FLOAT) / NULLIF(b.balls_faced, 0) * 100) as avg_strike_rate
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE YEAR(m.match_date) >= 2020
GROUP BY p.player_id, p.full_name, YEAR(m.match_date)
HAVING COUNT(DISTINCT m.match_id) >= 5;

-- ==========================================
-- Advanced Level (Questions 17-25)
-- ==========================================

-- Question 17: Advantage of winning the toss.
SELECT toss_decision,
       COUNT(match_id) as total_matches,
       SUM(CASE WHEN toss_winner_id = winning_team_id THEN 1 ELSE 0 END) as wins_after_toss,
       CAST(SUM(CASE WHEN toss_winner_id = winning_team_id THEN 1 ELSE 0 END) AS FLOAT) / COUNT(match_id) * 100 as win_percentage
FROM matches
WHERE winning_team_id IS NOT NULL
GROUP BY toss_decision;

-- Question 18: Most economical bowlers in limited-overs cricket.
SELECT p.full_name,
       SUM(b.wickets_taken) as total_wickets,
       CAST(SUM(b.runs_conceded) AS FLOAT) / NULLIF(SUM(FLOOR(b.overs_bowled) + (b.overs_bowled - FLOOR(b.overs_bowled))*10/6.0), 0) as overall_economy
FROM players p
JOIN bowling_stats b ON p.player_id = b.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE m.format IN ('ODI', 'T20I')
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT m.match_id) >= 10
   AND AVG(FLOOR(b.overs_bowled) + (b.overs_bowled - FLOOR(b.overs_bowled))*10/6.0) >= 2
ORDER BY overall_economy ASC;

-- Question 19: Batsmen consistency (Standard Deviation).
SELECT p.full_name,
       AVG(CAST(b.runs_scored AS FLOAT)) as avg_runs,
       STDEV(b.runs_scored) as stddev_runs
FROM players p
JOIN batting_stats b ON p.player_id = b.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE YEAR(m.match_date) >= 2022 AND b.balls_faced >= 10
GROUP BY p.player_id, p.full_name
ORDER BY stddev_runs ASC;

-- Question 20: Matches played and batting average by format for players with >=20 matches total.
WITH PlayerFormatStats AS (
    SELECT p.player_id, p.full_name, m.format,
           COUNT(DISTINCT m.match_id) as matches_played,
           CAST(SUM(b.runs_scored) AS FLOAT) / NULLIF(SUM(CASE WHEN b.dismissal_type != 'Not Out' THEN 1 ELSE 0 END), 0) as batting_avg
    FROM players p
    JOIN batting_stats b ON p.player_id = b.player_id
    JOIN matches m ON b.match_id = m.match_id
    GROUP BY p.player_id, p.full_name, m.format
), PlayerTotalMatches AS (
    SELECT player_id, COUNT(DISTINCT match_id) as total_matches
    FROM batting_stats
    GROUP BY player_id
    HAVING COUNT(DISTINCT match_id) >= 20
)
SELECT f.full_name, f.format, f.matches_played, f.batting_avg
FROM PlayerFormatStats f
JOIN PlayerTotalMatches t ON f.player_id = t.player_id;

-- Question 21: Comprehensive performance ranking system.
WITH PlayerMetrics AS (
    SELECT p.player_id, p.full_name, m.format,
           -- Batting
           SUM(b.runs_scored) as runs,
           CAST(SUM(b.runs_scored) AS FLOAT) / NULLIF(SUM(CASE WHEN b.dismissal_type != 'Not Out' THEN 1 ELSE 0 END), 0) as bat_avg,
           CAST(SUM(b.runs_scored) AS FLOAT) / NULLIF(SUM(b.balls_faced), 0) * 100 as sr,
           -- Bowling
           SUM(bw.wickets_taken) as wkts,
           CAST(SUM(bw.runs_conceded) AS FLOAT) / NULLIF(SUM(bw.wickets_taken), 0) as bowl_avg,
           CAST(SUM(bw.runs_conceded) AS FLOAT) / NULLIF(SUM(FLOOR(bw.overs_bowled) + (bw.overs_bowled - FLOOR(bw.overs_bowled))*10/6.0), 0) as econ,
           -- Fielding
           SUM(f.catches) as catches,
           SUM(f.stumpings) as stumpings
    FROM players p
    JOIN matches m ON 1=1
    LEFT JOIN batting_stats b ON p.player_id = b.player_id AND m.match_id = b.match_id
    LEFT JOIN bowling_stats bw ON p.player_id = bw.player_id AND m.match_id = bw.match_id
    LEFT JOIN fielding_stats f ON p.player_id = f.player_id AND m.match_id = f.match_id
    GROUP BY p.player_id, p.full_name, m.format
)
SELECT full_name, format,
       (COALESCE(runs, 0) * 0.01 + COALESCE(bat_avg, 0) * 0.5 + COALESCE(sr, 0) * 0.3) +
       (COALESCE(wkts, 0) * 2 + (50 - COALESCE(bowl_avg, 50)) * 0.5 + (6 - COALESCE(econ, 6)) * 2) +
       (COALESCE(catches, 0) * 3 + COALESCE(stumpings, 0) * 5) AS weighted_score
FROM PlayerMetrics
ORDER BY format, weighted_score DESC;

-- Question 22: Head-to-head match prediction analysis.
WITH H2H AS (
    SELECT m.team1_id, t1.team_name as team1, m.team2_id, t2.team_name as team2,
           COUNT(*) as total_matches,
           SUM(CASE WHEN m.winning_team_id = m.team1_id THEN 1 ELSE 0 END) as t1_wins,
           SUM(CASE WHEN m.winning_team_id = m.team2_id THEN 1 ELSE 0 END) as t2_wins,
           AVG(CASE WHEN m.winning_team_id = m.team1_id THEN m.victory_margin ELSE NULL END) as t1_avg_margin,
           AVG(CASE WHEN m.winning_team_id = m.team2_id THEN m.victory_margin ELSE NULL END) as t2_avg_margin
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    WHERE m.match_date >= DATEADD(year, -3, GETDATE())
    GROUP BY m.team1_id, t1.team_name, m.team2_id, t2.team_name
    HAVING COUNT(*) >= 5
)
SELECT team1, team2, total_matches, t1_wins, t2_wins, t1_avg_margin, t2_avg_margin,
       CAST(t1_wins AS FLOAT) / total_matches * 100 as t1_win_pct,
       CAST(t2_wins AS FLOAT) / total_matches * 100 as t2_win_pct
FROM H2H;

-- Question 23: Analyze recent player form and momentum.
WITH RecentMatches AS (
    SELECT player_id, match_id, runs_scored, CAST(runs_scored AS FLOAT)/NULLIF(balls_faced,0)*100 as sr,
           ROW_NUMBER() OVER(PARTITION BY player_id ORDER BY match_id DESC) as rn
    FROM batting_stats
), PlayerStats AS (
    SELECT player_id,
           AVG(CASE WHEN rn <= 5 THEN CAST(runs_scored AS FLOAT) END) as avg_last_5,
           AVG(CASE WHEN rn <= 10 THEN CAST(runs_scored AS FLOAT) END) as avg_last_10,
           AVG(CASE WHEN rn <= 10 THEN sr END) as recent_sr,
           SUM(CASE WHEN rn <= 10 AND runs_scored > 50 THEN 1 ELSE 0 END) as fifties_last_10,
           STDEV(CASE WHEN rn <= 10 THEN runs_scored END) as stddev_last_10
    FROM RecentMatches
    WHERE rn <= 10
    GROUP BY player_id
)
SELECT p.full_name, ps.avg_last_5, ps.avg_last_10, ps.recent_sr, ps.fifties_last_10, ps.stddev_last_10,
       CASE 
           WHEN ps.avg_last_5 > 40 AND ps.fifties_last_10 >= 3 THEN 'Excellent Form'
           WHEN ps.avg_last_5 > 30 THEN 'Good Form'
           WHEN ps.avg_last_5 > 20 THEN 'Average Form'
           ELSE 'Poor Form'
       END as form_status
FROM PlayerStats ps
JOIN players p ON ps.player_id = p.player_id;

-- Question 24: Study successful batting partnerships.
WITH Partnerships AS (
    SELECT b1.match_id, p1.full_name as batter1, p2.full_name as batter2,
           (b1.runs_scored + b2.runs_scored) as partnership_runs
    FROM batting_stats b1
    JOIN batting_stats b2 ON b1.match_id = b2.match_id AND b1.innings_id = b2.innings_id AND b2.batting_position = b1.batting_position + 1
    JOIN players p1 ON b1.player_id = p1.player_id
    JOIN players p2 ON b2.player_id = p2.player_id
)
SELECT batter1, batter2,
       COUNT(*) as total_partnerships,
       AVG(partnership_runs) as avg_partnership_runs,
       SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) as fifty_plus_partnerships,
       MAX(partnership_runs) as highest_partnership,
       CAST(SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as success_rate
FROM Partnerships
GROUP BY batter1, batter2
HAVING COUNT(*) >= 5
ORDER BY success_rate DESC;

-- Question 25: Time-series analysis of player performance evolution.
WITH QuarterlyStats AS (
    SELECT b.player_id, 
           DATEPART(year, m.match_date) as m_year,
           DATEPART(quarter, m.match_date) as m_quarter,
           COUNT(b.match_id) as matches,
           AVG(CAST(b.runs_scored AS FLOAT)) as avg_runs,
           AVG(CAST(b.runs_scored AS FLOAT)/NULLIF(b.balls_faced,0)*100) as avg_sr
    FROM batting_stats b
    JOIN matches m ON b.match_id = m.match_id
    GROUP BY b.player_id, DATEPART(year, m.match_date), DATEPART(quarter, m.match_date)
    HAVING COUNT(b.match_id) >= 3
), PlayerQuarterCounts AS (
    SELECT player_id, COUNT(*) as quarters_played
    FROM QuarterlyStats
    GROUP BY player_id
    HAVING COUNT(*) >= 6
)
SELECT p.full_name, qs.m_year, qs.m_quarter, qs.avg_runs, qs.avg_sr,
       LAG(qs.avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.m_year, qs.m_quarter) as prev_q_runs,
       CASE 
           WHEN qs.avg_runs > LAG(qs.avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.m_year, qs.m_quarter) * 1.1 THEN 'Improving'
           WHEN qs.avg_runs < LAG(qs.avg_runs) OVER(PARTITION BY qs.player_id ORDER BY qs.m_year, qs.m_quarter) * 0.9 THEN 'Declining'
           ELSE 'Stable'
       END as trend
FROM QuarterlyStats qs
JOIN PlayerQuarterCounts pqc ON qs.player_id = pqc.player_id
JOIN players p ON qs.player_id = p.player_id
ORDER BY p.full_name, qs.m_year, qs.m_quarter;
