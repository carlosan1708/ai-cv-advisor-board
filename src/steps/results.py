"""Module for rendering the results step in the application."""

import os

import streamlit as st

from crew_logic import create_crew
from pdf_utils import generate_pdf
from scraper import scrape_linkedin_job
from session_utils import reset_app


def _fetch_job_description():
    """Fetch job description from LinkedIn URL or fallback to manual text."""
    final_job_desc = ""
    if st.session_state.job_url:
        with st.status("Fetching Job Details...", expanded=True) as status:
            try:
                status.write("Connecting to LinkedIn...")
                final_job_desc = scrape_linkedin_job(st.session_state.job_url)
                status.update(label="Job Details Fetched!", state="complete")
            except Exception as e:
                status.update(label="Scraping Failed, using fallback.", state="error")
                st.error(f"Error scraping LinkedIn: {e}")
                final_job_desc = st.session_state.job_text
    elif st.session_state.job_text:
        final_job_desc = st.session_state.job_text
    return final_job_desc


def _run_analysis():
    """Execute the CV analysis using CrewAI."""
    st.session_state.job_description = _fetch_job_description()
    try:
        with st.spinner("Analyzing CV against Job Description..."):
            app = create_crew(
                st.session_state.custom_agents,
                st.session_state.cv_content,
                st.session_state.job_description,
                st.session_state.api_key,
                st.session_state.selected_model,
                st.session_state.llm_provider,
                user_answers="",
            )
            st.session_state.crew_result = app.kickoff()
            st.session_state.board_agents = [a.role for a in app.agents]
            st.rerun()
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        if st.button("Try Again"):
            st.rerun()
        st.stop()


def _render_download_section(cv_markdown):
    """Render download buttons for optimized CV."""
    pdf_enabled = os.getenv("ENABLE_PDF_EXPORT", "false").lower() == "true"
    if pdf_enabled:
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 Download Markdown",
                data=cv_markdown,
                file_name="optimized_cv.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_b:
            pdf_data = generate_pdf(cv_markdown)
            if pdf_data:
                st.download_button(
                    "📥 Download PDF",
                    data=pdf_data,
                    file_name="optimized_cv.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    else:
        st.download_button(
            "📥 Download Optimized CV (Markdown)",
            data=cv_markdown,
            file_name="optimized_cv.md",
            mime="text/markdown",
            use_container_width=True,
        )


def _sanitize_markdown(content):
    """Clean markdown artifacts from LLM output."""
    if content.startswith("```markdown"):
        return content.replace("```markdown", "", 1).rsplit("```", 1)[0]
    if content.startswith("```"):
        return content.replace("```", "", 1).rsplit("```", 1)[0]
    return content


def render_results_step():
    """Render the results step UI."""
    if st.session_state.crew_result is None:
        st.header("⏳ Board is Deliberating...")
        _run_analysis()
    else:
        st.header("📋 Board Recommendation")

        tabs_list = ["📋 Recommendations", "🔍 Detailed Analysis"]
        if st.session_state.interview_done:
            tabs_list.append("📄 Optimized CV")

        tabs = st.tabs(tabs_list)

        with tabs[0]:
            with st.container(border=True):
                st.subheader("Board Strategy & Critique")
                report_content = _sanitize_markdown(st.session_state.crew_result.tasks_output[-2].raw)
                st.markdown(report_content)

        with tabs[1]:
            for i, task_output in enumerate(st.session_state.crew_result.tasks_output[:-2]):
                agent_name = "Unknown Specialist"
                if i < len(st.session_state.board_agents):
                    agent_name = st.session_state.board_agents[i]
                with st.expander(f"👤 {agent_name} - Perspective"):
                    st.write(task_output.raw)

        if len(tabs) > 2:
            with tabs[2]:
                st.subheader("📄 Professional Optimized CV")
                cv_markdown = _sanitize_markdown(st.session_state.crew_result.tasks_output[-1].raw)
                st.markdown(cv_markdown)
                _render_download_section(cv_markdown)

        st.divider()
        if not st.session_state.interview_done:
            st.info("💡 **Ready to transform your CV?** The Board can rewrite it using your real-world achievements.")
            if st.button("🚀 Next: Personalize (Optional) ➡️", type="primary", use_container_width=True):
                st.session_state.step = 6
                st.rerun()

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 New Analysis", use_container_width=True):
                reset_app()
        with col2:
            st.download_button(
                "📥 Download Report",
                data=str(st.session_state.crew_result.raw),
                file_name="cv_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
