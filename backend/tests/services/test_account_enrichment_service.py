from decimal import Decimal
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pytest

from sqlalchemy.orm import Session

from jenmoney.exceptions import CurrencyConversionError, ExchangeRateNotFoundError
from jenmoney.models.account import Account
from jenmoney.services.account_enrichment_service import AccountEnrichmentService


class TestAccountEnrichmentService:
    def test_enrich_account_same_currency_as_default(self):
        """Test enrichment when account currency matches default currency"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account
        account = Mock(spec=Account)
        account.id = 1
        account.name = "Test Account"
        account.currency = "EUR"
        account.balance = Decimal("1000.00")
        account.description = "Test description"
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings with same currency
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "EUR"
            mock_user_settings.get_or_create.return_value = mock_settings

            result = service.enrich_account_with_conversion(account)

            assert result["id"] == 1
            assert result["name"] == "Test Account"
            assert result["currency"] == "EUR"
            assert result["balance"] == 1000.00
            assert result["description"] == "Test description"
            assert result["default_currency"] == "EUR"
            assert result["balance_in_default_currency"] is None
            assert result["exchange_rate_used"] is None

    def test_enrich_account_different_currency_success(self):
        """Test enrichment when account currency differs from default currency"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account
        account = Mock(spec=Account)
        account.id = 1
        account.name = "USD Account"
        account.currency = "USD"
        account.balance = Decimal("1000.00")
        account.description = "USD test account"
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings with different currency
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "EUR"
            mock_user_settings.get_or_create.return_value = mock_settings

            # Mock currency service
            service.currency_service.get_current_rate = Mock(return_value=Decimal("0.85"))
            service.currency_service.convert_amount = Mock(return_value=Decimal("850.00"))

            result = service.enrich_account_with_conversion(account)

            assert result["id"] == 1
            assert result["name"] == "USD Account"
            assert result["currency"] == "USD"
            assert result["balance"] == 1000.00
            assert result["description"] == "USD test account"
            assert result["default_currency"] == "EUR"
            assert result["balance_in_default_currency"] == 850.00
            assert result["exchange_rate_used"] == 0.85

            # Verify currency service was called correctly
            service.currency_service.get_current_rate.assert_called_once_with("USD", "EUR")
            service.currency_service.convert_amount.assert_called_once_with(
                Decimal("1000.00"), "USD", "EUR"
            )

    def test_enrich_account_conversion_graceful_fallback(self):
        """Test enrichment gracefully handles missing exchange rates"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account
        account = Mock(spec=Account)
        account.id = 1
        account.name = "JPY Account"
        account.currency = "JPY"
        account.balance = Decimal("100000.00")
        account.description = "JPY test account"
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings with different currency
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "EUR"
            mock_user_settings.get_or_create.return_value = mock_settings

            # Mock currency service to raise ExchangeRateNotFoundError
            service.currency_service.get_current_rate = Mock(
                side_effect=ExchangeRateNotFoundError("JPY", "EUR")
            )

            # Should not raise exception, instead return None for conversion fields
            result = service.enrich_account_with_conversion(account)
            
            # Verify basic account data is present
            assert result["id"] == 1
            assert result["name"] == "JPY Account"
            assert result["currency"] == "JPY"
            assert result["balance"] == 100000.00
            assert result["description"] == "JPY test account"
            assert result["default_currency"] == "EUR"
            
            # Verify conversion fields are None when exchange rates are missing
            assert result["balance_in_default_currency"] is None
            assert result["exchange_rate_used"] is None

    def test_enrich_account_with_none_description(self):
        """Test enrichment when account has None description"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account with None description
        account = Mock(spec=Account)
        account.id = 1
        account.name = "Test Account"
        account.currency = "EUR"
        account.balance = Decimal("500.00")
        account.description = None
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "EUR"
            mock_user_settings.get_or_create.return_value = mock_settings

            result = service.enrich_account_with_conversion(account)

            assert result["description"] is None
            assert result["balance"] == 500.00

    def test_enrich_account_zero_balance(self):
        """Test enrichment with zero balance account"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account with zero balance
        account = Mock(spec=Account)
        account.id = 1
        account.name = "Empty Account"
        account.currency = "USD"
        account.balance = Decimal("0.00")
        account.description = "Empty account"
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings with different currency
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "EUR"
            mock_user_settings.get_or_create.return_value = mock_settings

            # Mock currency service
            service.currency_service.get_current_rate = Mock(return_value=Decimal("0.85"))
            service.currency_service.convert_amount = Mock(return_value=Decimal("0.00"))

            result = service.enrich_account_with_conversion(account)

            assert result["balance"] == 0.00
            assert result["balance_in_default_currency"] == 0.00
            assert result["exchange_rate_used"] == 0.85

    def test_enrich_account_service_initialization(self):
        """Test that service initializes currency service correctly"""
        db = Mock(spec=Session)
        
        with patch("jenmoney.services.account_enrichment_service.CurrencyService") as MockCurrencyService:
            service = AccountEnrichmentService(db)
            
            # Verify CurrencyService was initialized with the database session
            MockCurrencyService.assert_called_once_with(db)
            assert service.db == db
            assert service.currency_service == MockCurrencyService.return_value

    def test_enrich_account_high_precision_balance(self):
        """Test enrichment with high precision decimal balance"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account with high precision balance
        account = Mock(spec=Account)
        account.id = 1
        account.name = "Precise Account"
        account.currency = "BTC"
        account.balance = Decimal("0.12345678")
        account.description = "Bitcoin account"
        account.created_at = datetime.now(timezone.utc)
        account.updated_at = datetime.now(timezone.utc)

        # Mock user settings
        with patch("jenmoney.services.account_enrichment_service.user_settings") as mock_user_settings:
            mock_settings = Mock()
            mock_settings.default_currency = "USD"
            mock_user_settings.get_or_create.return_value = mock_settings

            # Mock currency service with high value conversion
            service.currency_service.get_current_rate = Mock(return_value=Decimal("45000.00"))
            service.currency_service.convert_amount = Mock(return_value=Decimal("5555.55502"))

            result = service.enrich_account_with_conversion(account)

            assert result["balance"] == 0.12345678
            assert result["balance_in_default_currency"] == 5555.55502
            assert result["exchange_rate_used"] == 45000.00