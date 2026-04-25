import logging
import uuid
from pymongo import MongoClient
from config.config import cfg
from etl.proc import process_raw_data, audit
from database.sql_db import SqlDB

logging.basicConfig(level=cfg.L_LEVEL, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("BACKFILL")


def run_backfill():
    client = MongoClient(cfg.M_URL)
    db = client[cfg.DB]
    col = db[cfg.RAW_COL]

    total_docs = col.count_documents({})
    logger.info(f"Found {total_docs} raw documents in MongoDB.")

    if total_docs == 0:
        logger.info("No documents to backfill.")
        return

    # Initialize SQL DB once
    db_sql = SqlDB()
    db_sql.init_db()

    processed_docs = 0
    total_rows = 0
    errors = 0

    cursor = col.find().sort([('_ts', 1)])
    for doc in cursor:
        try:
            df = process_raw_data(doc)
            if df.empty:
                logger.info(f"Doc {doc.get('_id')} produced 0 rows; skipping.")
                processed_docs += 1
                continue

            chk = audit(df)
            if chk.get("rows", 0) == 0:
                logger.info(f"Doc {doc.get('_id')} had no rows after audit; skipping.")
                processed_docs += 1
                continue

            b_id = str(uuid.uuid4())
            with db_sql:
                db_sql.sync_data(df, b_id)

            total_rows += len(df)
            processed_docs += 1
            logger.info(f"Backfilled doc {doc.get('_id')}: {len(df)} rows (b_id={b_id}).")

        except Exception as e:
            logger.exception(f"Failed to backfill doc {doc.get('_id')}: {e}")
            errors += 1
            continue

    logger.info(f"Backfill complete. Docs processed: {processed_docs}/{total_docs}. Total rows written/merged: {total_rows}. Errors: {errors}.")


if __name__ == '__main__':
    run_backfill()
