"""
DEPLOYMENT CHECKLIST & NEXT STEPS
==================================

## ✅ Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] At least 2GB free disk space
- [ ] Port 5432 available (PostgreSQL)
- [ ] Port 8000 available (Metrics/Health)

### API Keys (You'll provide these)
- [ ] CoinGecko API key obtained
- [ ] CoinMarketCap API key obtained
- [ ] CMC DEX API key obtained (same as CMC)

### Environment Setup
- [ ] Create .env from .env.example
- [ ] Add all three API keys to .env
- [ ] Verify database credentials match existing DB
- [ ] Review rate limits (default: 15/15/50)

### Security
- [ ] .env is in .gitignore ✅ (already done)
- [ ] .env is NOT committed to git
- [ ] API keys are valid
- [ ] Database password is appropriate for environment

---

## 🚀 Quick Start (After Setup Above)

```bash
# 1. Navigate to project
cd c:\Users\deadm\Desktop\crypto-system

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Deploy
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health

# 5. Monitor
docker-compose logs -f crypto-system
```

---

## 📋 Step-by-Step Deployment

### Step 1: Get API Keys (5-10 minutes)

**CoinGecko Free API:**
1. Visit: https://www.coingecko.com/en/api
2. Sign up (free)
3. Get API key from dashboard
4. Copy to notepad

**CoinMarketCap API:**
1. Visit: https://coinmarketcap.com/api/
2. Sign up (requires credit card, but free tier available)
3. Create new API key
4. Copy to notepad

**CoinMarketCap DEX API:**
- Same as CoinMarketCap API key (included in Pro API)

### Step 2: Configure Environment (2 minutes)

```bash
cd c:\Users\deadm\Desktop\crypto-system
cp .env.example .env
```

Edit .env with your API keys:
```env
COINGECKO_API_KEY=your_key_here
CMC_API_KEY=your_key_here
CMC_DEX_API_KEY=your_key_here
```

Optional: Adjust rate limits if needed
```env
COINGECKO_RATE_LIMIT=15    # Max 30, we use 15 for safety
CMC_RATE_LIMIT=15          # Max 30, we use 15 for safety
CMC_DEX_RATE_LIMIT=50      # Max 300, we use 50 for safety
```

### Step 3: Deploy (2-5 minutes)

```bash
# Build and start containers
docker-compose up -d

# Wait 30-60 seconds for startup
# Check status
docker-compose ps

# View logs
docker-compose logs -f crypto-system

# Wait until you see "service_started" message
```

### Step 4: Verify (1 minute)

```bash
# Health check
curl http://localhost:8000/health

# You should see JSON response like:
# {"status":"healthy", "uptime_seconds":60, ...}

# Metrics endpoint
curl http://localhost:8000/metrics

# Database connectivity
docker-compose exec postgres pg_isready -U crypto_user -d crypto_market
```

### Step 5: Monitor (ongoing)

```bash
# Watch logs in real-time
docker-compose logs -f crypto-system

# Look for:
# - "price_fetch_success" → Data being collected
# - "storing_price" → Data being stored
# - No "ERROR" messages

# Check database has data
docker-compose exec postgres psql -U crypto_user -d crypto_market -c "SELECT COUNT(*) FROM cryptocurrencies;"
```

---

## 🔍 Verification Points

After deployment, verify each component:

### 1. Service is Running
```bash
docker-compose ps
# crypto-system should show "Up"
# postgres should show "Up"
```

### 2. API Keys are Working
```bash
docker-compose logs crypto-system | grep -i "rate_limit"
# Should NOT show many errors
```

### 3. Database Connected
```bash
curl http://localhost:8000/health
# database.status should be "ok"
```

### 4. Data is Being Collected
```bash
docker-compose exec postgres psql -U crypto_user -d crypto_market

psql> SELECT COUNT(*) FROM cryptocurrencies;
# Should return > 0

psql> SELECT COUNT(*) FROM price_history;
# Should increase over time

psql> SELECT * FROM price_history ORDER BY created_at DESC LIMIT 1;
# Should show recent data
```

### 5. Metrics Available
```bash
curl http://localhost:8000/metrics | head -20
# Should show Prometheus metrics
```

---

## 📊 Expected Behavior

### First 60 Seconds
- Service starts
- API clients initialize
- Scheduler jobs scheduled
- First price update runs

### First 5 Minutes
- Price data: ~5,000+ records
- Exchange data: ~100 records
- Sentiment data: ~50 records (trending only)

### First Hour
- Metadata refresh: 10,000+ coins
- Continued price updates
- Multiple sentiment updates
- Database growing

### First 24 Hours
- Historical data accumulation
- Multiple job cycles
- Millions of price records
- Complete market snapshot

---

## 🛑 If Something Goes Wrong

### Service Won't Start
```bash
# Check logs
docker-compose logs crypto-system

# Common issues:
# 1. Missing API keys in .env
# 2. Database not accessible
# 3. Port 5432 already in use

# Fix and retry
docker-compose restart crypto-system
```

### High Error Rates
```bash
# View errors
docker-compose logs crypto-system | grep ERROR

# Check rate limits
docker-compose logs crypto-system | grep rate_limit

# Verify API keys are valid
# Visit API provider dashboards

# Reduce rate limits if needed
COINGECKO_RATE_LIMIT=10
CMC_RATE_LIMIT=10
CMC_DEX_RATE_LIMIT=30
```

### No Data Being Stored
```bash
# Check jobs are running
docker-compose logs crypto-system | grep "fetching_"

# Check database connection
docker-compose logs crypto-system | grep "database"

# Manually test database
docker-compose exec postgres psql -U crypto_user -d crypto_market -c "SELECT 1;"
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Check credentials in .env
grep DB_ c:\Users\deadm\Desktop\crypto-system\.env

# Test connection
docker-compose exec postgres pg_isready -U crypto_user -d crypto_market
```

---

## 📈 Performance Monitoring

### Monitor CPU/Memory
```bash
# Real-time stats
docker stats

# Watch crypto-system resource usage
# Should be < 500MB RAM, < 10% CPU at rest
```

### Monitor API Usage
```bash
# View API request metrics
curl http://localhost:8000/metrics | grep api_requests_total
```

### Monitor Database
```bash
# Connection count
docker-compose exec postgres psql -U crypto_user -d crypto_market -c "SELECT count(*) FROM pg_stat_activity;"

# Table sizes
docker-compose exec postgres psql -U crypto_user -d crypto_market -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

---

## 🔄 Maintenance Tasks

### Daily
- [ ] Check logs for errors
- [ ] Verify data is being collected
- [ ] Monitor disk space

### Weekly
- [ ] Review metrics
- [ ] Check API quota usage
- [ ] Backup database (if production)

### Monthly
- [ ] Rotate API keys (recommended)
- [ ] Clean old logs
- [ ] Review and adjust rate limits if needed

---

## 🎯 Next Steps After Deployment

1. **Let It Run** (24-48 hours)
   - Collect baseline data
   - Verify all systems working
   - Monitor for issues

2. **Tune Rate Limits**
   - Monitor API usage
   - Increase if quota available
   - Decrease if hitting limits

3. **Customize Schedule**
   - Adjust update intervals if needed
   - Enable/disable APIs as required
   - Test different schedules

4. **Set Up Backups** (production)
   - Database backups
   - Log rotation
   - Metrics retention

5. **Integrate with Other Systems**
   - Connect to analytics platform
   - Set up alerts
   - Build dashboards

---

## 📚 Reference Documents

Read these for more details:
- `README.md` - Project overview
- `QUICK_REFERENCE.md` - Common commands
- `SETUP_GUIDE.md` - Detailed setup
- `COMPLETE_OVERVIEW.md` - Technical deep dive

---

## ✅ Final Checklist Before Going Live

- [ ] All API keys added to .env
- [ ] .env file is NOT in git
- [ ] Service starts without errors
- [ ] Health check passes
- [ ] Database has data
- [ ] Metrics endpoint responds
- [ ] Logs show normal operation
- [ ] Rate limits appropriate for tier
- [ ] Update intervals set correctly
- [ ] Database backup plan in place

---

## 🚀 You're Ready to Go!

Once you have:
1. ✅ API keys
2. ✅ .env configured
3. ✅ Docker running

Simply run:
```bash
docker-compose up -d
```

The system will start automatically and begin collecting data!

Monitor with:
```bash
docker-compose logs -f crypto-system
```

---

**Questions?** Check the documentation files or the API provider docs.

**Good luck! 🎉**
"""

# This is an actionable checklist document
