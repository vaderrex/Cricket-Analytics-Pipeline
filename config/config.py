import os
from pathlib import Path
from dotenv import load_dotenv

# load the env stuff
p_root = Path(__file__).parent.parent
load_dotenv(p_root / ".env")

class Config:
    # API shit
    RAPID_KEY = os.getenv("RAPIDAPI_KEY")
    HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
    DEFAULT_MID = os.getenv("CRICKET_MATCH_ID", "105820")
    
    # Mongo info
    M_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB = os.getenv("MONGO_DB", "CrickAnalytics")
    RAW_COL = "scorecards_raw"
    
    # SQL db
    SQL_SRV = os.getenv("SQL_SERVER", ".")
    SQL_DB = os.getenv("SQL_DB_NAME", "CricketAnalyticsDB")
    DRIVER = os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}")
    
    @property
    def conn_str(self):
        # standard sql connection
        return f"DRIVER={self.DRIVER};SERVER={self.SQL_SRV};DATABASE={self.SQL_DB};Trusted_Connection=yes;TrustServerCertificate=yes;"

    @property
    def master_conn(self):
        # need this to create the db if it doesn't exist yet
        return self.conn_str.replace(f"DATABASE={self.SQL_DB}", "DATABASE=master")

    # Logging and stuff
    L_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    INTERVAL = 6 # hours

# instance for the app
cfg = Config()
