from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# load the env stuff
p_root = Path('.')
load_dotenv(p_root / ".env")

uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
db_name = os.getenv("MONGO_DB", "ETL_Database")

client = MongoClient(uri)
db = client[db_name]

print(f"Database: {db_name}")
print("Collections:")
for col_name in db.list_collection_names():
    count = db[col_name].count_documents({})
    print(f" - {col_name}: {count} documents")
    
    # Check last document in each
    last = db[col_name].find_one(sort=[("_ts", -1)]) or db[col_name].find_one(sort=[("_ingestion_timestamp", -1)])
    if last:
        ts = last.get("_ts") or last.get("_ingestion_timestamp")
        print(f"   Last entry timestamp: {ts}")
    else:
        print("   No documents found or no timestamp field.")

client.close()
