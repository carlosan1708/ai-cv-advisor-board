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
    st.subheader("Step 5: Board Recommendations")

    if not state_manager.crew_result:
        # Show summary of selection
        # Collect all specialists names
        predefined = state_manager.selected_persona_names
        custom = [a["name"] for a in state_manager.custom_agents]
        all_specialists = predefined + custom

        st.markdown(
            """
        ### Analysis Summary
        The following specialists will analyze your CV:
        """
        )

        # Display as a bulleted list or comma separated
        if all_specialists:
            st.markdown("- " + "\n- ".join(all_specialists))
        else:
            st.warning("No specialists selected. Please go back and choose at least one.")

        st.info("Click the button below to start the analysis.")

        st.warning(
            "⏳ **Note:** The process could take up to **2 minutes** depending on the complexity of your CV. "
            "The more specialists you selected, the longer it will take."
        )

        is_ready = len(all_specialists) > 0
        if st.button("🚀 Start Board Review", type="primary", use_container_width=True, disabled=not is_ready):
            _run_analysis()

        if st.button("⬅️ Back to Team Selection", use_container_width=True):
            state_manager.prev_step()
        return

    # Results available
    result = state_manager.crew_result

    # In CrewAI, result.tasks_output contains the output of each task
    # Our tasks: [...specialists, board_head, optimization, reformat]
    tasks_output = getattr(result, "tasks_output", [])

    # Safely extract outputs
    # Last task is Reformatter
    final_cv = tasks_output[-1].raw if len(tasks_output) >= 1 else str(result)
    # Second to last is Optimization
    minimal_changes = tasks_output[-2].raw if len(tasks_output) >= 2 else "Optimization data not found."
    # Third to last is Board Head (Synthesized Report)
    board_report = tasks_output[-3].raw if len(tasks_output) >= 3 else str(result)

    # Clean up markdown outputs to remove code blocks if present
    def clean_output(text):
        if not isinstance(text, str):
            return str(text)
        text = text.strip()
        if text.startswith("```markdown"):
            text = text[11:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    final_cv = clean_output(final_cv)
    minimal_changes = clean_output(minimal_changes)
    board_report = clean_output(board_report)

    st.success("Analysis Complete!")

    tabs = st.tabs(["📋 Board Report", "🛠️ Minimal Changes", "📄 PDF Generated"])

    with tabs[0]:
        st.markdown(board_report)

    with tabs[1]:
        st.info("Specific keywords and phrasing tweaks identified by the board.")
        st.markdown(minimal_changes)

    with tabs[2]:
        # PDF Download - Moved to Top
        pdf_bytes = CVService.generate_pdf(final_cv)
        if pdf_bytes:
            st.download_button(
                label="📥 Download Generated PDF",
                data=pdf_bytes,
                file_name="Optimized_CV.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )

        st.warning(
            "⚠️ **Highlight:** Some of the changes performed here might not adjust to the reality of your skills. "
            "I recommend to review the board recommendations and customize it based on real experience."
        )

        st.info(
            "💡 **Note:** The text below is a preview. The **Downloaded PDF** will have a professional layout and formatting."
        )
        st.markdown(final_cv)

        if pdf_bytes:
            st.caption("👉 For a full rewrite tailored to your interview answers, use the **Personalize** step below.")

    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Start Over", use_container_width=True):
            state_manager.reset()
    with col2:
        if st.button("⬅️ Step Back", use_container_width=True):
            state_manager.crew_result = None
            st.rerun()
    with col3:
        if st.button("✨ Personalize (WIP) ➡️", type="primary", use_container_width=True):
            state_manager.next_step()
