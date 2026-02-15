import os
from typing import List

from exceptions import LLMProviderError
from llm_utils import DEFAULT_GEMINI_MODELS, DEFAULT_OPENAI_MODELS, get_available_models
from logger import logger

CHEAP_MODELS = {
    "Google": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
    "OpenAI": "gpt-4o-mini",
}


class ConfigService:
    @staticmethod
    def get_is_online() -> bool:
        return os.getenv("ONLINE_MODE", "false").lower() == "true"

    @staticmethod
    def get_env_api_key(provider: str) -> str:
        if provider == "Google":
            return os.getenv("GOOGLE_API_KEY", "")
        return os.getenv("OPENAI_API_KEY", "")

    @staticmethod
    def fetch_models(provider: str, api_key: str) -> List[str]:
        if not api_key:
            logger.warning(f"Attempted to fetch models for {provider} without an API key.")
            return []

        # Use defaults if using system key
        system_key = ConfigService.get_env_api_key(provider)
        if api_key == system_key:
            logger.info(f"Using system default models for {provider}.")
            return DEFAULT_GEMINI_MODELS if provider == "Google" else DEFAULT_OPENAI_MODELS

        try:
            logger.info(f"Fetching available models for {provider}...")
            models = get_available_models(api_key, provider)
            logger.info(f"Successfully fetched {len(models)} models for {provider}.")
            return models
        except Exception as e:
            logger.error(f"Failed to fetch models for {provider}: {str(e)}")
            raise LLMProviderError(f"Could not retrieve models from {provider}. Please check your API key.") from e

    @staticmethod
    def get_cheap_model(provider: str) -> str:
        return CHEAP_MODELS.get(provider, "")
