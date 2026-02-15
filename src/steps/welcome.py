"""Module for rendering the welcome step in the application."""

import streamlit as st

from state_manager import state_manager


def render_welcome_step():
    """Render the welcome screen UI."""
    st.markdown(
        """
        <div style="text-align: center; padding-top: 5px;">
            <span style="background-color: #e1f5fe; color: #01579b; padding: 2px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">MVP Version</span>
            <h2 style="margin-top: 5px; margin-bottom: 0;">🚀 Elevate Your Career with AI</h2>
            <p style="font-size: 1rem; color: #555;">
                Expert feedback and high-impact CVs tailored to your dream job.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 👤 **The Board**")
        st.write("Assemble AI experts: Tech Recruiters to Startup Founders.")

    with col2:
        st.markdown("##### 🔍 **Critique**")
        st.write("Deep, specialized analysis against a job description.")

    with col3:
        st.markdown("##### ✨ **Personalized**")
        st.write("Optional AI interview to inject real achievements.")

    st.info("💡 **Steps:** Configuration -> Upload -> Job -> Team -> Results.", icon="ℹ️")

    if st.button("Get Started ➡️", use_container_width=True, type="primary"):
        state_manager.next_step()
