from config.config import cfg
import pyodbc

cn = pyodbc.connect(cfg.conn_str)
cur = cn.cursor()
cur.execute('SELECT COUNT(*) FROM batting_stats')
print('sql_total:', cur.fetchone()[0])
cur.execute('SELECT COUNT(DISTINCT match_id) FROM batting_stats')
print('distinct_matches:', cur.fetchone()[0])
cur.execute("SELECT SUM(rows) FROM etl_log WHERE status='SUCCESS'")
print('etl_log_rows_sum:', cur.fetchone()[0])
cn.close()
