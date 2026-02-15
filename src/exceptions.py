class AICVAdvisorError(Exception):
    """Base exception for the AI CV Advisor Board application."""

    pass


class LLMProviderError(AICVAdvisorError):
    """Raised when there's an error with the LLM provider (e.g., invalid API key, rate limit)."""

    pass


class JobScrapingError(AICVAdvisorError):
    """Raised when a job description cannot be scraped from a URL."""

    pass


class FileProcessingError(AICVAdvisorError):
    """Raised when there's an error processing an uploaded file (e.g., PDF parsing failure)."""

    pass


class PersonaLoadError(AICVAdvisorError):
    """Raised when a persona configuration cannot be loaded."""

    pass
