"""Module for rendering the team assembly step in the application."""

import streamlit as st

from persona_utils import load_personas
from session_utils import next_step, prev_step


def _handle_custom_specialist():
    """Handle UI for adding a custom specialist agent."""
    with st.expander("🛠️ Add Custom Specialist (Advanced)", expanded=False):
        st.write("Create your own agent with a specific perspective.")
        st.info("💡 **Examples:** 'Industry Historian', 'Behavioral Psychologist', 'Negotiation Expert'")

        new_name = st.text_input("Specialist Role", placeholder="e.g., Strategic Hiring Manager")
        new_prompt = st.text_area(
            "Analysis Instructions",
            placeholder=(
                "Analyze the CV for long-term growth potential and alignment with Fortune 500 " "leadership standards..."
            ),
        )
        if st.button("Add Specialist"):
            if new_name and new_prompt:
                st.session_state.custom_agents.append({"name": new_name, "prompt": new_prompt})
                st.rerun()


def render_team_step():
    """Render the team selection step UI."""
    st.header("Step 4: Assemble Your Personal Board")
    st.markdown("Select the AI experts who will critique your CV.")

    all_available_personas = load_personas()
    matchmaker_key = next((k for k in all_available_personas.keys() if "LinkedIn Matchmaker" in k), None)

    has_job_context = bool(st.session_state.job_url or st.session_state.job_text)

    # --- Pre-selection Logic ---
    # Only initialize if NOT in session state to avoid overwriting user changes
    if "selected_persona_names" not in st.session_state:
        st.session_state.selected_persona_names = []
        if matchmaker_key and has_job_context:
            st.session_state.selected_persona_names = [matchmaker_key]

    # --- Display Options Setup ---
    display_options = []
    option_mapping = {}
    for k in all_available_personas.keys():
        label = k
        if k == matchmaker_key:
            label = f"⭐ {k} (Recommended)"
        display_options.append(label)
        option_mapping[label] = k

    # --- Multiselect Configuration ---
    # Convert current stored keys to labels for the `default` parameter.
    # CRITICAL: We use `default` only for initial render or when state is cleared.
    # Streamlit's widget state persistence handles the rest if key is stable.
    current_defaults = [label for label, key in option_mapping.items() if key in st.session_state.selected_persona_names]

    # Use a callback or simply read the return value.
    # Reading return value is standard but can cause the "reset" issue if `default` changes
    # between reruns in a way that conflicts with internal widget state.
    # However, since `current_defaults` is derived from session_state, it should be stable.

    selected_labels = st.multiselect(
        "Select Board Members", options=display_options, default=current_defaults, key="team_multiselect"
    )

    # --- State Synchronization ---
    # Only update session state if the widget value differs from what we expect
    new_selected_keys = [option_mapping[label] for label in selected_labels]

    # Check for difference to avoid infinite rerender loops if we were to rerun
    if new_selected_keys != st.session_state.selected_persona_names:
        st.session_state.selected_persona_names = new_selected_keys

        # Sync the custom_agents list immediately
        current_manual_agents = [
            agent
            for agent in st.session_state.custom_agents
            if not any(agent["name"] == p["name"] for p in all_available_personas.values())
        ]
        new_persona_agents = [all_available_personas[name].copy() for name in new_selected_keys]
        st.session_state.custom_agents = new_persona_agents + current_manual_agents

        # Force a rerun to ensure the UI reflects the new state immediately (e.g. the list below)
        st.rerun()

    _handle_custom_specialist()

    st.subheader("Current Team")
    if not st.session_state.custom_agents:
        st.warning("No agents selected.")
    else:
        for agent in st.session_state.custom_agents:
            st.success(f"👤 **{agent['name']}**")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        if st.button(
            "🚀 Start Analysis ➡️",
            type="primary",
            disabled=not st.session_state.custom_agents,
            use_container_width=True,
        ):
            next_step()
