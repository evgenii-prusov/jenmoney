"""Tests for the default data initialization functionality."""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from jenmoney.models.currency_rate import CurrencyRate
from jenmoney.utils.default_data import initialize_default_exchange_rates


class TestDefaultDataInitialization:
    def test_initialize_default_rates_creates_rates_when_none_exist(self):
        """Test that default rates are created when no rates exist in database."""
        db = Mock(spec=Session)
        
        # Mock query to return None (no existing rates)
        mock_query = Mock()
        mock_query.first.return_value = None
        db.query.return_value = mock_query
        
        # Call the function
        initialize_default_exchange_rates(db)
        
        # Verify that rates were added
        assert db.add.call_count == 8  # Should add 8 default currencies
        db.commit.assert_called_once()
        
        # Verify the first call to add() contains a CurrencyRate
        first_add_call = db.add.call_args_list[0]
        rate = first_add_call[0][0]  # First positional argument
        assert isinstance(rate, CurrencyRate)
        assert rate.currency_to == "USD"
        assert rate.effective_to is None
        
    def test_initialize_default_rates_skips_when_rates_exist(self):
        """Test that default rates are not created when rates already exist."""
        db = Mock(spec=Session)
        
        # Mock query to return an existing rate
        existing_rate = Mock()
        mock_query = Mock()
        mock_query.first.return_value = existing_rate
        db.query.return_value = mock_query
        
        # Call the function
        initialize_default_exchange_rates(db)
        
        # Verify that no rates were added
        db.add.assert_not_called()
        db.commit.assert_not_called()
        
    def test_default_rates_include_expected_currencies(self):
        """Test that all expected currencies are included in default rates."""
        db = Mock(spec=Session)
        
        # Mock query to return None (no existing rates)
        mock_query = Mock()
        mock_query.first.return_value = None
        db.query.return_value = mock_query
        
        # Call the function
        initialize_default_exchange_rates(db)
        
        # Extract all currencies that were added
        added_currencies = []
        for call in db.add.call_args_list:
            rate = call[0][0]
            added_currencies.append(rate.currency_from)
        
        # Verify expected currencies are present
        expected_currencies = ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "RUB"]
        assert set(added_currencies) == set(expected_currencies)
        
        # Verify all rates convert to USD
        for call in db.add.call_args_list:
            rate = call[0][0]
            assert rate.currency_to == "USD"
            assert isinstance(rate.rate, Decimal)
            assert rate.rate > 0