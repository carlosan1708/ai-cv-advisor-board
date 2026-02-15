"""Module for rendering the welcome step in the application."""

import streamlit as st

from state_manager import state_manager


def render_welcome_step():
    """Render the welcome screen UI."""
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <h1>🚀 Elevate Your Career with AI</h1>
            <p style="font-size: 1.2rem; color: #555;">
                Welcome to the <b>AI - CV Advisor Board</b>. Get expert feedback and a personalized,
                high-impact CV tailored to your dream job.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 👤 **The Board**")
        st.write("Assemble a custom board of AI experts—from Tech Recruiters to Startup Founders.")

    with col2:
        st.markdown("### 🔍 **Smart Critique**")
        st.write("Receive deep, specialized analysis of your CV against a specific job description.")

    with col3:
        st.markdown("### ✨ **Personalized CV**")
        st.write("Participate in an optional AI interview to inject real achievements into a " "reformatted document.")

    st.write("")
    st.write("")

    st.info("💡 **How it works:** Configuration -> Upload -> Job Context -> Team Selection -> expert Results.")

    if st.button("Get Started ➡️", use_container_width=True, type="primary"):
        state_manager.next_step()
