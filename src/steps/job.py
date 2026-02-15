"""Module for rendering the job target step in the application."""

import streamlit as st

from services.job_service import JobService
from state_manager import state_manager


def render_job_step():
    """Render the job target step UI."""
    st.subheader("Step 3: Target Job Context")

    job = state_manager.job

    def handle_scrape():
        url = st.session_state.job_url_input
        if url:
            with st.spinner("Scraping job description..."):
                try:
                    content = JobService.scrape_job(url)
                    state_manager.update_job(url=url, description=content)
                    st.success("Successfully scraped job description!")
                except Exception as e:
                    st.error(f"Failed to scrape job: {str(e)}")
        else:
            st.warning("Please enter a LinkedIn URL first.")

    def on_text_change():
        text = st.session_state.job_text_input
        if text != job.description:
            state_manager.update_job(description=text)

    with st.container(border=True):
        st.markdown("**Option 1: Paste LinkedIn URL**")
        url_col, btn_col = st.columns([4, 1])
        with url_col:
            st.text_input(
                "LinkedIn Job URL",
                placeholder="https://www.linkedin.com/jobs/view/...",
                key="job_url_input",
                value=job.url,
                label_visibility="collapsed",
            )
        with btn_col:
            st.button("Scrape 🔍", on_click=handle_scrape, use_container_width=True)

        st.markdown("**Option 2: Paste Job Description**")
        st.text_area(
            "Job Description Text",
            height=200,
            placeholder="Paste the full job description here...",
            key="job_text_input",
            on_change=on_text_change,
            value=job.description,
        )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            state_manager.prev_step()
    with col2:
        disabled = not job.description
        if st.button("Next: Assemble Board ➡️", type="primary", disabled=disabled, use_container_width=True):
            state_manager.next_step()
