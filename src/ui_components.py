"""Reusable UI components for the AI CV Advisor Board application."""

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
    st.write("")  # Spacer
    cols = st.columns(len(STEPS))
    for i, (col, step) in enumerate(zip(cols, STEPS)):
        step_num = i + 1
        with col:
            if current_step == step_num:
                st.markdown(f"#### 🔷 {step['label']}")
                st.progress(100)
            elif current_step > step_num:
                st.markdown(f"**✅ {step['label']}**")
                st.progress(100)
            else:
                st.markdown(f"⚪ {step['label']}")
                st.progress(0)
    st.write("---")


def render_header():
    """Render the application header."""
    st.title("AI - CV Advisor Board")
