import argparse
import logging
from fetcher import StatInkFetcher
from transformer import flatten_battles
from indexer import SplatoonIndexer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Splatoon 3 Stats Extractor")
    parser.add_argument("--mode", choices=["daily", "backfill"], default="daily", help="Fetch mode")

    parser.add_argument("--username", required=True, help="Stat.ink username (e.g. so9137)")
    parser.add_argument("--days", type=int, default=0, help="Number of days to backfill (uses API date filtering)")
    parser.add_argument("--host", default="localhost", help="OpenSearch host")
    parser.add_argument("--purge", action="store_true", help="Delete existing index before running")
    
    args = parser.parse_args()
    
    # Create fetcher and fetch data
    fetcher = StatInkFetcher(username=args.username)
    indexer = SplatoonIndexer(host=args.host)
    
    # 2. Prepare Index
    if args.purge:
        logger.info("Purging old index...")
        indexer.delete_index()

    try:
        indexer.create_index()
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch or create index: {e}")
        return

    # 3. Fetch
    logger.info(f"Starting job in {args.mode} mode...")
    battles = fetcher.fetch_battles(mode=args.mode, days=args.days)
    
    if not battles:
        logger.info("No battles found.")
        return

    # 4. Transform
    logger.info("wd...")
    flat_battles = flatten_battles(battles)
    
    # 5. Index
    logger.info("Indexing...")
    indexer.index_battles(flat_battles)
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
