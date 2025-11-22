# Big Data + Credit API System

> Complete Architecture & Implementation Guide for handling 70M-700M+ records

---

## Project Overview

### Core Objectives

- Ingest 70M-700M+ records from multiple formats
- Normalize and unify data schemas
- Build scalable storage solution
- Create credit-based API system
- Implement authentication & logging

### Data Formats Supported

CSV • JSON/JSONL • XML • Parquet • SQL Dumps • Excel

### Scale Target

- **Phase I**: 70-200M records
- **Phase II**: 300-700M+ records

### Key Challenges

- Multi-schema unification
- Duplicate detection at scale
- Low-latency API responses
- Credit tracking per request
- Horizontal scalability

---

## Technology Stack

### Storage Layer

**Primary: ClickHouse**
- Columnar storage for fast analytics
- Handles 1B+ rows easily
- Low query latency (<100ms)
- Built-in partitioning & sharding

**Alternative: PostgreSQL + Citus**
- For relational needs & ACID compliance

### Processing Engine

**Apache Spark (PySpark)**
- Distributed processing
- Multi-format support
- DataFrame API for transformations
- Direct write to ClickHouse

### API Layer

**FastAPI (Python) + Redis**
- High performance async API
- Automatic OpenAPI docs
- Redis for caching & rate limiting

### Orchestration

**Apache Airflow**
- Schedule ingestion jobs
- Monitor pipelines

### Infrastructure

**AWS / Docker + Kubernetes**
- S3 for raw data lake
- EC2/EKS for compute

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│     INGESTION LAYER                         │
│  Raw Files (S3) → Spark Jobs → Validation  │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│     PROCESSING LAYER                        │
│  Normalization → Deduplication → Mapping    │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│     STORAGE LAYER                           │
│  ClickHouse Cluster (Sharded + Replicated)  │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│     API LAYER                               │
│  FastAPI + Redis → Credit Check → Query    │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│     CLIENT                                  │
│  API Key Auth → JSON Response              │
└─────────────────────────────────────────────┘
```

### Scalability Strategy

- Horizontal sharding by date/region
- Read replicas for API queries
- Redis cluster for caching
- Kubernetes auto-scaling

### Fault Tolerance

- Multi-AZ deployment
- Data replication (3x)
- Circuit breakers in API
- Dead letter queues

---

## Data Ingestion Pipeline

### Master Schema Design

```json
{
  "id": "UUID (generated)",
  "source_file": "original filename",
  "record_hash": "MD5 for deduplication",
  "ingested_at": "timestamp",
  
  "user_id": "string",
  "email": "string",
  "name": "string",
  "phone": "string",
  "address": "string",
  "city": "string",
  "country": "string",
  "created_date": "date",
  "status": "string",
  
  "metadata": "JSON object",
  "data_quality_score": "float",
  "validation_errors": "array"
}
```

### Ingestion Steps

1. **File Discovery**: Scan S3 bucket for new files
2. **Format Detection**: Auto-detect CSV/JSON/XML/Parquet
3. **Schema Inference**: Map fields to master schema
4. **Validation**: Check data types, required fields
5. **Cleansing**: Trim whitespace, normalize formats
6. **Deduplication**: Hash-based duplicate removal
7. **Load**: Batch insert into ClickHouse
8. **Logging**: Record ingestion metrics

### Performance Targets

- **Ingest rate**: 100K+ records/second
- **Spark cluster**: 5-10 worker nodes
- **Batch size**: 1M records per batch
- **Error tolerance**: <0.1% failure rate

---

## API Design

### Endpoints

#### `POST /api/v1/query`
Main data query endpoint with filters

#### `GET /api/v1/credits`
Check remaining credits

#### `GET /api/v1/usage`
View usage history

### Sample Query Request

```http
POST /api/v1/query
Headers:
  X-API-Key: sk_live_abc123xyz

Body:
{
  "filters": {
    "country": "USA",
    "created_date": {
      "gte": "2024-01-01",
      "lte": "2024-12-31"
    },
    "status": ["active", "pending"]
  },
  "fields": ["user_id", "email", "name"],
  "limit": 1000,
  "offset": 0,
  "sort": {
    "field": "created_date",
    "order": "desc"
  }
}
```

### Sample Response

```json
{
  "status": "success",
  "data": [
    {
      "user_id": "usr_123",
      "email": "user@example.com",
      "name": "John Doe"
    }
  ],
  "metadata": {
    "total_records": 25847,
    "returned": 1000,
    "page": 1,
    "credits_used": 10,
    "credits_remaining": 990,
    "query_time_ms": 45
  }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "Insufficient credits. Required: 10, Available: 5"
  }
}
```

---

## Credit Management System

### Credit Calculation Logic

```
Credits per request = BASE_COST (1) + (RECORDS_RETURNED / 100)

Examples:
- 100 records = 2 credits
- 1000 records = 11 credits
- 10000 records = 101 credits
```

### Database Schema

```sql
-- Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  api_key VARCHAR(64) UNIQUE,
  credits_balance INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Credit Transactions Table
CREATE TABLE credit_transactions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  amount INTEGER,
  type ENUM('credit', 'debit'),
  reason VARCHAR(255),
  created_at TIMESTAMP
);

-- API Usage Logs Table
CREATE TABLE api_usage_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  endpoint VARCHAR(255),
  query_params JSONB,
  credits_used INTEGER,
  response_time_ms INTEGER,
  status_code INTEGER,
  created_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_user_api_key ON users(api_key);
CREATE INDEX idx_usage_user_date ON api_usage_logs(user_id, created_at);
```

### Admin Functions

- Add credits to user account
- View user credit balance
- Generate new API keys
- Revoke API keys
- View usage analytics per user
- Set credit expiration dates

---

## Implementation Roadmap

### Phase 1: Infrastructure Setup (Week 1)

- Set up AWS account & S3 buckets
- Deploy ClickHouse cluster (3 nodes)
- Configure Redis cluster
- Set up Spark cluster on EMR/Dataproc

### Phase 2: Ingestion Pipeline (Week 2-3)

- Build Spark ingestion jobs
- Implement schema detection
- Create master schema mapping
- Add deduplication logic
- Test with sample dataset

### Phase 3: API Development (Week 3-4)

- Build FastAPI application
- Implement authentication middleware
- Create query builder
- Add credit deduction logic
- Implement caching layer

### Phase 4: Testing & Optimization (Week 5)

- Load testing (JMeter/Locust)
- Query optimization
- Add monitoring (Grafana/Prometheus)
- Documentation

### Phase 5: Deployment (Week 6)

- Dockerize all services
- Set up Kubernetes manifests
- Configure CI/CD pipeline
- Production deployment

---

## Deployment Strategy

### Docker Compose Setup

```yaml
version: '3.8'
services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - CLICKHOUSE_HOST=clickhouse
      - REDIS_HOST=redis
    depends_on:
      - clickhouse
      - redis
    
  spark-master:
    image: bitnami/spark:latest
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"

volumes:
  clickhouse_data:
```

### AWS Architecture

- **EC2/EKS** for compute
- **S3** for data lake
- **RDS** for user/credit DB
- **ElastiCache** for Redis
- **CloudWatch** for monitoring

### Estimated Costs

| Component | Monthly Cost |
|-----------|-------------|
| Compute   | $500-1000   |
| Storage   | $200-500    |
| Network   | $100-300    |
| **Total** | **$1000-2000** |

### CI/CD Pipeline

```
GitHub Actions → Build Docker → Push to ECR → Deploy to EKS
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Apache Spark
- AWS Account (optional)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bigdata-credit-api.git
   cd bigdata-credit-api
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Run ingestion pipeline**
   ```bash
   python src/ingestion/ingest.py --input s3://bucket/data --format csv
   ```

4. **Start API server**
   ```bash
   cd src/api
   uvicorn main:app --reload
   ```

5. **Access API documentation**
   ```
   http://localhost:8000/docs
   ```

---

## Project Structure

```
/project-root
├── docs/
│   ├── architecture.pdf
│   ├── schema-definition.pdf
│   ├── api-spec.md
│   └── credit-system.md
├── src/
│   ├── ingestion/
│   │   ├── spark_jobs.py
│   │   ├── schema_mapper.py
│   │   └── validators.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── auth.py
│   │   └── models.py
│   └── utils/
│       ├── logging.py
│       └── helpers.py
├── deployment/
│   ├── docker-compose.yml
│   └── kubernetes/
├── tests/
│   ├── test_ingestion.py
│   └── test_api.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Load Testing
```bash
locust -f tests/load/locustfile.py
```

---

## Monitoring

### Metrics Tracked

- API response time
- Credit consumption rate
- Ingestion throughput
- Error rates
- Database query performance

### Tools

- **Prometheus** for metrics collection
- **Grafana** for visualization
- **CloudWatch** for AWS monitoring
- **Sentry** for error tracking

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Team

- **Project Lead**: Your Name
- **Data Engineers**: Team Members
- **Backend Developers**: Team Members
- **DevOps Engineers**: Team Members

---

## Support

For questions or support, please open an issue or contact the team.

---

## Next Steps

1. Set up development environment (Docker, Python, Spark)
2. Start with Phase 1: Infrastructure setup
3. Build ingestion pipeline for CSV format first
4. Test with small dataset before scaling
5. Iterate and expand to other formats
6. Deploy to production with monitoring

---

**Built for handling massive datasets efficiently**