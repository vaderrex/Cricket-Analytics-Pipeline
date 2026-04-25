import pandas as pd
import logging

logger = logging.getLogger(__name__)

def process_raw_data(raw):
    """Parses raw JSON from MongoDB into a flattened DataFrame with basic metrics."""
    if not raw or "scorecard" not in raw:
        logger.warning("No scorecard data found in raw payload.")
        return pd.DataFrame()

    # Prefer the Mongo document _id (unique per stored document) so each
    # API document becomes a unique match snapshot. Fall back to API matchId
    # if _id is not present.
    match_id = None
    if raw.get("_id") is not None:
        match_id = str(raw.get("_id"))
    else:
        match_id = raw.get("matchId") or raw.get("match_id")
        if match_id is not None:
            match_id = str(match_id)
    
    # Also capture the API-provided match id (if present) as source_match_id
    source_match_id = raw.get("matchId") or raw.get("match_id")
    if source_match_id is not None:
        source_match_id = str(source_match_id)

    recs = []
    for inn in raw.get("scorecard", []):
        i_id = inn.get("inningsid")
        bats = inn.get("batsman", [])
        
        for p in bats:
            recs.append({
                "match_id": match_id,
                "player_id": p.get("id"),
                "name": p.get("name"),
                "source_match_id": source_match_id,
                "innings_id": i_id,
                "runs": int(p.get("runs", 0)),
                "balls": int(p.get("balls", 0)),
                "fours": int(p.get("fours", 0)),
                "sixes": int(p.get("sixes", 0)),
                "strike_rate": float(p.get("strkrate", 0)) if p.get("strkrate") else 0.0,
                "dismissal": p.get("outdec", "DNB")
            })

    df = pd.DataFrame(recs)
    if df.empty:
        return df

    # Feature engineering: boundaries and tiered categories
    df["boundary_runs"] = (df["fours"] * 4) + (df["sixes"] * 6)
    df["boundary_pct"] = (df["boundary_runs"] / df["runs"]).fillna(0) * 100
    
    def get_tier(runs):
        if runs >= 100: return "Cent"
        if runs >= 50: return "Half"
        if runs >= 30: return "30+"
        return "Normal"
    
    df["perf_category"] = df["runs"].apply(get_tier)
    df["is_valid_record"] = df["player_id"].notna() & df["name"].notna()
    
    logger.info(f"Processed {len(df)} batting records.")
    return df

def audit(df):
    """Executes data quality checks on the transformed data."""
    if df.empty:
        return {"ok": False, "rows": 0}
    
    dups = int(df.duplicated(subset=["player_id", "innings_id"]).sum())
    
    report = {
        "ok": dups == 0,
        "rows": len(df),
        "dups": dups,
        "missing": int((~df["is_valid_record"]).sum())
    }
    
    if dups > 0:
        logger.error(f"Integrity check failed: {dups} duplicate records found.")
        
    return report
