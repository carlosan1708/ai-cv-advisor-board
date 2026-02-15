"""Reusable UI components for the AI CV Advisory Board application."""

import streamlit as st

STEPS = [
    {"label": "Setup"},
    {"label": "Upload"},
    {"label": "Job"},
    {"label": "Team"},
    {"label": "Results"},
]


def render_stepper(current_step):
    """Render a step-by-step progress indicator.

    Args:
        current_step: The current step number (1-indexed).
    """
    cols = st.columns(len(STEPS))
    for i, (col, step) in enumerate(zip(cols, STEPS)):
        step_num = i + 1
        with col:
            if current_step == step_num:
                st.markdown(f"**🔷 {step['label']}**")
                st.progress(100)
            elif current_step > step_num:
                st.markdown(f"**✅ {step['label']}**")
                st.progress(100)
            else:
                st.markdown(f"<span style='color: #888;'>⚪ {step['label']}</span>", unsafe_allow_html=True)
                st.progress(0)
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)


def render_header():
    """Render the application header."""
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>AI - CV Advisory Board</h1>", unsafe_allow_html=True)


def render_footer():
    """Render the application footer."""
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.7rem; color: #888; margin-bottom: 5px;">
            Author: <a href="https://linkedin.com/in/carlosan1708" target="_blank">linkedin/carlosan1708</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Buy Me a Coffee Button
    bmc_button = """
    <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="carlosan1708" data-color="#FFDD00" data-emoji="☕"  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
    """
    st.components.v1.html(
        f"""
        <div style="display: flex; justify-content: center; transform: scale(0.8); transform-origin: center top;">
            {bmc_button}
        </div>
        """,
        height=55,
    )
