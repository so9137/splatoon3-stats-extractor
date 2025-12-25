import requests
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Generator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STAT_INK_BASE_URL = "https://stat.ink/api/v3"
USER_AGENT = "Splatoon3StatsExtractor/1.0"

class StatInkFetcher:
    def __init__(self, username: str):
        self.username = username
        self.base_url = f"{STAT_INK_BASE_URL}/battle"
        # User specific feed URL pattern
        self.user_feed_url = f"https://stat.ink/@{self.username}/spl3/index.json"

    def fetch_battles(self, mode: str = "daily", days: int = 21) -> List[Dict]:
        """
        Fetch battles from stat.ink in a SINGLE request.
        
        Args:
            mode: 'daily' (last 24h) or 'backfill' (historical).
            days: Number of days of history to fetch (max 21).
        
        Returns:
            List of battle dictionaries (limited by API response size, usually 100).
        """
        params = {"f[lobby]": "xmatch"}
        
        if mode == "daily":
            params["f[term]"] = "24h"
            logger.info(f"Fetching daily battles (24h) with params: {params}")
        
        elif mode == "backfill":
            # Enforce max 21 days (3 weeks) as requested
            if days > 21:
                logger.warning(f"Requested {days} days, capping at 21 days as per configuration.")
                days = 21
            if days <= 0:
                days = 21 # Default to 21 if 0 passed
                
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format: @unix_timestamp for server-side strict filtering
            t_start = int(start_date.timestamp())
            t_end = int(end_date.timestamp())
            
            params["f[term]"] = "term" # Required for term_from/to to work reliably
            params["f[term_from]"] = f"@{t_start}"
            params["f[term_to]"] = f"@{t_end}"
            
            logger.info(f"Fetching backfill ({days} days) single request from {start_date} (@{t_start}) to {end_date} (@{t_end})")

        # Validate mode
        if mode not in ["daily", "backfill"]:
             raise ValueError(f"Unknown mode: {mode}")

        try:
            logger.info(f"Making API request with params: {params}...")
            response = requests.get(
                self.user_feed_url,
                params=params,
                headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.info("No data found.")
                return []
            
            # Client-side validation just in case, but server should handle it now
            xmatch_battles = [b for b in data if b.get('lobby', {}).get('key') == 'xmatch']
            if len(xmatch_battles) < len(data):
                 logger.warning(f"Server returned {len(data)-len(xmatch_battles)} non-x battles despite filter. Discarding.")
            
            logger.info(f"Fetch complete. Retrieved {len(xmatch_battles)} X Battles.")
            return xmatch_battles
            
        except requests.RequestException as e:
            logger.error(f"Error fetching battles: {e}")
            return []
        


if __name__ == "__main__":
    fetcher = StatInkFetcher()
    # Test fetch
    battles = fetcher.fetch_battles(mode="daily")
    if battles:
        print(f"Sample battle ID: {battles[0].get('uuid')}")
