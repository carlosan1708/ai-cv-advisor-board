"""Module for rendering the system configuration step in the application."""

import streamlit as st

from llm_utils import get_available_models
from session_utils import CHEAP_MODELS, get_env_api_key, get_is_online, next_step

# --- Callbacks ---
# We define callbacks outside the render function to keep state logic clean


def on_provider_change():
    """Callback when provider changes."""
    new_provider = st.session_state.online_provider_select if get_is_online() else st.session_state.offline_provider_select

    if new_provider != st.session_state.llm_provider:
        st.session_state.llm_provider = new_provider

        # Reset API key logic based on mode
        if not get_is_online():
            st.session_state.api_key = get_env_api_key(new_provider)
        else:
            # Online mode: Clear custom key input
            st.session_state.api_key = ""

        # Reset model
        st.session_state.selected_model = CHEAP_MODELS.get(new_provider, "")

        # Clear cache
        if "available_models" in st.session_state:
            del st.session_state.available_models


def on_api_key_change():
    """Callback when API key input changes."""
    # Logic depends on mode slightly for where we read the key from
    key_widget = "online_api_key_input" if get_is_online() else "offline_api_key_input"
    new_key = st.session_state.get(key_widget, "")

    # Store previous value to check if it actually changed
    prev_key = st.session_state.get("api_key", "")

    if new_key != prev_key:
        st.session_state.api_key = new_key
        if "available_models" in st.session_state:
            del st.session_state.available_models


def on_model_change():
    """Callback when model selection changes."""
    st.session_state.selected_model = st.session_state.model_selector


# --- Helper Functions ---


def _ensure_defaults():
    """Ensure session state has necessary defaults."""
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "Google"

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = CHEAP_MODELS.get(st.session_state.llm_provider, "")

    # In online mode, we might need to initialize api_key if not set
    if get_is_online() and "api_key" not in st.session_state:
        st.session_state.api_key = ""  # Start empty, use system fallback later


def _fetch_models_logic(api_key_to_use):
    """Core logic to fetch models without UI side effects."""
    if not api_key_to_use:
        return []

    cache_key = f"{st.session_state.llm_provider}_{api_key_to_use}"

    # Return cached if valid
    if (
        st.session_state.get("last_api_cache_key") == cache_key
        and "available_models" in st.session_state
        and st.session_state.available_models
    ):
        return st.session_state.available_models

    # Fetch new
    try:
        models = get_available_models(api_key_to_use, st.session_state.llm_provider)
        st.session_state.available_models = models
        st.session_state.last_api_cache_key = cache_key
        return models
    except Exception:
        return []


def render_config_step():
    """Render the configuration step UI."""
    _ensure_defaults()

    st.header("Step 1: System Configuration")

    is_online = get_is_online()

    # --- Section 1: Provider & Key Input ---

    if is_online:
        gemini_model = st.session_state.get("selected_model", "Unknown")
        st.success(f"System is pre-configured with **{gemini_model}** and ready to go!")

        with st.expander("🛠️ Advanced: Change Provider / Custom API Key", expanded=False):
            st.subheader("Provider Selection")
            st.radio(
                "Select AI Provider",
                options=["Google", "OpenAI"],
                horizontal=True,
                index=0 if st.session_state.llm_provider == "Google" else 1,
                key="online_provider_select",
                on_change=on_provider_change,
            )

            st.subheader("Custom API Key (Optional)")
            st.markdown("If you prefer to use your own API key, enter it below. otherwise, the system default will be used.")

            # Logic for input default value
            current_val = st.session_state.get("api_key", "")
            system_key = get_env_api_key(st.session_state.llm_provider)
            # If internal key matches system key, show empty in UI to hide it
            if current_val == system_key:
                current_val = ""

            st.text_input(
                f"Enter your {st.session_state.llm_provider} API Key",
                type="password",
                value=current_val,
                help=f"Leave empty to use the system's default key.",
                key="online_api_key_input",
                on_change=on_api_key_change,
            )

    else:
        st.info("Let's get your AI environment set up first.")
        with st.container(border=True):
            st.subheader("🔑 Provider Selection")
            st.radio(
                "Select AI Provider",
                options=["Google", "OpenAI"],
                horizontal=True,
                index=0 if st.session_state.llm_provider == "Google" else 1,
                key="offline_provider_select",
                on_change=on_provider_change,
            )

            st.text_input(
                f"Enter your {st.session_state.llm_provider} API Key",
                type="password",
                value=st.session_state.get("api_key", ""),
                help=f"Required to access {st.session_state.llm_provider} models.",
                key="offline_api_key_input",
                on_change=on_api_key_change,
            )

    # --- Section 2: Model Fetching & Selection ---

    # Determine which key to actually USE for fetching
    active_key = st.session_state.get("api_key", "")

    # Strictly define what counts as a custom key
    system_key = get_env_api_key(st.session_state.llm_provider)
    has_custom_key = bool(active_key) and active_key != system_key

    # If online and NO custom key, use system key
    if is_online and not has_custom_key:
        active_key = system_key

    available_models = []

    # Only fetch if we have a key
    if active_key:
        cache_key = f"{st.session_state.llm_provider}_{active_key}"
        is_cached = st.session_state.get("last_api_cache_key") == cache_key

        if not is_cached:
            with st.spinner(f"Validating {st.session_state.llm_provider} API Key..."):
                available_models = _fetch_models_logic(active_key)
        else:
            available_models = st.session_state.get("available_models", [])

    # Render Selectbox if models exist
    if available_models:
        st.success(f"{st.session_state.llm_provider} API Key Validated!")

        # Ensure current selection is valid
        current_selection = st.session_state.get("selected_model")
        if current_selection not in available_models:
            cheap_model = CHEAP_MODELS.get(st.session_state.llm_provider)
            current_selection = cheap_model if cheap_model in available_models else available_models[0]
            st.session_state.selected_model = current_selection

        try:
            default_index = available_models.index(current_selection)
        except ValueError:
            default_index = 0

        # FORCE LOCKING:
        # If is_online is true, it is ALWAYS disabled unless has_custom_key is explicitly true.
        lock_it = is_online and not has_custom_key

        st.selectbox(
            f"Select {st.session_state.llm_provider} Model",
            options=available_models,
            index=default_index,
            key="model_selector",
            on_change=on_model_change,
            disabled=lock_it,
            help="Locked to default in Online Mode unless you provide a custom API key." if lock_it else "Choose model.",
        )

        cheap_model = CHEAP_MODELS.get(st.session_state.llm_provider)
        if st.session_state.selected_model != cheap_model:
            st.info(f"Note: **{cheap_model}** is recommended for cost-efficiency.")

    elif active_key:
        st.error("Invalid API Key or no models available.")

    # --- Section 3: Navigation ---

    st.write("---")
    col1, col2 = st.columns([1, 4])
    with col2:
        is_valid = bool(available_models) and bool(st.session_state.get("selected_model"))

        if st.button(
            "Next: Upload CV ➡️", type="primary", disabled=not is_valid, use_container_width=True, key="config_next_btn"
        ):
            next_step()
