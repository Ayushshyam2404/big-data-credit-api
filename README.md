Unified Big Data Ingestion & Credit-Regulated API System
Overview

This project is a streamlined Big Data system that can ingest very large datasets (700M+ records), store them efficiently, and expose them through a secure, credit-based API.

It’s designed for speed, reliability, and simplicity — from ingestion to querying to credit deduction.

Key Features
Big Data Ingestion

A Python-based ETL pipeline that can read CSV/JSON files, clean them, normalize the data, and load everything into a high-performance database.

Fast Analytical Storage

ClickHouse is used as the main database because it's extremely fast for analytical workloads and can return results from millions of rows in milliseconds.

Credit-Based API Access

Each API request deducts credits using Redis atomic counters.
This ensures accurate, race-condition-free credit tracking even under heavy load.

Secure API Layer

The API includes:

API key authentication

Rate limiting

Credit-based access control

Containerized Deployment

The entire system (API, Redis, ClickHouse) runs using Docker and Docker Compose, making it easy to deploy anywhere.

| Component      | Technology      | Reason                                                     |
| -------------- | --------------- | ---------------------------------------------------------- |
| API Layer      | FastAPI         | Modern, fast, asynchronous, auto-generates docs.           |
| ETL/Processing | Python + Pandas | Reliable for data cleaning and transformation.             |
| Storage        | ClickHouse      | Columnar OLAP DB built for huge datasets and fast queries. |
| Cache/Credits  | Redis           | In-memory store for atomic operations and rate limiting.   |
| Infrastructure | Docker          | Simplifies deployment and environment consistency.         |

/project-root
├── docker-compose.yml      # Docker setup for API, Redis, ClickHouse
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
└── src
    ├── api
    │   └── main.py         # FastAPI application + credit logic
    └── ingestion
        └── etl.py          # ETL ingestion and data normalization


How to Run
1. Prerequisites
Docker Desktop installed and running.
2. Start the System
code
Bash
docker-compose up --build
Wait until you see Connected to ClickHouse! in the terminal.
3. Ingest Data
Open a new terminal window and run:
code
Bash
docker-compose exec app python src/ingestion/etl.py
4. Access the API
Open your browser to: http://localhost:8000/docs

PI Usage Guide
Step 1: Create a User (Get API Key)
Endpoint: POST /create_user
Input: {"username": "admin", "credits": 100}
Response: Returns a unique api_key.
Step 2: Query Data (Costs 1 Credit)
Endpoint: GET /get_data
Headers: api_key: <YOUR_KEY>
Query: country=USA
Logic:
Checks Redis for remaining credits.
If credits > 0, deducts 1 credit atomically.
Queries ClickHouse for records.
Returns Data + Remaining Credits.


Scalability & Performance
Horizontal Scaling: The ClickHouse cluster can be sharded across multiple nodes to handle TBs of data.
Concurrency: Redis handles thousands of credit checks per second without race conditions.
Ingestion: The ETL script can be upgraded to Apache Spark for distributed processing of files >10GB.
