import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from config.config import cfg

logger = logging.getLogger(__name__)

class CricApi:
    """Quick wrapper for the cricbuzz api."""
    def __init__(self):
        self.base = f"https://{cfg.HOST}/mcenter/v1"
        self.headers = {
            "x-rapidapi-key": cfg.RAPID_KEY,
            "x-rapidapi-host": cfg.HOST
        }

    def _get(self, url):
        """Internal helper — makes a single GET and returns JSON or None."""
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 204:
                return None
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"API call failed [{url}]: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_stats(self, mid=None):
        m_id = mid or cfg.DEFAULT_MID
        url = f"{self.base}/{m_id}/hscard"
        logger.info(f"fetching stats for {m_id}...")
        r = requests.get(url, headers=self.headers, timeout=10)
        if r.status_code != 200:
            logger.error(f"API returned status {r.status_code}: {r.text[:500]}")
            r.raise_for_status()
        try:
            json_data = r.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise
        if not json_data:
            logger.warning("api returned nothing")
            return {}
        return json_data

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_live_matches(self):
        """Fetches the list of live matches. 1 API call — primary quota saver."""
        url = f"https://{cfg.HOST}/matches/v1/live"
        logger.info("fetching live match list...")
        r = requests.get(url, headers=self.headers, timeout=10)
        logger.info(f"API Response Status: {r.status_code}")
        if r.status_code == 204:
            logger.info("No live matches available (HTTP 204)")
            return []
        if r.status_code != 200:
            logger.error(f"API returned status {r.status_code}: {r.text[:500]}")
            r.raise_for_status()
        try:
            json_data = r.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise
        if not json_data or "typeMatches" not in json_data:
            logger.warning("api returned no live match groups")
            return []
        matches = []
        for group in json_data.get("typeMatches", []):
            for m_wrapper in group.get("seriesMatches", []):
                for m in m_wrapper.get("seriesAdWrapper", {}).get("matches", []):
                    m["_series_name"] = m_wrapper.get("seriesAdWrapper", {}).get("seriesName", "Unknown Series")
                    m["_series_id"] = m_wrapper.get("seriesAdWrapper", {}).get("seriesId")
                    matches.append(m)
        return matches

    def get_match_info(self, mid):
        """Fetches match info (venue, teams, toss). 1 call per NEW match only."""
        url = f"{self.base}/{mid}/matchstats"
        logger.info(f"fetching match info for {mid}...")
        return self._get(url)


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_stats(self, mid=None):
        m_id = mid or cfg.DEFAULT_MID
        url = f"{self.base}/{m_id}/hscard"
        
        logger.info(f"fetching stats for {m_id}...")
        
        r = requests.get(url, headers=self.headers, timeout=10)
        
        # Check for HTTP errors
        if r.status_code != 200:
            logger.error(f"API returned status {r.status_code}: {r.text[:500]}")
            r.raise_for_status()
        
        try:
            json_data = r.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            logger.error(f"Response text: {r.text[:1000]}")
            raise
        
        if not json_data:
            logger.warning("api returned nothing")
            return {}
            
        return json_data

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_live_matches(self):
        """Fetches the list of live matches from the API."""
        url = f"https://{cfg.HOST}/matches/v1/live"
        logger.info("fetching live match list...")
        
        r = requests.get(url, headers=self.headers, timeout=10)
        
        # Log response details for debugging
        logger.info(f"API Response Status: {r.status_code}")
        logger.debug(f"API Response Headers: {r.headers}")
        
        # Handle 204 No Content (empty response is valid for "no live matches")
        if r.status_code == 204:
            logger.info("No live matches available (HTTP 204)")
            return []
        
        # Check for other HTTP errors
        if r.status_code != 200:
            logger.error(f"API returned status {r.status_code}: {r.text[:500]}")
            r.raise_for_status()
        
        try:
            json_data = r.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            logger.error(f"Response text: {r.text[:1000]}")
            raise
        
        if not json_data or "typeMatches" not in json_data:
            logger.warning("api returned no live match groups")
            return []
            
        # Flatten the nested response structure common in this API
        matches = []
        for group in json_data.get("typeMatches", []):
            for m_wrapper in group.get("seriesMatches", []):
                for m in m_wrapper.get("seriesAdWrapper", {}).get("matches", []):
                    matches.append(m)
        
        return matches
