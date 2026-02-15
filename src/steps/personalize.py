"""Module for rendering the personalization/interview step in the application."""

import os

import streamlit as st
from crewai import Agent, Crew, Task


def render_personalize_step():
    """Render the personalization interview step UI."""
    st.header("Step 6: Board Interview")
    st.warning("⚠️ **Work in Progress:** The personalization engine is currently being optimized.")
    st.markdown(
        """
        The Board of Advisors can rewrite your CV into a professional, modern format.
        To make it truly impactful, they need to clarify a few details about your real-world achievements.
    """
    )

    with st.container(border=True):
        from state_manager import state_manager

        if not st.session_state.interview_questions:
            if st.button("🎤 Generate Questions", use_container_width=True, type="primary"):
                with st.spinner("Board is reviewing documents..."):
                    config = state_manager.config
                    provider = config.llm_provider
                    api_key = config.api_key
                    model = config.selected_model

                    if provider == "Google":
                        os.environ["GEMINI_API_KEY"] = api_key
                        crew_model = f"gemini/{model}"
                    else:
                        os.environ["OPENAI_API_KEY"] = api_key
                        crew_model = f"openai/{model}"

                    interviewer = Agent(
                        role="Board Interviewer",
                        goal="Identify gaps and ask 3-4 targeted questions.",
                        backstory="You are an expert recruiter gathering achievements.",
                        llm=crew_model,
                        allow_delegation=False,
                    )
                    it_task = Task(
                        description=f"Based on CV: {st.session_state.cv_content[:1500]}, ask 3 specific questions.",
                        expected_output="3 numbered questions.",
                        agent=interviewer,
                    )
                    interview_crew = Crew(agents=[interviewer], tasks=[it_task], verbose=False)
                    q_result = str(interview_crew.kickoff())
                    st.session_state.interview_questions = [
                        q.strip() for q in q_result.split("\n") if q.strip() and q.strip()[0].isdigit()
                    ][:4]
                    st.rerun()
        else:
            with st.form("interview_form_step6"):
                for i, q in enumerate(st.session_state.interview_questions):
                    st.markdown(f"**{q}**")
                    st.session_state.user_answers[f"q_{i}"] = st.text_area(
                        f"Your Answer {i + 1}", key=f"ans_step6_{i}", height=100
                    )

                if st.form_submit_button("✨ Generate Optimized CV ➡️", use_container_width=True, type="primary"):
                    with st.spinner("Board is incorporating your answers..."):
                        combined_answers = "\n".join(
                            [
                                f"Q: {q}\nA: {st.session_state.user_answers.get(f'q_{i}', '')}"
                                for i, q in enumerate(st.session_state.interview_questions)
                            ]
                        )
                        # We use AnalysisService instead of create_crew for consistency with state_manager
                        from services.analysis_service import AnalysisService
                        from services.persona_service import PersonaService

                        available_personas = PersonaService.load_personas()
                        selected_personas = [available_personas[name] for name in state_manager.selected_persona_names]

                        crew = AnalysisService.create_analysis_crew(
                            selected_personas=selected_personas,
                            cv_content=st.session_state.cv_content,
                            job_description=state_manager.job.description,
                            config=state_manager.config,
                            user_answers=combined_answers,
                        )
                        state_manager.crew_result = crew.kickoff()
                        st.session_state.interview_done = True
                        state_manager.step = 5  # Back to results
                        st.rerun()

            if st.button("Cancel & Return"):
                st.session_state.step = 5
                st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.step = 5
        st.rerun()
