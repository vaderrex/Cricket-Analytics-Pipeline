import pymongo
from config.config import cfg
import json

def inspect_mongo():
    client = pymongo.MongoClient(cfg.M_URL)
    db = client[cfg.DB]
    col = db[cfg.RAW_COL]
    
    last_doc = col.find_one(sort=[('_id', pymongo.DESCENDING)])
    if not last_doc:
        print("No documents found in MongoDB.")
        return

    print(f"Latest Doc ID: {last_doc.get('_id')}")
    print(f"Number of documents in collection: {col.count_documents({})}")
    
    # Print structure of scorecard
    scorecard = last_doc.get("scorecard", [])
    print(f"Scorecard entries: {len(scorecard)}")
    
    for i, inn in enumerate(scorecard):
        i_id = inn.get("inningsid")
        bats = inn.get("batsman", [])
        print(f"  Innings {i+1}: ID={i_id}, Batsmen Count={len(bats)}")
        if bats:
            print(f"    Example Batsman: {bats[0].get('name')} (ID: {bats[0].get('id')})")

    # Check for match identifier
    match_id = last_doc.get("matchId") or last_doc.get("match_id")
    print(f"Match ID found: {match_id}")

if __name__ == "__main__":
    inspect_mongo()
