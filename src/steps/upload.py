"""Module for rendering the CV upload step in the application."""

import streamlit as st
from pypdf import PdfReader

from session_utils import next_step, prev_step


def render_upload_step():
    """Render the CV upload step UI."""
    st.header("Step 2: Upload Your CV")
    st.markdown("Upload the Resume/CV you want to analyze.")

    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

        if uploaded_file:
            if uploaded_file.name != st.session_state.cv_filename:
                with st.spinner("Reading file..."):
                    if uploaded_file.name.endswith(".pdf"):
                        reader = PdfReader(uploaded_file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()
                        st.session_state.cv_content = content
                    else:
                        st.session_state.cv_content = uploaded_file.read().decode("utf-8")
                    st.session_state.cv_filename = uploaded_file.name

            st.success(f"✅ Successfully loaded: **{st.session_state.cv_filename}**")
            st.markdown(f"**Preview:** {st.session_state.cv_content[:200]}...")

    st.write("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        disabled = not st.session_state.cv_content
        if st.button("Next: Job Target ➡️", type="primary", disabled=disabled, use_container_width=True):
            next_step()
