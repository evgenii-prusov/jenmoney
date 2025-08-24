"""Custom exceptions for the JenMoney application."""


class CurrencyConversionError(Exception):
    """Raised when currency conversion fails."""

    def __init__(
        self,
        message: str,
        from_currency: str | None = None,
        to_currency: str | None = None,
        amount: str | None = None,
        original_error: Exception | None = None,
    ):
        """Initialize the currency conversion error.

        Args:
            message: Human-readable error message
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount that failed to convert
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.amount = amount
        self.original_error = original_error

    def __str__(self) -> str:
        """Return a detailed error message."""
        parts = [super().__str__()]

        if self.from_currency and self.to_currency:
            parts.append(f"Conversion: {self.from_currency} -> {self.to_currency}")

        if self.amount:
            parts.append(f"Amount: {self.amount}")

        if self.original_error:
            parts.append(f"Original error: {self.original_error}")

        return " | ".join(parts)


class ExchangeRateNotFoundError(CurrencyConversionError):
    """Raised when no exchange rate is found for a currency pair."""

    def __init__(
        self,
        from_currency: str,
        to_currency: str,
        date: str | None = None,
    ):
        """Initialize the exchange rate not found error.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for which the rate was requested
        """
        message = f"No exchange rate found for {from_currency} to {to_currency}"
        if date:
            message += f" for date {date}"

        super().__init__(
            message=message,
            from_currency=from_currency,
            to_currency=to_currency,
        )
        self.date = date


class TransferValidationError(Exception):
    """Raised when transfer validation fails."""

    pass


class InsufficientFundsError(TransferValidationError):
    """Raised when source account has insufficient funds."""

    pass


class InvalidAccountError(TransferValidationError):
    """Raised when account does not exist or is invalid."""

    pass
