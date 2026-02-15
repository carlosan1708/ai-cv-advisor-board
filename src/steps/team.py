"""Module for rendering the team selection step in the application."""

import streamlit as st

from services.persona_service import PersonaService
from state_manager import state_manager


def _handle_custom_specialist():
    """Handle adding a custom specialist persona."""
    with st.expander("➕ Add Custom Specialist", expanded=False):
        custom_name = st.text_input("Specialist Name (e.g., 'Google Senior Engineer')")
        custom_prompt = st.text_area(
            "What should this specialist focus on?",
            help="Describe the persona's background and what they should look for in the CV.",
        )
        if st.button("Add to Board"):
            if custom_name and custom_prompt:
                # Add to custom_agents in session_state via state_manager
                # Note: We still use session_state for some temporary UI lists,
                # but we'll manage the core 'custom_agents' through state_manager
                new_agent = {"name": custom_name, "prompt": custom_prompt}
                state_manager.custom_agents.append(new_agent)
                st.success(f"Added {custom_name} to the board!")
                st.rerun()


def render_team_step():
    """Render the team selection step UI."""
    st.subheader("Step 4: Assemble Your Board")

    # Load personas using PersonaService
    available_personas = PersonaService.load_personas()

    if not available_personas:
        st.error("No personas found. Please check the 'personas' directory.")
        return

    st.markdown("**Choose your specialists** (Select 2-3 for balanced review)")

    # Create a container for the checkboxes
    # We use a copy of the list to avoid modifying it while iterating if needed,
    # but here we build a new list based on checkbox states.

    # We need to maintain the selection state across reruns.
    # The checkbox widget handles its own state if we provide a key.
    # However, to sync with state_manager.selected_persona_names, we need to handle the logic.

    current_selection = state_manager.selected_persona_names
    new_selection = []

    with st.container():
        for name, persona in available_personas.items():
            # Check if this persona is currently in the selected list
            is_selected = name in current_selection

            # Use a checkbox for each persona
            # Key must be unique for each checkbox
            checked = st.checkbox(f"**{name}**", value=is_selected, key=f"chk_{name}", help=persona.backstory)

            if checked:
                new_selection.append(name)

    # Update state_manager with the new selection list
    state_manager.selected_persona_names = new_selection

    # Map selected names back to Persona objects for the board
    selected_personas = [available_personas[name] for name in new_selection]
    st.session_state.board_agents = selected_personas  # Keep for crew_logic

    _handle_custom_specialist()

    if state_manager.custom_agents:
        st.subheader("Your Custom Specialists")
        for idx, agent in enumerate(state_manager.custom_agents):
            col1, col2 = st.columns([4, 1])
            col1.write(f"👤 **{agent['name']}**")
            if col2.button("🗑️", key=f"del_{idx}"):
                state_manager.custom_agents.pop(idx)
                st.rerun()

    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            state_manager.prev_step()
    with col2:
        # Require at least one specialist (either pre-defined or custom)
        is_ready = len(new_selection) > 0 or len(state_manager.custom_agents) > 0
        if st.button("Next: Run Analysis ➡️", type="primary", disabled=not is_ready, use_container_width=True):
            state_manager.next_step()
