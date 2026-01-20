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

---

# Splatoon 3 Stats Extractor (日本語)

このプロジェクトは、[stat.ink](https://stat.ink) から Splatoon 3 の X マッチのデータを自動的に取得し、分析しやすい形式に変換して、可視化のためにローカルの OpenSearch インスタンスにインデックスするプロセスを自動化します。

## 機能

- **X マッチのみ**: 厳密に X マッチのみをフィルタリングして処理します。
- **詳細なプレイヤー統計**: 全試合の全8プレイヤーの詳細な統計（キル、デス、ブキ、スペシャルなど）を取得します。
- **効率的な取得**: API負荷を最小限に抑えるために、単一リクエストのタイムスタンプベースのフィルタリングを使用します。
- **バックフィル＆デイリーモード**: 過去のデータ（直近3週間）を簡単にバックフィルしたり、最新の日次バトルを取得したりできます。
- **OpenSearch 統合**: OpenSearch および OpenSearch Dashboards 用のすぐに使える Docker Compose セットアップ。

## 前提条件

- **Docker** & **Docker Compose**
- **Python 3.10+**
- **Poetry** (Python 依存関係マネージャー)

## セットアップ

1.  **リポジトリのクローン**:
    ```bash
    git clone <repository-url>
    cd splatoon3-stats-extractor
    ```

2.  **依存関係のインストール**:
    ```bash
    poetry install
    ```

3.  **OpenSearch の起動**:
    ```bash
    docker-compose up -d
    ```
    - OpenSearch は `http://localhost:9200` で利用可能です。
    - OpenSearch Dashboards は `http://localhost:5601` で利用可能です。
    - *注: データは `opensearch-data` Docker ボリュームに永続化されます。*

4.  **OpenSearch の管理**:
    - **停止**: `docker-compose down`
    - **再起動**: `docker-compose restart`
    - **ログ表示**: `docker-compose logs -f`

## 使い方

`poetry run python src/main.py` を使用してスクリプトを実行します。

### 1. 履歴のバックフィル（初回実行時に推奨）
過去3週間（最大制限）の X マッチを取得します。
```bash
poetry run python src/main.py --mode backfill --days 21 --username <YOUR_STAT_INK_USERNAME> --purge
```
*`--purge` フラグは取り込み前に既存のインデックスをクリアします。クリーンスタートに便利です。*

### 2. 日次更新
過去24時間のデータを取得します。
```bash
poetry run python src/main.py --mode daily --username <YOUR_STAT_INK_USERNAME>
```

### 3. 引数
| 引数 | 説明 | 必須 | デフォルト |
| :--- | :--- | :--- | :--- |
| `--username` | stat.ink のユーザー名 (例: `so9137`) | はい | - |
| `--mode` | `daily` (24h) または `backfill` (履歴) | いいえ | `daily` |
| `--days` | 取得する過去の日数 (最大 21)。`backfill` モードのみ。 | いいえ | `0` (デフォルトは 21) |
| `--purge` | 実行前に既存のインデックスを削除する。 | いいえ | False |
| `--host` | OpenSearch のホスト URL。 | いいえ | `localhost` |

## データの可視化

1.  [http://localhost:5601](http://localhost:5601) で **OpenSearch Dashboards** を開きます。
2.  **Stack Management > Index Patterns** に移動します。
3.  `splatoon3-battles*` の新しいインデックスパターンを作成します。
4.  プライマリ時間フィールドとして `end_at` を選択します。
5.  **Discover** に移動してデータを探索しましょう！

## データスキーマ

`players` フィールドは、全参加者の統計を含む**ネストされた**オブジェクトです。
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
これにより、「味方がブキXを使用しているときの勝率」のような複雑なクエリが可能になります。