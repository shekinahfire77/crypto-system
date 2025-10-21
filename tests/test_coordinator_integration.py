"""Integration tests for data coordinator."""

import asyncio
from datetime import datetime
from decimal import Decimal

import pytest

from database import get_db_session, CryptoRepository
from database.models import PriceHistory, Cryptocurrency, TradingPair
from orchestration.coordinator import DataCoordinator


@pytest.mark.asyncio
async def test_fetch_and_store_prices_actually_persists(mocker, db_session):
    """Test that prices are actually persisted to database.
    
    This test verifies the fix for the critical bug where prices were
    being fetched and counted but never inserted into the database.
    """
    # Mock the CoinGecko service
    mock_market_data = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 45000.50,
            "high_24h": 46000.00,
            "low_24h": 44000.00,
            "market_cap": 900000000000,
            "market_cap_rank": 1,
            "total_volume": 25000000000,
            "price_change_24h": 1000.00,
            "price_change_percentage_24h": 2.27,
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 2500.75,
            "high_24h": 2600.00,
            "low_24h": 2400.00,
            "market_cap": 300000000000,
            "market_cap_rank": 2,
            "total_volume": 15000000000,
            "price_change_24h": 50.00,
            "price_change_percentage_24h": 2.04,
        },
    ]
    
    # Create coordinator
    coordinator = DataCoordinator()
    await coordinator.initialize()
    
    # Mock the CoinGecko service's get_coin_markets method
    mocker.patch.object(
        coordinator.coingecko,
        "get_coin_markets",
        return_value=mock_market_data,
    )
    
    # Run the fetch and store
    records_inserted = await coordinator.fetch_and_store_prices()
    
    # Verify records were counted
    assert records_inserted == 2, f"Expected 2 records inserted, got {records_inserted}"
    
    # Verify records actually exist in database
    prices = db_session.query(PriceHistory).all()
    assert len(prices) == 2, f"Expected 2 price records in database, got {len(prices)}"
    
    # Verify cryptocurrency records were created
    cryptocurrencies = db_session.query(Cryptocurrency).all()
    assert len(cryptocurrencies) >= 2, "Should have at least 2 cryptocurrencies"
    
    # Verify trading pair records were created
    trading_pairs = db_session.query(TradingPair).all()
    assert len(trading_pairs) >= 2, "Should have at least 2 trading pairs"
    
    # Verify price data integrity
    btc_prices = [p for p in prices if p.trading_pair.base_currency.symbol == "BTC"]
    eth_prices = [p for p in prices if p.trading_pair.base_currency.symbol == "ETH"]
    
    assert len(btc_prices) == 1, "Should have 1 BTC price record"
    assert len(eth_prices) == 1, "Should have 1 ETH price record"
    
    # Verify BTC price data
    btc_price = btc_prices[0]
    assert btc_price.close_price == Decimal("45000.50")
    assert btc_price.high_price == Decimal("46000")
    assert btc_price.low_price == Decimal("44000")
    assert btc_price.open_price == Decimal("45000.50")
    assert btc_price.volume == Decimal("25000000000")
    
    # Verify ETH price data
    eth_price = eth_prices[0]
    assert eth_price.close_price == Decimal("2500.75")
    assert eth_price.high_price == Decimal("2600")
    assert eth_price.low_price == Decimal("2400")
    assert eth_price.open_price == Decimal("2500.75")
    assert eth_price.volume == Decimal("15000000000")
    
    # Cleanup
    await coordinator.cleanup()


@pytest.mark.asyncio
async def test_fetch_and_store_prices_batch_operation(mocker, db_session):
    """Test that batch operation is used for efficiency."""
    mock_markets = [
        {
            "id": f"coin-{i}",
            "symbol": f"coin{i}",
            "name": f"Coin {i}",
            "current_price": 100.0 + i,
            "high_24h": 110.0 + i,
            "low_24h": 90.0 + i,
            "market_cap": 1000000000 + i,
            "market_cap_rank": i + 1,
            "total_volume": 100000000 + i,
            "price_change_24h": 5.0,
            "price_change_percentage_24h": 5.0,
        }
        for i in range(10)
    ]
    
    coordinator = DataCoordinator()
    await coordinator.initialize()
    
    mocker.patch.object(
        coordinator.coingecko,
        "get_coin_markets",
        return_value=mock_markets,
    )
    
    # Run fetch and store
    records_inserted = await coordinator.fetch_and_store_prices()
    
    # Verify all records were inserted
    assert records_inserted == 10
    
    # Verify all prices exist
    prices = db_session.query(PriceHistory).all()
    assert len(prices) == 10
    
    await coordinator.cleanup()


@pytest.mark.asyncio
async def test_fetch_and_store_prices_handles_missing_data(mocker, db_session):
    """Test that missing data fields are handled gracefully."""
    mock_markets = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 45000.50,
            "high_24h": None,  # Missing
            "low_24h": None,   # Missing
            "market_cap": None,  # Missing
            "market_cap_rank": 1,
            "total_volume": None,  # Missing
            "price_change_24h": None,  # Missing
            "price_change_percentage_24h": None,  # Missing
        },
    ]
    
    coordinator = DataCoordinator()
    await coordinator.initialize()
    
    mocker.patch.object(
        coordinator.coingecko,
        "get_coin_markets",
        return_value=mock_markets,
    )
    
    # Run fetch and store - should not raise exception
    records_inserted = await coordinator.fetch_and_store_prices()
    
    # Verify record was inserted despite missing data
    assert records_inserted == 1
    
    prices = db_session.query(PriceHistory).all()
    assert len(prices) == 1
    
    # Verify prices use fallback values
    price = prices[0]
    assert price.close_price == Decimal("45000.50")
    assert price.high_price == Decimal("45000.50")  # Falls back to current
    assert price.low_price == Decimal("45000.50")  # Falls back to current
    assert price.volume == 0  # Defaults to 0
    
    await coordinator.cleanup()


@pytest.mark.asyncio
async def test_fetch_and_store_prices_error_handling(mocker, db_session):
    """Test that errors are handled and logged appropriately."""
    coordinator = DataCoordinator()
    await coordinator.initialize()
    
    # Mock API to raise exception
    mocker.patch.object(
        coordinator.coingecko,
        "get_coin_markets",
        side_effect=Exception("API Error"),
    )
    
    # Run fetch and store - should not raise, should return 0
    records_inserted = await coordinator.fetch_and_store_prices()
    
    assert records_inserted == 0
    
    # Verify no prices were inserted
    prices = db_session.query(PriceHistory).all()
    assert len(prices) == 0
    
    await coordinator.cleanup()


def test_price_history_fields_populated(db_session):
    """Test that all required PriceHistory fields are populated."""
    repo = CryptoRepository(db_session)
    
    # Create test data
    crypto = repo.get_or_create_cryptocurrency("TEST", "Test Coin")
    pair = repo.get_or_create_trading_pair(crypto.id, "USD")
    
    # Add price
    price = repo.add_price_history(
        trading_pair_id=pair.id,
        open_price=Decimal("100.00"),
        high_price=Decimal("105.00"),
        low_price=Decimal("95.00"),
        close_price=Decimal("102.00"),
        volume=Decimal("1000000"),
        recorded_at=datetime.now(),
    )
    
    # Verify all fields
    assert price.trading_pair_id == pair.id
    assert price.open_price == Decimal("100.00")
    assert price.high_price == Decimal("105.00")
    assert price.low_price == Decimal("95.00")
    assert price.close_price == Decimal("102.00")
    assert price.volume == Decimal("1000000")
    assert price.recorded_at is not None


def test_batch_add_prices_efficiency(db_session):
    """Test that batch insert reduces database operations."""
    repo = CryptoRepository(db_session)
    
    # Create test cryptocurrencies and pairs
    pairs = []
    for i in range(5):
        crypto = repo.get_or_create_cryptocurrency(f"COIN{i}", f"Coin {i}")
        pair = repo.get_or_create_trading_pair(crypto.id, "USD")
        pairs.append(pair)
    
    # Create batch prices
    price_batch = [
        (
            pair.id,
            Decimal(f"{100 + i}"),  # open
            Decimal(f"{105 + i}"),  # high
            Decimal(f"{95 + i}"),   # low
            Decimal(f"{102 + i}"),  # close
            Decimal("1000000"),     # volume
            datetime.now(),
        )
        for i, pair in enumerate(pairs)
    ]
    
    # Add all prices in batch
    count = repo.batch_add_prices(price_batch)
    
    # Verify all added
    assert count == 5
    
    prices = db_session.query(PriceHistory).all()
    assert len(prices) == 5


@pytest.mark.asyncio
async def test_coordinator_cleanup_closes_sessions(mocker, db_session):
    """Test that coordinator cleanup properly closes sessions."""
    coordinator = DataCoordinator()
    await coordinator.initialize()
    
    # Mock the close methods
    close_spy_cg = mocker.spy(coordinator.coingecko, "close")
    close_spy_cmc = mocker.spy(coordinator.cmc, "close")
    close_spy_dex = mocker.spy(coordinator.cmc_dex, "close")
    
    # Run cleanup
    await coordinator.cleanup()
    
    # Verify close was called on all services
    close_spy_cg.assert_called_once()
    close_spy_cmc.assert_called_once()
    close_spy_dex.assert_called_once()
