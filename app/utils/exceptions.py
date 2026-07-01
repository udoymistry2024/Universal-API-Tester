class ProviderError(Exception):
    """Base exception for all provider interactions."""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class AuthenticationError(ProviderError):
    """Raised when authentication (API key) fails (401)."""
    pass

class RateLimitError(ProviderError):
    """Raised when rate limits are exceeded (429)."""
    pass

class QuotaExceededError(ProviderError):
    """Raised when billing limits or usage quotas are reached."""
    pass

class ConnectionError(ProviderError):
    """Raised on DNS, SSL, connection timeouts, or network resets."""
    pass
