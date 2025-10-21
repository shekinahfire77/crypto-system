"""
CRYPTO SYSTEM SETUP GUIDE
========================

This document provides step-by-step instructions for setting up and deploying 
the Crypto Market Data Extraction & Orchestration System.

## Quick Start

### 1. Clone Configuration
```bash
cd crypto-system
cp .env.example .env
```

### 2. Add Your API Keys (IMPORTANT - DO NOT COMMIT!)

Edit `.env` with your API keys:

```env
# CoinGecko API
COINGECKO_API_KEY=your_coingecko_api_key_here

# CoinMarketCap API
CMC_API_KEY=your_cmc_api_key_here

# CoinMarketCap DEX API
CMC_DEX_API_KEY=your_cmc_dex_api_key_here
```

**API Key Security:**
- Never commit .env file
- Rotate keys regularly
- Use environment-specific keys when possible
- Monitor API usage in provider dashboards

### 3. Verify Prerequisites

```bash
# Check Docker is installed
docker --version

# Check Docker Compose is installed
docker-compose --version

# Verify Python (if running locally)
python --version  # Python 3.11+
```

### 4. Build and Deploy

```bash
# Build the container
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f crypto-system

# Check status
docker-compose ps
```

### 5. Verify Installation

```bash
# Health check endpoint
curl http://localhost:8000/health

# Metrics endpoint
curl http://localhost:8000/metrics

# Database connectivity
docker-compose exec postgres pg_isready -U crypto_user -d crypto_market
```

## Rate Limits Configuration

Current settings in `.env`:

```env
COINGECKO_RATE_LIMIT=15          # 15 calls/min (conservative)
CMC_RATE_LIMIT=15                # 15 calls/min (conservative)
CMC_DEX_RATE_LIMIT=50            # 50 calls/min (efficient)
```

**Adjusting Rate Limits:**
- Start conservative and monitor API responses
- 429 responses indicate rate limit exceeded
- Check logs for rate limit warnings
- Adjust based on API tier and available credits

## Scheduled Jobs

Jobs run automatically on intervals:

| Job | Interval | API | Purpose |
|-----|----------|-----|---------|
| Price Update | 60s | CoinGecko/CMC | Get latest prices |
| Metadata | 1h | CoinGecko | Update coin data |
| Sentiment | 5min | CoinGecko | Market sentiment |
| DEX Pairs | 2min | CMC DEX | DEX trading data |
| Exchanges | 2h | CoinGecko | Exchange info |

**Custom Intervals:**
Edit in `.env`:
```env
PRICE_UPDATE_INTERVAL=60
METADATA_UPDATE_INTERVAL=3600
SENTIMENT_UPDATE_INTERVAL=300
DEX_UPDATE_INTERVAL=120
EXCHANGE_UPDATE_INTERVAL=7200
```

## API Feature Flags

Enable/disable APIs in `.env`:

```env
ENABLE_COINGECKO=true         # Centralized exchange data
ENABLE_CMC=true               # Market quotes and historical data
ENABLE_CMC_DEX=true           # Decentralized exchange data
ENABLE_SENTIMENT_ANALYSIS=true # Market sentiment tracking
```

## Local Development

### Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and local DB connection

# Start PostgreSQL (separate terminal)
# Ensure database is running at localhost:5432

# Run the service
python -m orchestration.main
```

### Database Initialization

The database initializes automatically using scripts from `../Databases/crypto-market-db/`:

```bash
# Manual init (if needed)
docker-compose exec postgres psql -U crypto_user -d crypto_market < ../Databases/crypto-market-db/init.sql
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response includes:
- Service status (healthy/degraded/unhealthy)
- Database connectivity
- API availability
- Uptime

### Metrics

Prometheus metrics available at `http://localhost:8000/metrics`:

```bash
# View in browser
open http://localhost:8000/metrics

# Parse specific metric
curl http://localhost:8000/metrics | grep crypto_api_requests_total
```

Key metrics:
- `crypto_api_requests_total` - Total API requests
- `crypto_db_operations_total` - Database operations
- `crypto_records_processed_total` - Records processed
- `crypto_service_uptime_seconds` - Service uptime

### Logs

```bash
# View live logs
docker-compose logs -f crypto-system

# View with filter
docker-compose logs -f crypto-system | grep "ERROR"

# View last N lines
docker-compose logs --tail=100 crypto-system
```

## Troubleshooting

### Service won't start

```bash
# Check Docker daemon
docker ps

# Review environment variables
docker-compose config

# Check logs
docker-compose logs crypto-system

# Verify API keys are set
docker-compose exec crypto-system env | grep API_KEY
```

### High error rates

```bash
# Check rate limits
docker-compose logs crypto-system | grep "rate_limit"

# Verify API keys are valid
# Visit: https://www.coingecko.com/en/api
# Visit: https://coinmarketcap.com/api/

# Check network connectivity
docker-compose exec crypto-system curl -I https://api.coingecko.com/api/v3/ping
```

### Database connection issues

```bash
# Test database connection
docker-compose exec postgres pg_isready -U crypto_user -d crypto_market

# Check database logs
docker-compose logs postgres

# Manual connection test
docker-compose exec postgres psql -U crypto_user -d crypto_market -c "SELECT 1;"
```

### Out of memory

Increase Docker resource limits in docker-compose.yml:
```yaml
services:
  crypto-system:
    deploy:
      resources:
        limits:
          memory: 2G
```

## Performance Tuning

### Batch Size

Increase batch size for faster database inserts:
```env
BATCH_SIZE=500  # Default: 250
```

### Connection Pool

Tune database connection pool:
```env
DB_POOL_SIZE=20       # Default: 10
DB_MAX_OVERFLOW=40    # Default: 20
```

### Cache TTL

Adjust cache time-to-live:
```python
# In code - set different TTLs for different data types
CACHE_TTL_PRICES=300      # 5 minutes
CACHE_TTL_METADATA=3600   # 1 hour
```

## Production Deployment

### Environment Setup

```bash
# Use production .env
cp .env.example .env.prod
# Edit with production values

export ENV_FILE=.env.prod
docker-compose --env-file $ENV_FILE up -d
```

### SSL/TLS

Add reverse proxy (nginx/traefik) in front of the service for HTTPS.

### Backups

```bash
# Backup database
docker-compose exec postgres pg_dump -U crypto_user crypto_market > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U crypto_user crypto_market < backup.sql
```

### Scaling

For horizontal scaling, consider:
- Deploying multiple instances with load balancer
- Using message queue (Redis/RabbitMQ) for job distribution
- Implementing dedicated database read replicas

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify configuration in `.env`
3. Test API connectivity manually
4. Check API documentation:
   - CoinGecko: https://www.coingecko.com/en/api/documentation
   - CoinMarketCap: https://coinmarketcap.com/api/documentation/v1/
   - CoinMarketCap DEX: https://coinmarketcap.com/api/documentation/v1-dex/

## Security Checklist

- [ ] API keys stored in .env (not committed)
- [ ] .env added to .gitignore
- [ ] Database password changed from default
- [ ] HTTPS/TLS enabled in production
- [ ] Rate limits appropriate for API tier
- [ ] Logs don't contain sensitive data
- [ ] Regular database backups scheduled
- [ ] API keys rotated periodically

---

Version: 1.0
Last Updated: October 2025
"""

# This file is informational and contains setup instructions
