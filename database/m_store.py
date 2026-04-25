from pymongo import MongoClient
from datetime import datetime
from config.config import cfg
import logging

logger = logging.getLogger(__name__)

class MStore:
    """mongo storage for raw api data"""
    def __init__(self):
        self.url = cfg.M_URL
        self.db_name = cfg.DB
        self.cli = None

    def __enter__(self):
        self.cli = MongoClient(self.url, serverSelectionTimeoutMS=5000)
        return self

    def __exit__(self, *args):
        if self.cli:
            self.cli.close()

    def store_raw(self, data):
        if not self.cli: return
            
        db = self.cli[self.db_name]
        c = db[cfg.RAW_COL]
        
        # add some basic meta
        save_obj = data.copy()
        save_obj["_ts"] = datetime.utcnow()
        save_obj["src"] = "rapid"
        
        save_obj.pop("_id", None)
        
        try:
            res = c.insert_one(save_obj)
            logger.info(f"saved to mongo {res.inserted_id}")
            return res.inserted_id
        except Exception as e:
            logger.error(f"mongo error: {e}")
            raise

    def get_last(self):
        if not self.cli: return None
        db = self.cli[self.db_name]
        c = db[cfg.RAW_COL]
        return c.find_one(sort=[("_ts", -1)])
