# Testing Guide - Crypto System

## Overview

The crypto-system project includes comprehensive test coverage for:
- Database models and ORM relationships
- Repository layer (CRUD operations)
- API client extractors
- Data transformers
- Utilities and validators
- End-to-end database integration

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── test_models.py                 # Database model tests
├── test_repository.py             # Repository layer tests
├── test_extractors.py             # API client tests
├── test_transformers.py           # Data transformation tests
├── test_utils.py                  # Utility function tests
└── test_database_integration.py   # Integration tests
```

## Setting Up Tests

### 1. Install Test Dependencies

```bash
pip install -r requirements.txt
```

The following test dependencies are included:
- `pytest==7.4.3` - Test framework
- `pytest-asyncio==0.21.1` - Async test support
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.12.0` - Mocking support

### 2. Install Development Dependencies (Optional)

```bash
pip install pytest-xdist  # For parallel test execution
pip install pytest-timeout  # For test timeouts
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_models.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_models.py::TestCryptocurrencyModel -v
```

### Run Specific Test Method

```bash
pytest tests/test_models.py::TestCryptocurrencyModel::test_create_cryptocurrency -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

This generates:
- Terminal output showing coverage percentage
- HTML report in `htmlcov/index.html`

### Run Using Test Script

```bash
python run_tests.py                # Run all tests
python run_tests.py --coverage     # Run with coverage
python run_tests.py --cov=70       # Require 70% minimum coverage
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

### Run with Timeout (30 seconds max per test)

```bash
pytest tests/ --timeout=30
```

## Test Categories

### 1. Model Tests (`test_models.py`)

Tests for SQLAlchemy ORM models:

- **CryptocurrencyModel**
  - ✅ Create cryptocurrency with all fields
  - ✅ Unique symbol constraint
  - ✅ Timestamp fields (created_at, updated_at)

- **ExchangeModel**
  - ✅ Create exchange with details
  - ✅ Unique name constraint

- **TradingPairModel**
  - ✅ Create trading pair with foreign keys
  - ✅ Relationships to crypto and exchange
  - ✅ Unique constraint (exchange_id + crypto_id + currencies)

- **PriceHistoryModel**
  - ✅ Create price history records
  - ✅ Relationships to trading pairs
  - ✅ Decimal precision for prices

- **MarketSentimentModel**
  - ✅ Store sentiment scores and labels
  - ✅ Relationship to cryptocurrency

- **MarketEventModel**
  - ✅ Create market events
  - ✅ Optional crypto relationship
  - ✅ Different event types

### 2. Repository Tests (`test_repository.py`)

Tests for data access layer:

- **Cryptocurrency Operations**
  - ✅ Get or create with idempotency
  - ✅ Retrieve by symbol
  - ✅ Get all cryptocurrencies

- **Exchange Operations**
  - ✅ Get or create exchanges
  - ✅ Retrieve by name
  - ✅ List all exchanges

- **Trading Pair Operations**
  - ✅ Create trading pairs
  - ✅ Get active pairs
  - ✅ Unique constraints enforced

- **Price History Operations**
  - ✅ Add single price record
  - ✅ Get latest price
  - ✅ Get price range by date
  - ✅ Get prices for last N hours
  - ✅ Batch insert (250+ records)

### 3. Extractor Tests (`test_extractors.py`)

Tests for API client services:

- **RateLimiter**
  - ✅ Token bucket algorithm
  - ✅ Respects call limits
  - ✅ Token regeneration

- **BaseAPIService**
  - ✅ Service initialization
  - ✅ Async context manager
  - ✅ Error handling with retries

- **CoinGecko Service**
  - ✅ Proper API headers
  - ✅ Coin list structure

- **CoinMarketCap Service**
  - ✅ API key in headers
  - ✅ Request formatting

- **CMC DEX Service**
  - ✅ DEX-specific headers
  - ✅ Rate limit configuration

### 4. Transformer Tests (`test_transformers.py`)

Tests for data transformation:

- **PriceTransformer**
  - ✅ Transform CoinGecko market data
  - ✅ Transform OHLC data
  - ✅ Transform CMC quotes

- **MetadataTransformer**
  - ✅ Transform coin details
  - ✅ Transform exchange data
  - ✅ Extract links and scores

- **SentimentTransformer**
  - ✅ Determine sentiment labels
  - ✅ Transform trending data
  - ✅ Calculate composite sentiment
  - ✅ Handle empty sentiment lists

### 5. Utility Tests (`test_utils.py`)

Tests for helper functions:

- **Cache**
  - ✅ Set and get values
  - ✅ TTL expiration
  - ✅ Clear cache
  - ✅ Cleanup expired entries

- **Validators**
  - ✅ Validate price data (required fields, positive values)
  - ✅ Validate exchange data
  - ✅ Validate sentiment data (score range -1 to 1)

- **Helpers**
  - ✅ Format decimals with precision
  - ✅ Parse ISO timestamps
  - ✅ Handle invalid timestamps
  - ✅ Truncate strings with ellipsis

### 6. Integration Tests (`test_database_integration.py`)

End-to-end database tests:

- **Database Connection**
  - ✅ URL generation
  - ✅ Settings masking
  - ✅ Connection pooling

- **End-to-End Data Flow**
  - ✅ Create cryptocurrency → Exchange → Trading Pair → Price
  - ✅ Verify data relationships
  - ✅ Retrieve and validate

- **Sentiment Integration**
  - ✅ Store sentiment data
  - ✅ Query latest sentiment

- **Market Events**
  - ✅ Store market events
  - ✅ Query by date range

- **Batch Operations**
  - ✅ Insert 100+ records efficiently
  - ✅ Verify batch data integrity

- **Database Constraints**
  - ✅ Foreign key constraints
  - ✅ Unique constraints
  - ✅ NOT NULL constraints

## Database Testing

### Using SQLite for Tests

By default, tests use an **in-memory SQLite database**:

```python
@pytest.fixture(scope="session")
def test_db_url():
    """Get test database URL."""
    return "sqlite:///:memory:"
```

**Advantages:**
- ✅ Fast test execution
- ✅ No external dependencies
- ✅ Automatic cleanup
- ✅ Isolated test environment

**Using PostgreSQL for Tests**

To test against actual PostgreSQL:

```bash
# Create test database
createdb test_crypto_market

# Run tests against PostgreSQL
SQLALCHEMY_DATABASE_URL="postgresql://user:password@localhost:5432/test_crypto_market" pytest tests/
```

## Fixtures

### conftest.py Fixtures

All fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def test_session():
    """Create isolated database session for each test."""
    # Returns a SQLAlchemy session
    # Automatically rolls back after test

@pytest.fixture
def test_settings():
    """Get test configuration settings."""
    # Returns Settings object with test values
    # API keys, rate limits, DB config

@pytest.fixture(scope="session")
def test_engine():
    """Shared database engine for session."""
    # Creates all tables before tests
    # Cleans up after all tests complete

@pytest.fixture
def event_loop():
    """Event loop for async tests."""
    # Provides asyncio event loop
```

### Using Fixtures in Tests

```python
def test_example(test_session, test_settings):
    """Test using fixtures."""
    # test_session: SQLAlchemy session
    # test_settings: Configuration object
    
    repo = CryptoRepository(test_session)
    # ... perform tests
```

## Async Testing

Tests for async code use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_rate_limiter():
    """Test async rate limiter."""
    limiter = RateLimiter(calls_per_minute=10)
    await limiter.acquire()
    # ... verify rate limiting
```

### Running Only Async Tests

```bash
pytest tests/ -k asyncio -v
```

## Coverage Analysis

### Generate Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
```

### View HTML Coverage Report

```bash
# Open in browser
htmlcov/index.html
```

### Identify Uncovered Code

The HTML report shows:
- ✅ **Green**: Covered code
- ✅ **Red**: Uncovered code
- ✅ **Yellow**: Partially covered

### Set Minimum Coverage Threshold

```bash
pytest tests/ --cov=. --cov-fail-under=80
```

This fails if overall coverage < 80%.

## Common Test Issues

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'crypto_system'`

**Solution**:
```bash
# Install in development mode
pip install -e .

# OR add project root to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;c:\Users\deadm\Desktop\crypto-system
```

### Issue: Database Lock

**Problem**: `database is locked`

**Solution**: SQLite locks during concurrent writes. Use PostgreSQL for tests:
```bash
pytest tests/ --db postgresql://localhost/test_crypto
```

### Issue: Async Test Timeout

**Problem**: Test hangs indefinitely

**Solution**:
```bash
# Add timeout
pytest tests/test_extractors.py --timeout=30
```

### Issue: Foreign Key Constraint

**Problem**: `FOREIGN KEY constraint failed`

**Solution**: Ensure parent records exist before referencing:
```python
# Create cryptocurrency first
crypto = repo.get_or_create_cryptocurrency(...)

# Then create trading pair
pair = repo.get_or_create_trading_pair(
    crypto_id=crypto.id,  # Now valid
    ...
)
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=. --cov-fail-under=80
      - run: |
          if [ -d htmlcov ]; then
            echo "Coverage report available"
          fi
```

### Running Tests Before Deployment

```bash
# Run all tests with coverage
pytest tests/ --cov=. --cov-fail-under=70

# Check for security issues
bandit -r . -ll

# Check code quality
pylint crypto_system/

# Only deploy if all checks pass
docker-compose up -d
```

## Performance Testing

### Run Tests with Timing

```bash
pytest tests/ -v --durations=10
```

Shows the 10 slowest tests.

### Profile Slow Tests

```bash
pytest tests/ --profile
```

Generates `prof_stats.txt` with detailed timing.

## Next Steps

### After Running Tests

1. **Review Coverage Report**
   ```bash
   open htmlcov/index.html  # macOS
   start htmlcov/index.html  # Windows
   xdg-open htmlcov/index.html  # Linux
   ```

2. **Fix Failed Tests**
   - Review test output
   - Check error messages
   - Update code or tests as needed

3. **Add New Tests**
   - For new features
   - For bug fixes
   - For edge cases

4. **Deploy with Confidence**
   ```bash
   docker-compose up -d
   ```

## Test Maintenance

### Update Tests When Code Changes

1. Run tests: `pytest tests/`
2. Fix failures: Update code or tests
3. Add coverage: Write tests for new functionality
4. Verify: Re-run full test suite

### Keep Tests Isolated

- Each test should be independent
- Use fixtures for shared setup
- Clean up after each test
- Don't depend on test execution order

### Keep Tests Fast

- Use in-memory SQLite
- Mock external APIs
- Parallel execution with `-n auto`
- Proper fixture scoping

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#testing-orm-code)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Test Status**: Production Ready ✅

All components tested and verified for database integration!
