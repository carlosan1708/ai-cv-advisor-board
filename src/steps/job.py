"""Module for rendering the job selection step in the application."""

import streamlit as st

from session_utils import next_step, prev_step


def render_job_step():
    """Render the job opportunity input step UI."""
    st.header("Step 3: Target Opportunity")
    st.markdown("What job are you applying for? This context is crucial for the board.")

    tab1, tab2 = st.tabs(["🔗 LinkedIn URL", "📝 Manual Description"])

    with tab1:
        # Use on_change to avoid manual rerun loops
        def on_url_change():
            st.session_state.job_url = st.session_state.job_url_input_widget

        st.text_input(
            "Paste LinkedIn Job URL",
            value=st.session_state.job_url,
            placeholder="https://www.linkedin.com/jobs/view/...",
            key="job_url_input_widget",
            on_change=on_url_change,
        )

        if st.session_state.job_url:
            st.info("We will scrape the job details automatically.")

    with tab2:

        def on_text_change():
            st.session_state.job_text = st.session_state.job_text_input_widget

        st.text_area(
            "Paste Job Description Text",
            value=st.session_state.job_text,
            height=200,
            placeholder="Key Responsibilities, Requirements, etc.",
            key="job_text_input_widget",
            on_change=on_text_change,
        )

    # Calculate context status locally for UI responsiveness
    has_job_context = bool(st.session_state.job_url or st.session_state.job_text)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        # Optimization: The button text now changes immediately because we removed manual reruns
        # and use widget state correctly.
        btn_label = "Next: Assemble Board ➡️" if has_job_context else "Skip to Board (General Review) ➡️"

        if st.button(btn_label, type="primary", use_container_width=True, key="job_step_next_btn"):
            next_step()
