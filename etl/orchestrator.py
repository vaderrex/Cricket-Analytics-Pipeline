import uuid
import logging
from datetime import date
from typing import Optional
from config.config import cfg
from api.cric_api import CricApi
from database.m_store import MStore
from database.sql_db import SqlDB
from etl.proc import process_raw_data, audit

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        self.b_id = str(uuid.uuid4())
        self.api = CricApi()

    def run(self, match_id: Optional[str] = None):
        """Main entry point. Quota-aware: only calls API for new matches."""
        logger.info(f"--- STARTING BATCH: {self.b_id} ---")

        try:
            db = SqlDB()
            db.init_db()  # ensure all Snowflake tables exist

            # Step 1: One API call to get live match list + dimension data
            live_matches = self.api.get_live_matches()

            if not live_matches:
                # Fallback: use the configured default match_id
                logger.info("No live matches. Falling back to default match_id.")
                self._process_single_match(db, match_id or cfg.DEFAULT_MID)
            else:
                self._process_live_matches(db, live_matches)

            logger.info(f"--- COMPLETED BATCH: {self.b_id} ---")

        except Exception as e:
            logger.exception(f"Pipeline failure: {e}")
            raise

    def _process_live_matches(self, db: SqlDB, live_matches: list):
        """
        Extract dimension data from live match list JSON (free \u2014 no extra API calls),
        then fetch scorecards ONLY for new matches we haven\u2019t stored yet.
        """
        teams_to_upsert = {}
        series_to_upsert = {}
        venues_to_upsert = {}
        new_match_ids = []

        for m in live_matches:
            info = m.get("matchInfo", {})
            mid = str(info.get("matchId", ""))
            if not mid:
                continue

            # --- Extract Teams (zero extra API calls) ---
            t1 = info.get("team1", {})
            t2 = info.get("team2", {})
            if t1.get("teamId"):
                teams_to_upsert[t1["teamId"]] = (t1["teamId"], t1.get("teamName", "Unknown"), t1.get("teamSName", ""))
            if t2.get("teamId"):
                teams_to_upsert[t2["teamId"]] = (t2["teamId"], t2.get("teamName", "Unknown"), t2.get("teamSName", ""))

            # --- Extract Series (zero extra API calls) ---
            s_id = m.get("_series_id")
            s_name = m.get("_series_name", "Unknown Series")
            if s_id:
                series_to_upsert[s_id] = (
                    s_id, s_name, "Unknown",
                    info.get("matchFormat", "Unknown"),
                    date.today(), 0
                )

            # --- Extract Venue (zero extra API calls) ---
            venue = info.get("venueInfo", {})
            v_id = venue.get("id")
            if v_id:
                venues_to_upsert[v_id] = (
                    v_id,
                    venue.get("ground", "Unknown"),
                    venue.get("city", "Unknown"),
                    venue.get("country", "Unknown"),
                    venue.get("capacity", 0) or 0
                )

            # --- Check if we already have this match (saves API quota!) ---
            with db:
                already_exists = db.check_match_exists(mid)

            if not already_exists:
                new_match_ids.append((mid, info, m))

        # Upsert all dimension data extracted for FREE from the live match list
        if teams_to_upsert:
            with db:
                db.upsert_teams(list(teams_to_upsert.values()))

        if venues_to_upsert:
            with db:
                db.upsert_venues(list(venues_to_upsert.values()))

        if series_to_upsert:
            with db:
                db.upsert_series(list(series_to_upsert.values()))

        logger.info(f"Found {len(new_match_ids)} new matches to fetch scorecards for.")

        # Fetch scorecards only for NEW matches (each is 1 API call)
        for mid, info, m_raw in new_match_ids:
            self._process_single_match(db, mid, info=info, m_raw=m_raw)

    def _process_single_match(self, db: SqlDB, mid: str, info: dict = None, m_raw: dict = None):
        """Fetch scorecard for one match (1 API call) and load all data into SQL."""
        raw = self._get_raw(mid)
        if not raw:
            return

        df = process_raw_data(raw)
        chk = audit(df)

        if chk.get("rows", 0) == 0:
            logger.warning(f"Empty batting data for match {mid}, skipping.")
            return

        with db:
            # Step 1: Insert match record (must be before batting_stats due to FK)
            if info:
                t1 = info.get("team1", {})
                t2 = info.get("team2", {})
                toss = info.get("tossResults", {})
                result = info.get("result", {})
                venue = info.get("venueInfo", {})
                win_team = result.get("winningTeam")
                match_tuple = (
                    str(mid),
                    m_raw.get("_series_id") if m_raw else None,
                    info.get("matchDesc", "Live Match"),
                    t1.get("teamId"), t2.get("teamId"),
                    venue.get("id"),
                    date.today(),
                    info.get("matchFormat", "Unknown"),
                    win_team.get("teamId") if isinstance(win_team, dict) else None,
                    result.get("winByRuns") or result.get("winByWickets"),
                    "runs" if result.get("winByRuns") else "wickets",
                    toss.get("tossWinnerId"),
                    toss.get("decision", "").lower() or None
                )
                db.upsert_match(match_tuple)
            else:
                # Minimal match record just to satisfy FK constraint
                db.upsert_match((str(mid), None, "Legacy Match", None, None, None,
                                 date.today(), "Unknown", None, None, None, None, None))

            # Step 2: Auto-insert players found in scorecard (prevents player FK violations)
            players = [
                (int(r.player_id), str(r["name"]), "Unknown", "Unknown", "Unknown", "Unknown")
                for _, r in df.iterrows()
                if r.player_id is not None
            ]
            if players:
                db.upsert_players(players)

            # Step 3: Load batting stats (match + players now guaranteed to exist)
            db.sync_data(df, self.b_id)

        logger.info(f"Processed match {mid}: {len(df)} batting records loaded.")

    def _get_raw(self, mid):
        """Fetch scorecard from API and store in MongoDB Bronze layer."""
        data = self.api.get_stats(mid)
        if not data:
            return None
        with MStore() as m:
            m.store_raw(data)
            return m.get_last()
