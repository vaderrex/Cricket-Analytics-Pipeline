import logging
import uuid
import sys
from database.m_store import MStore
from database.sql_db import SqlDB
from etl.proc import process_raw_data, audit
from config.config import cfg

# Setup minimal logging to see what happens
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("TEST_RUN")

def test_mongo_to_sql():
    logger.info("Starting test run: MongoDB (Bronze) -> SQL Server (Gold)")
    
    # 1. Fetch latest from MongoDB
    with MStore() as m:
        raw_data = m.get_last()
    
    if not raw_data:
        logger.error("No data found in MongoDB scorecards_raw! Run main.py first.")
        return

    logger.info(f"Successfully fetched latest raw data from Mongo. ID: {raw_data.get('_id')}")

    # 2. Transform the data
    try:
        df = process_raw_data(raw_data)
        chk = audit(df)
        
        if not chk["ok"] and chk.get("rows", 0) == 0:
            logger.error("Transformation resulted in 0 rows. Check if the JSON structure has changed.")
            return
            
        logger.info(f"Transformed data into {len(df)} batting stats records.")
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        return

    # 3. Load into SQL Server
    try:
        db = SqlDB()
        db.init_db() # Ensures tables exist
        
        batch_id = str(uuid.uuid4())
        with db:
            db.sync_data(df, batch_id)
        
        logger.info(f"SUCCESS: Data synchronized to SQL Server (Batch: {batch_id})")
        
        # 4. Verify by checking the log table
        log_df = db.run_query(f"SELECT TOP 1 * FROM etl_log WHERE b_id = '{batch_id}'")
        if not log_df.empty:
            logger.info("Verified etl_log entry:")
            print(log_df.to_string())
        else:
            logger.warning("Could not find log entry in SQL Server.")

    except Exception as e:
        logger.error(f"SQL Load failed: {e}")

if __name__ == "__main__":
    test_mongo_to_sql()
