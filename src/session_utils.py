"""Utility functions for managing Streamlit session state and navigation."""

import os

import streamlit as st

# Default Cheap Models
CHEAP_MODELS = {
    "Google": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
    "OpenAI": "gpt-4o-mini",
}


def get_is_online():
    """Check if online mode is enabled."""
    return os.getenv("ONLINE_MODE", "false").lower() == "true"


def get_env_api_key(provider):
    """Retrieve the API key for the specified provider from environment variables.

    Args:
        provider: The LLM provider ("Google" or "OpenAI").

    Returns:
        The API key if found, otherwise an empty string.
    """
    if provider == "Google":
        return os.getenv("GOOGLE_API_KEY", "")
    return os.getenv("OPENAI_API_KEY", "")


def init_session_state():
    """Initialize the session state variables for the application."""
    defaults = {
        "step": 0,
        "llm_provider": "Google",
        "custom_agents": [],
        "selected_persona_names": [],
        "vectorstore": None,
        "cv_content": "",
        "cv_filename": "",
        "job_description": "",
        "job_url": "",
        "job_text": "",
        "crew_result": None,
        "interview_questions": [],
        "user_answers": {},
        "interview_done": False,
        "board_agents": [],
    }

    is_online = get_is_online()

    if is_online:
        defaults["llm_provider"] = "Google"

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if is_online:
        st.session_state.llm_provider = "Google"
        st.session_state.api_key = get_env_api_key("Google")
        st.session_state.selected_model = CHEAP_MODELS.get("Google", "")
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = get_env_api_key(st.session_state.llm_provider)

        if "selected_model" not in st.session_state or not st.session_state.selected_model:
            st.session_state.selected_model = CHEAP_MODELS.get(st.session_state.llm_provider, "")


def reset_app():
    """Reset the application state and navigate back to the first step."""
    st.session_state.step = 1
    st.session_state.cv_content = ""
    st.session_state.cv_filename = ""
    st.session_state.job_description = ""
    st.session_state.job_url = ""
    st.session_state.job_text = ""
    st.session_state.crew_result = None
    st.session_state.interview_questions = []
    st.session_state.user_answers = {}
    st.session_state.interview_done = False
    st.session_state.board_agents = []
    st.rerun()


def next_step():
    """Advance to the next step in the application."""
    st.session_state.step += 1
    st.rerun()


def prev_step():
    """Return to the previous step in the application."""
    st.session_state.step -= 1
    st.rerun()
