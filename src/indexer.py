from opensearchpy import OpenSearch, helpers
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

INDEX_NAME = "splatoon3-battles"

class SplatoonIndexer:
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False
        )
    
    def delete_index(self):
        """Delete the index if it exists."""
        if self.client.indices.exists(index=INDEX_NAME):
            self.client.indices.delete(index=INDEX_NAME)
            logger.info(f"Deleted index {INDEX_NAME}")
        else:
            logger.info(f"Index {INDEX_NAME} does not exist, skipping delete.")

    def create_index(self):
        """Create index with mapping if it doesn't exist."""
        if not self.client.indices.exists(index=INDEX_NAME):
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "end_at": {"type": "date"},
                        "id": {"type": "keyword"},
                        "result": {"type": "keyword"},
                        "rule_key": {"type": "keyword"},
                        "stage_name": {"type": "keyword"},
                        "weapon_key": {"type": "keyword"},
                        "weapon_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "x_power_after": {"type": "float"},
                        "x_power_before": {"type": "float"},
                        "kill": {"type": "integer"},
                        "assist": {"type": "integer"},
                        "death": {"type": "integer"},
                        "special_count": {"type": "integer"},
                        "inked": {"type": "integer"},
                        
                        # Nested mapping for detailed players
                        "players": {
                            "type": "nested",
                            "properties": {
                                "weapon_key": {"type": "keyword"},
                                "weapon_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                                "kill": {"type": "integer"},
                                "assist": {"type": "integer"},
                                "kill_or_assist": {"type": "integer"},
                                "death": {"type": "integer"},
                                "special": {"type": "integer"},
                                "inked": {"type": "integer"},
                                "is_me": {"type": "boolean"},
                                "team": {"type": "keyword"}
                            }
                        }
                    }
                }
            }
            response = self.client.indices.create(index=INDEX_NAME, body=mapping)
            logger.info(f"Created index {INDEX_NAME}: {response}")
        else:
            logger.info(f"Index {INDEX_NAME} already exists.")

    def index_battles(self, battles: List[Dict]):
        """Bulk index battles."""
        if not battles:
            logger.info("No battles to index.")
            return

        actions = []
        for battle in battles:
            action = {
                "_index": INDEX_NAME,
                "_id": battle["id"], # key by UUID to prevent duplicates
                "_source": battle
            }
            actions.append(action)

        success, failed = helpers.bulk(self.client, actions)
        logger.info(f"Indexed {success} documents. Failed: {failed}")

if __name__ == "__main__":
    # Test connection
    indexer = SplatoonIndexer()
    indexer.create_index()
