# Crypto Market Data Extraction & Orchestration System

A containerized Python service that extracts cryptocurrency market data from multiple APIs (CoinGecko, CoinMarketCap, CoinMarketCap DEX) and stores it in a PostgreSQL database.

## Features

- **Multi-API Integration**: CoinGecko, CoinMarketCap, and CoinMarketCap DEX
- **Rate Limiting**: Configurable rate limits per API (15/15/50 calls/min)
- **Async Processing**: Efficient async/await pattern for concurrent requests
- **Robust Error Handling**: Retry logic, exponential backoff, and circuit breaker patterns
- **Database Management**: SQLAlchemy ORM with alembic migrations
- **Monitoring**: Prometheus metrics and health check endpoint
- **Logging**: Structured logging with rotation
- **Docker Deployment**: Full containerization with docker-compose

## Project Structure

```
crypto-system/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration management
├── extractors/
│   ├── __init__.py
│   ├── base_service.py          # Base API service class
│   ├── coingecko_service.py     # CoinGecko API client
│   ├── cmc_service.py           # CoinMarketCap API client
│   └── cmc_dex_service.py       # CoinMarketCap DEX API client
├── database/
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy ORM models
│   ├── connection.py            # Database connection management
│   └── repository.py            # Data access layer
├── orchestration/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── scheduler.py             # APScheduler orchestration
│   ├── coordinator.py           # Coordination logic
│   └── pipeline.py              # Data processing pipeline
├── transformers/
│   ├── __init__.py
│   ├── price_transformer.py     # Price data transformation
│   ├── metadata_transformer.py  # Metadata transformation
│   └── sentiment_transformer.py # Sentiment data transformation
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py               # Prometheus metrics
│   ├── health.py                # Health check endpoint
│   └── logger.py                # Structured logging
├── utils/
│   ├── __init__.py
│   ├── cache.py                 # Caching utilities
│   ├── validators.py            # Data validation
│   └── helpers.py               # Helper functions
├── migrations/                  # Alembic database migrations
├── logs/                        # Application logs (generated at runtime)
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Docker compose configuration
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- API Keys for:
  - CoinGecko (https://www.coingecko.com/en/api)
  - CoinMarketCap (https://coinmarketcap.com/api/)
  - CoinMarketCap DEX (included with CMC API subscription)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd crypto-system
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Add your API keys to `.env`:**
   ```bash
   # Edit .env and add your API keys
   COINGECKO_API_KEY=your_key_here
   CMC_API_KEY=your_key_here
   CMC_DEX_API_KEY=your_key_here
   ```

4. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

5. **Check service status:**
   ```bash
   docker-compose logs -f crypto-system
   ```

## Usage

### API Keys Management

**IMPORTANT: API key security**

- Never commit `.env` file to version control
- Use `.env.example` as a template
- Rotate keys periodically
- Monitor API usage in the health check endpoint

### Configuration

Edit `.env` to customize:

```env
# Rate limits (calls per minute)
COINGECKO_RATE_LIMIT=15
CMC_RATE_LIMIT=15
CMC_DEX_RATE_LIMIT=50

# Update intervals (seconds)
PRICE_UPDATE_INTERVAL=60
METADATA_UPDATE_INTERVAL=3600
SENTIMENT_UPDATE_INTERVAL=300
DEX_UPDATE_INTERVAL=120

# Feature flags
ENABLE_COINGECKO=true
ENABLE_CMC=true
ENABLE_CMC_DEX=true
```

### Monitoring

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Metrics:**
```bash
curl http://localhost:8000/metrics
```

**View Logs:**
```bash
docker-compose logs -f crypto-system
```

## API Limits and Scheduling

### Current Rate Limits

| API | Calls/Min | Use Case |
|-----|-----------|----------|
| CoinGecko | 15 | Cryptocurrency data, exchanges, market data |
| CoinMarketCap | 15 | Latest quotes, OHLCV data, exchange info |
| CMC DEX | 50 | DEX pairs, cross-chain data |

### Scheduled Tasks

| Task | Interval | API | Purpose |
|------|----------|-----|---------|
| Price Updates | 60s | All | Latest OHLCV and market prices |
| Metadata Refresh | 1h | CoinGecko | Coin metadata and descriptions |
| Sentiment Analysis | 5min | CoinGecko | Market sentiment and trending |
| DEX Pairs Update | 2min | CMC DEX | Decentralized exchange data |
| Exchange Info | 2h | CoinGecko | Exchange data and volumes |

## Database

The service automatically initializes the PostgreSQL database using the init scripts from `../Databases/crypto-market-db/`.

**Connection Details:**
- Host: `postgres` (in container), `localhost` (local)
- Port: 5432
- Database: `crypto_market`
- User: `crypto_user`
- Password: `crypto_pass`

## Error Handling

The system includes:

- **Exponential Backoff**: Automatic retry with increasing delays
- **Circuit Breaker**: Prevents cascading failures
- **Rate Limit Handling**: Respects API 429 responses
- **Connection Pooling**: Efficient database connections
- **Graceful Degradation**: Continues with partial data if one API fails

## Development

### Running Locally (without Docker)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the service:
   ```bash
   python -m orchestration.main
   ```

### Running Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Troubleshooting

### Service won't start

1. Check environment variables are set: `docker-compose config`
2. Verify database connectivity: `docker-compose exec postgres pg_isready`
3. Review logs: `docker-compose logs crypto-system`

### High API error rates

1. Check rate limits in `.env`
2. Verify API keys are correct
3. Review API quota in provider dashboards
4. Check network connectivity

### Database connection issues

1. Ensure PostgreSQL is running: `docker-compose ps`
2. Verify credentials in `.env` match database setup
3. Check database logs: `docker-compose logs postgres`

## Performance Tuning

- Adjust `BATCH_SIZE` for database inserts
- Tune rate limits based on API tier
- Configure `PRICE_UPDATE_INTERVAL` for real-time vs background updates
- Use database indices for common queries

## License

[Your License Here]

## Support

For issues and questions, see the main project documentation.
