"""
QUICK REFERENCE - CRYPTO SYSTEM
===============================

## 🚀 Get Started in 3 Steps

### Step 1: Configure
```bash
cd crypto-system
cp .env.example .env
# Edit .env and add your API keys
```

### Step 2: Deploy
```bash
docker-compose up -d
```

### Step 3: Verify
```bash
curl http://localhost:8000/health
```

---

## 📊 API Keys Needed

Visit these sites and generate API keys:

1. **CoinGecko** (Free tier available)
   - https://www.coingecko.com/en/api
   - Free tier: 10-50 calls/min
   - Set COINGECKO_API_KEY in .env

2. **CoinMarketCap** (Requires credit card)
   - https://coinmarketcap.com/api/
   - Basic tier: Sufficient for this setup
   - Set CMC_API_KEY in .env
   - Set CMC_DEX_API_KEY in .env (same API)

---

## 🎯 Current Rate Limits

| API | Config | Limit | Safety Margin |
|-----|--------|-------|----------------|
| CoinGecko | 15/min | 30/min | 50% |
| CoinMarketCap | 15/min | 30/min | 50% |
| CMC DEX | 50/min | 300/min | 83% |

**These are conservative. Adjust in .env if your API tier allows.**

---

## 📅 Scheduled Jobs (Run Automatically)

```
Every 60s  → Fetch current prices
Every 5m   → Update market sentiment
Every 2m   → Fetch DEX trading pairs
Every 1h   → Refresh cryptocurrency metadata
Every 2h   → Update exchange information
```

Customize intervals in .env:
```env
PRICE_UPDATE_INTERVAL=60
SENTIMENT_UPDATE_INTERVAL=300
DEX_UPDATE_INTERVAL=120
METADATA_UPDATE_INTERVAL=3600
EXCHANGE_UPDATE_INTERVAL=7200
```

---

## 🔍 Monitor the Service

### Health Check
```bash
curl http://localhost:8000/health
```

### Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

### View Logs
```bash
docker-compose logs -f crypto-system
```

### Watch Database
```bash
docker-compose exec postgres psql -U crypto_user -d crypto_market
# SELECT * FROM cryptocurrencies LIMIT 5;
# SELECT * FROM price_history ORDER BY created_at DESC LIMIT 10;
```

---

## ⚙️ Configuration Checklist

### Required
- [ ] CoinGecko API Key
- [ ] CoinMarketCap API Key
- [ ] PostgreSQL running at localhost:5432

### Optional (Tune Later)
- [ ] Adjust rate limits based on API tier
- [ ] Change update intervals
- [ ] Enable/disable specific APIs
- [ ] Configure database credentials

### Security
- [ ] .env file NOT committed to git
- [ ] .gitignore includes .env
- [ ] API keys rotated periodically
- [ ] Logs don't expose sensitive data

---

## 🛠️ Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f crypto-system
```

### Restart Service
```bash
docker-compose restart crypto-system
```

### Execute Commands in Container
```bash
docker-compose exec crypto-system python -c "from config.settings import get_settings; print(get_settings().get_masked_settings())"
```

### Access Database
```bash
docker-compose exec postgres psql -U crypto_user -d crypto_market
```

### Rebuild Container
```bash
docker-compose build --no-cache
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs crypto-system

# Check environment variables
docker-compose exec crypto-system env | grep API

# Verify database connection
docker-compose logs postgres
```

### High error rates
```bash
# Check if APIs are accessible
curl https://api.coingecko.com/api/v3/ping

# Check rate limit headers in logs
docker-compose logs crypto-system | grep "rate_limit"

# Verify API keys are correct
# Check your API provider dashboard for quota/limits
```

### Database issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U crypto_user -d crypto_market

# View database logs
docker-compose logs postgres

# Check disk space
docker system df
```

---

## 📊 Data Collected

### Cryptocurrencies Table
- symbol, name, description
- created_at, updated_at

### Exchanges Table
- name, country, website
- established_year, trading_volume_usd

### Trading Pairs Table
- exchange_id, crypto_id
- base_currency, quote_currency
- is_active status

### Price History Table
- trading_pair_id
- open, high, low, close prices
- volume, recorded_at

### Market Sentiment Table
- crypto_id
- sentiment_score (-1.0 to 1.0)
- sentiment_label, mentions_count

### Market Events Table
- crypto_id
- event_type, title, description
- impact_level, event_date

---

## 🚨 Important Notes

1. **API Keys**: Never commit .env to version control
2. **Rate Limits**: Start conservative, monitor, then adjust
3. **Database**: Backup regularly in production
4. **Logs**: Check logs for errors/warnings
5. **Metrics**: Monitor Prometheus metrics for performance

---

## 📞 Support Resources

- CoinGecko Docs: https://www.coingecko.com/en/api/documentation
- CoinMarketCap Docs: https://coinmarketcap.com/api/documentation/v1/
- CMC DEX Docs: https://coinmarketcap.com/api/documentation/v1-dex/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Docker Docs: https://docs.docker.com/

---

## 📝 Environment Variables Reference

```env
# API Keys (REQUIRED)
COINGECKO_API_KEY=xxx
CMC_API_KEY=xxx
CMC_DEX_API_KEY=xxx

# Rate Limits (calls per minute)
COINGECKO_RATE_LIMIT=15
CMC_RATE_LIMIT=15
CMC_DEX_RATE_LIMIT=50

# Update Intervals (seconds)
PRICE_UPDATE_INTERVAL=60
METADATA_UPDATE_INTERVAL=3600
SENTIMENT_UPDATE_INTERVAL=300
DEX_UPDATE_INTERVAL=120
EXCHANGE_UPDATE_INTERVAL=7200

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=crypto_market
DB_USER=crypto_user
DB_PASSWORD=crypto_pass

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/crypto-system.log

# Features
ENABLE_COINGECKO=true
ENABLE_CMC=true
ENABLE_CMC_DEX=true
ENABLE_SENTIMENT_ANALYSIS=true

# Performance
BATCH_SIZE=250
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

---

**Version**: 1.0  
**Created**: October 2025  
**Status**: Production Ready ✅
"""

# This file is informational quick reference
