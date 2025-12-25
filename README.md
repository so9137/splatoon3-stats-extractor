# Splatoon 3 Stats Extractor

This project automates the process of fetching your Splatoon 3 X Battle data from [stat.ink](https://stat.ink), transforming it into an analysis-friendly format, and indexing it into a local OpenSearch instance for visualization.

## Features

- **X Battle Only**: Strictly filters and processes only X Battles.
- **Detailed Player Stats**: detailed statistics (kills, deaths, weapon, special, etc.) for all 8 players in every match.
- **Efficient Fetching**: Uses single-request timestamp-based filtering to minimize API load.
- **Backfill & Daily Modes**: Easily backfill historical data (last 3 weeks) or fetch the latest daily battles.
- **OpenSearch Integration**: Ready-to-use Docker Compose setup for OpenSearch and OpenSearch Dashboards.

## Prerequisites

- **Docker** & **Docker Compose**
- **Python 3.10+**
- **Poetry** (Python dependency manager)

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd splatoon3-stats-extractor
    ```

2.  **Install Dependencies**:
    ```bash
    poetry install
    ```

3.  **Start OpenSearch**:
    ```bash
    docker-compose up -d
    ```
    - OpenSearch will be available at `http://localhost:9200`.
    - OpenSearch Dashboards will be available at `http://localhost:5601`.
    - *Note: Data is persisted in the `opensearch-data` Docker volume.*

4.  **Manage OpenSearch**:
    - **Stop**: `docker-compose down`
    - **Restart**: `docker-compose restart`
    - **View Logs**: `docker-compose logs -f`

## Usage

Run the script using `poetry run python src/main.py`.

### 1. Backfill History (Recommended First Run)
Fetch the last 3 weeks (max limit) of X Battles.
```bash
poetry run python src/main.py --mode backfill --days 21 --username <YOUR_STAT_INK_USERNAME> --purge
```
*The `--purge` flag clears the existing index before ingestion, useful for a clean start.*

### 2. Daily Update
Fetch the last 24 hours of data.
```bash
poetry run python src/main.py --mode daily --username <YOUR_STAT_INK_USERNAME>
```

### 3. Arguments
| Argument | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `--username` | Your stat.ink username (e.g. `so9137`) | Yes | - |
| `--mode` | `daily` (24h) or `backfill` (history) | No | `daily` |
| `--days` | Number of past days to fetch (max 21). Only for `backfill`. | No | `0` (defaults to 21) |
| `--purge` | Delete existing index before running. | No | False |
| `--host` | OpenSearch host URL. | No | `localhost` |

## Visualizing Data

1.  Open **OpenSearch Dashboards** at [http://localhost:5601](http://localhost:5601).
2.  Go to **Stack Management > Index Patterns**.
3.  Create a new index pattern for `splatoon3-battles*`.
4.  Select `end_at` as the primary time field.
5.  Go to **Discover** to explore your data!

## Data Schema

The `players` field is a **nested** object containing stats for all participants.
```json
"players": [
  {
    "weapon_name": "Splattershot",
    "kill": 12,
    "death": 5,
    "special": 2,
    "is_me": true,
    "team": "my",
    ...
  },
  ...
]
```
This allows for complex queries, such as "Win rate when ally uses Weapon X".