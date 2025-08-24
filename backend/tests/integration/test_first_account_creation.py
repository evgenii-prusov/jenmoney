"""Integration test for the first account creation scenario."""
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from jenmoney.exceptions import ExchangeRateNotFoundError
from jenmoney.models.account import Account
from jenmoney.services.account_enrichment_service import AccountEnrichmentService


class TestFirstAccountCreationScenario:
    """Test the specific scenario reported in the issue where creating the first account fails."""
    
    def test_first_account_creation_without_exchange_rates(self):
        """Test that the first account can be created even when no exchange rates exist.
        
        This reproduces the exact scenario from the bug report:
        1. Fresh database setup
        2. No exchange rates configured yet
        3. User creates first account with non-USD currency
        4. Account listing should not fail
        """
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)
        
        # Create mock account with EUR currency (different from default USD)
        account = Mock(spec=Account)
        account.id = 1
        account.name = "My First Account"
        account.currency = "EUR"
        account.balance = Decimal("1000.00")
        account.description = "My first account in EUR"
        account.created_at = "2024-01-01T10:00:00Z"
        account.updated_at = "2024-01-01T10:00:00Z"
        
        # Mock user settings with USD as default currency
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "USD"
            mock_user_settings.get_or_create.return_value = mock_settings
            
            # Mock currency service to simulate no exchange rates available
            # This is the exact error that was occurring
            service.currency_service.get_current_rate = Mock(
                side_effect=ExchangeRateNotFoundError("EUR", "USD", "2024-01-01T10:00:00Z")
            )
            
            # This should NOT raise an exception anymore
            result = service.enrich_account_with_conversion(account)
            
            # Verify that the account data is returned correctly
            assert result["id"] == 1
            assert result["name"] == "My First Account"
            assert result["currency"] == "EUR"
            assert result["balance"] == 1000.00
            assert result["description"] == "My first account in EUR"
            assert result["default_currency"] == "USD"
            
            # Key fix: conversion fields should be None when rates are missing
            assert result["balance_in_default_currency"] is None
            assert result["exchange_rate_used"] is None
            
    def test_account_listing_endpoint_simulation(self):
        """Simulate the account listing endpoint that was failing.
        
        This tests the enrich_account_full method which calls both
        currency conversion and percentage calculation.
        """
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)
        
        # Create account
        account = Mock(spec=Account)
        account.id = 1
        account.name = "EUR Account"
        account.currency = "EUR"
        account.balance = Decimal("500.00")
        account.description = None
        account.created_at = "2024-01-01T10:00:00Z"
        account.updated_at = "2024-01-01T10:00:00Z"
        
        # Mock user settings
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "USD"
            mock_user_settings.get_or_create.return_value = mock_settings
            
            # Mock currency service to fail rate lookup
            service.currency_service.get_current_rate = Mock(
                side_effect=ExchangeRateNotFoundError("EUR", "USD", "2024-01-01T10:00:00Z")
            )
            service.currency_service.convert_amount = Mock(
                side_effect=ExchangeRateNotFoundError("EUR", "USD", "2024-01-01T10:00:00Z")
            )
            
            # Mock the database query for percentage calculation
            # Return empty list to simulate first account scenario
            db.query.return_value.all.return_value = []
            
            # This simulates what the account listing endpoint does
            result = service.enrich_account_full(account)
            
            # Should succeed and return expected structure
            assert result["id"] == 1
            assert result["name"] == "EUR Account"
            assert result["currency"] == "EUR"
            assert result["balance"] == 500.00
            assert result["description"] is None
            assert result["default_currency"] == "USD"
            assert result["balance_in_default_currency"] is None
            assert result["exchange_rate_used"] is None
            assert result["percentage_of_total"] == 0.0  # Empty portfolio
            
    def test_mixed_currency_accounts_with_partial_rates(self):
        """Test scenario where some rates exist but not all."""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)
        
        # Create account with currency that has no rate
        account = Mock(spec=Account)
        account.id = 1
        account.name = "RUB Account"
        account.currency = "RUB"
        account.balance = Decimal("50000.00")
        account.description = "Russian Ruble account"
        account.created_at = "2024-01-01T10:00:00Z"
        account.updated_at = "2024-01-01T10:00:00Z"
        
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "USD"
            mock_user_settings.get_or_create.return_value = mock_settings
            
            # Simulate missing rate for RUB
            service.currency_service.get_current_rate = Mock(
                side_effect=ExchangeRateNotFoundError("RUB", "USD", "2024-01-01T10:00:00Z")
            )
            
            # Should handle gracefully
            result = service.enrich_account_with_conversion(account)
            
            assert result["currency"] == "RUB"
            assert result["balance"] == 50000.00
            assert result["balance_in_default_currency"] is None
            assert result["exchange_rate_used"] is None