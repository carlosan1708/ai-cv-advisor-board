"""Module for rendering the analysis results step in the application."""

import streamlit as st

from logger import logger
from services.analysis_service import AnalysisService
from services.cv_service import CVService
from state_manager import state_manager


def _run_analysis():
    """Execute the CrewAI analysis process."""
    try:
        # Combine selected pre-defined personas and custom personas
        # available_personas are already Persona objects from team step
        selected_personas = st.session_state.get("board_agents", [])

        # Add custom personas (as Persona objects)
        from models import Persona

        for custom in state_manager.custom_agents:
            selected_personas.append(
                Persona(
                    name=custom["name"],
                    role=custom["name"],
                    goal=f"Provide specialized analysis as {custom['name']}",
                    backstory=custom["prompt"],
                )
            )

        with st.spinner("The Board is reviewing your CV... This may take a minute."):
            crew = AnalysisService.create_analysis_crew(
                selected_personas=selected_personas,
                cv_content=st.session_state.cv_content,
                job_description=state_manager.job.description,
                config=state_manager.config,
            )
            result = crew.kickoff()
            state_manager.crew_result = result
            st.rerun()
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        st.error(f"Analysis failed: {str(e)}")


def render_results_step():
    """Render the analysis results step UI."""
    st.header("Step 5: Board Recommendations")

    if not state_manager.crew_result:
        st.info("The board is ready. Click the button below to start the analysis.")
        if st.button("🚀 Start Board Review", type="primary", use_container_width=True):
            _run_analysis()

        if st.button("⬅️ Back to Team Selection", use_container_width=True):
            state_manager.prev_step()
        return

    # Results available
    result = state_manager.crew_result

    # In CrewAI v0.x, result is an object with 'raw' and 'tasks_output'
    # We'll try to find the final CV from the last task output
    final_cv = ""
    if hasattr(result, "raw"):
        # Usually the last task output is the reformatted CV
        final_cv = result.raw

    st.success("Analysis Complete!")

    tabs = st.tabs(["📋 Board Report", "✨ Optimized CV", "🛠️ Minimal Changes"])

    with tabs[0]:
        # Synthesized report is usually in the second to last task or part of the main result
        st.markdown(result.raw if hasattr(result, "raw") else str(result))

    with tabs[1]:
        st.markdown(final_cv)

        # PDF Download
        pdf_bytes = CVService.generate_pdf(final_cv)
        if pdf_bytes:
            st.download_button(
                label="📥 Download Optimized CV (PDF)",
                data=pdf_bytes,
                file_name="Optimized_CV.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with tabs[2]:
        st.info("Specific keywords and phrasing tweaks identified by the board.")
        # This would ideally be extracted from specific task outputs
        st.write("Review the 'Minimal Changes' section in the Board Report for targeted updates.")

    st.write("---")
    if st.button("🏠 Start Over", use_container_width=True):
        state_manager.reset()
