class AICVAdvisoryError(Exception):
    """Base exception for the AI CV Advisory Board application."""

    pass


class LLMProviderError(AICVAdvisoryError):
    """Raised when there's an error with the LLM provider (e.g., invalid API key, rate limit)."""

    pass


class JobScrapingError(AICVAdvisoryError):
    """Raised when a job description cannot be scraped from a URL."""

    pass


class FileProcessingError(AICVAdvisoryError):
    """Raised when there's an error processing an uploaded file (e.g., PDF parsing failure)."""

    pass


class PersonaLoadError(AICVAdvisoryError):
    """Raised when a persona configuration cannot be loaded."""

    pass
