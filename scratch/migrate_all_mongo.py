import logging
import uuid
from database.m_store import MStore
from database.sql_db import SqlDB
from etl.proc import process_raw_data, audit
from config.config import cfg

# Setup minimal logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("BULK_MIGRATE")

def migrate_all():
    logger.info("Starting historical migration: All MongoDB scorecards -> SQL Server (Gold)")
    
    # 1. Fetch ALL records from MongoDB
    records = []
    with MStore() as m:
        if m.cli:
            db = m.cli[m.db_name]
            cursor = db[cfg.RAW_COL].find({})
            records = list(cursor)
    
    if not records:
        logger.error(f"No data found in MongoDB {cfg.RAW_COL}! Cannot migrate.")
        return

    logger.info(f"Successfully fetched {len(records)} raw JSON documents from Mongo.")

    db_sql = SqlDB()
    db_sql.init_db() # Ensures tables exist

    success_count = 0
    total_processed = 0

    for idx, raw_data in enumerate(records):
        logger.info(f"--- Processing Document {idx+1}/{len(records)} (ID: {raw_data.get('_id')}) ---")
        
        # 2. Transform the data
        try:
            df = process_raw_data(raw_data)
            chk = audit(df)
            
            if not chk["ok"] and chk.get("rows", 0) == 0:
                logger.warning(f"Skipping document {idx+1} - resulted in 0 rows or invalid data structure.")
                continue
                
            logger.info(f"Transformed data into {len(df)} batting stats records.")
            
            # 3. Load into SQL Server
            batch_id = str(uuid.uuid4())
            with db_sql:
                db_sql.sync_data(df, batch_id)
            
            logger.info(f"SUCCESS: Batch synchronized to SQL Server (Batch: {batch_id})")
            success_count += 1
            total_processed += len(df)
            
        except Exception as e:
            logger.error(f"Failed to process document {idx+1}: {e}")
            continue

    logger.info(f"=== Migration Complete ===")
    logger.info(f"Successfully migrated {success_count}/{len(records)} documents.")
    logger.info(f"Total SQL records inserted/updated: {total_processed}")

if __name__ == "__main__":
    migrate_all()
