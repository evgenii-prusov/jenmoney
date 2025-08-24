from decimal import Decimal
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from jenmoney.models.account import Account
from jenmoney.services.account_enrichment_service import AccountEnrichmentService


class TestAccountEnrichmentService:
    def test_get_account_percentage_single_account(self):
        """Test percentage calculation with a single account (should be 100%)"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account
        account = Mock(spec=Account)
        account.id = 1
        account.balance = Decimal("1000.00")
        account.currency = "USD"

        # Mock database query
        db.query.return_value.all.return_value = [account]

        # Mock currency service to return same value (USD to USD)
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            mock_convert.return_value = Decimal("1000.00")

            result = service.get_account_percentage(1)

            # Single account should be 100%
            assert result == 1.0

    def test_get_account_percentage_multiple_accounts_equal(self):
        """Test percentage calculation with multiple accounts of equal value"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock accounts
        accounts = []
        for i in range(4):
            account = Mock(spec=Account)
            account.id = i + 1
            account.balance = Decimal("250.00")
            account.currency = "USD"
            accounts.append(account)

        # Mock database query
        db.query.return_value.all.return_value = accounts

        # Mock currency service
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            mock_convert.return_value = Decimal("250.00")

            result = service.get_account_percentage(2)

            # Each account should be 25%
            assert result == 0.25

    def test_get_account_percentage_different_currencies(self):
        """Test percentage calculation with different currencies"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock accounts with different currencies
        account1 = Mock(spec=Account)
        account1.id = 1
        account1.balance = Decimal("1000.00")
        account1.currency = "EUR"

        account2 = Mock(spec=Account)
        account2.id = 2
        account2.balance = Decimal("500.00")
        account2.currency = "USD"

        account3 = Mock(spec=Account)
        account3.id = 3
        account3.balance = Decimal("100000.00")
        account3.currency = "JPY"

        # Mock database query
        db.query.return_value.all.return_value = [account1, account2, account3]

        # Mock currency service with realistic exchange rates
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            def convert_side_effect(amount, from_currency, to_currency):
                if from_currency == "EUR":
                    return Decimal("1100.00")  # 1 EUR = 1.1 USD
                elif from_currency == "USD":
                    return Decimal("500.00")
                elif from_currency == "JPY":
                    return Decimal("900.00")  # 100000 JPY = 900 USD
                return amount

            mock_convert.side_effect = convert_side_effect

            result = service.get_account_percentage(2)

            # Account 2: 500 USD out of (1100 + 500 + 900) = 500/2500 = 0.20
            assert result == 0.20

    def test_get_account_percentage_zero_balance(self):
        """Test percentage calculation when account has zero balance"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock accounts
        account1 = Mock(spec=Account)
        account1.id = 1
        account1.balance = Decimal("1000.00")
        account1.currency = "USD"

        account2 = Mock(spec=Account)
        account2.id = 2
        account2.balance = Decimal("0.00")
        account2.currency = "USD"

        # Mock database query
        db.query.return_value.all.return_value = [account1, account2]

        # Mock currency service
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            def convert_side_effect(amount, from_currency, to_currency):
                return amount

            mock_convert.side_effect = convert_side_effect

            result = service.get_account_percentage(2)

            # Account with zero balance should be 0%
            assert result == 0.0

    def test_get_account_percentage_nonexistent_account(self):
        """Test percentage calculation for non-existent account"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock account
        account = Mock(spec=Account)
        account.id = 1
        account.balance = Decimal("1000.00")
        account.currency = "USD"

        # Mock database query
        db.query.return_value.all.return_value = [account]

        # Mock currency service
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            mock_convert.return_value = Decimal("1000.00")

            result = service.get_account_percentage(999)  # Non-existent ID

            # Non-existent account should return 0%
            assert result == 0.0

    def test_get_account_percentage_no_accounts(self):
        """Test percentage calculation when no accounts exist"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Mock database query returning empty list
        db.query.return_value.all.return_value = []

        result = service.get_account_percentage(1)

        # Should return 0% when no accounts exist
        assert result == 0.0

    def test_get_account_percentage_all_zero_balances(self):
        """Test percentage calculation when all accounts have zero balance"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock accounts with zero balances
        accounts = []
        for i in range(3):
            account = Mock(spec=Account)
            account.id = i + 1
            account.balance = Decimal("0.00")
            account.currency = "USD"
            accounts.append(account)

        # Mock database query
        db.query.return_value.all.return_value = accounts

        # Mock currency service
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            mock_convert.return_value = Decimal("0.00")

            result = service.get_account_percentage(1)

            # Should return 0% when all balances are zero
            assert result == 0.0

    def test_get_account_percentage_rounding(self):
        """Test that percentage is properly rounded to 2 decimal places"""
        db = Mock(spec=Session)
        service = AccountEnrichmentService(db)

        # Create mock accounts that will result in repeating decimal
        account1 = Mock(spec=Account)
        account1.id = 1
        account1.balance = Decimal("100.00")
        account1.currency = "USD"

        account2 = Mock(spec=Account)
        account2.id = 2
        account2.balance = Decimal("200.00")
        account2.currency = "USD"

        # Mock database query
        db.query.return_value.all.return_value = [account1, account2]

        # Mock currency service
        with patch.object(service.currency_service, 'convert_amount') as mock_convert:
            def convert_side_effect(amount, from_currency, to_currency):
                return amount

            mock_convert.side_effect = convert_side_effect

            result = service.get_account_percentage(1)

            # 100/300 = 0.333... should be rounded to 0.33
            assert result == 0.33
