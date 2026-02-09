import google.generativeai as genai
from openai import OpenAI
from typing import List

# --- Constants ---
DEFAULT_GEMINI_MODELS = [
    "gemini-2.0-flash-lite-preview-02-05", # New lightweight model
    "gemini-2.0-flash-exp", 
    "gemini-1.5-flash"
]

DEFAULT_OPENAI_MODELS = [
    "gpt-4o-mini", # New lightweight model
    "gpt-4o", 
    "gpt-4-turbo"
]

def get_available_models(api_key: str, provider: str = "Google") -> List[str]:
    """
    Fetches available models for the specified AI provider.
    
    Args:
        api_key: The API key for the provider.
        provider: "Google" or "OpenAI".
        
    Returns:
        A list of model IDs.
    """
    if not api_key:
        return []
        
    if provider == "Google":
        try:
            genai.configure(api_key=api_key)
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name.replace('models/', ''))
            return sorted(models) if models else DEFAULT_GEMINI_MODELS
        except Exception:
            return DEFAULT_GEMINI_MODELS
            
    elif provider == "OpenAI":
        try:
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            # Filter for relevant GPT models
            gpt_models = [m.id for m in models if m.id.startswith("gpt-") and "vision" not in m.id]
            return sorted(gpt_models) if gpt_models else DEFAULT_OPENAI_MODELS
        except Exception:
            return DEFAULT_OPENAI_MODELS
            
    return []
