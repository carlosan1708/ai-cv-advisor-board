import os
import textwrap
from typing import List

from crewai import Agent, Crew, Process, Task

from logger import logger
from models import AppConfig, Persona


class AnalysisService:
    @staticmethod
    def create_analysis_crew(
        selected_personas: List[Persona], cv_content: str, job_description: str, config: AppConfig, user_answers: str = ""
    ) -> Crew:
        """Creates and configures a CrewAI crew for CV analysis using domain models."""

        logger.info(f"Creating analysis crew with {len(selected_personas)} specialists...")

        # Configure environment for LiteLLM
        if config.llm_provider == "Google":
            os.environ["GEMINI_API_KEY"] = config.api_key
            crew_model = f"gemini/{config.selected_model}"
        else:
            os.environ["OPENAI_API_KEY"] = config.api_key
            crew_model = (
                f"openai/{config.selected_model}" if not config.selected_model.startswith("openai/") else config.selected_model
            )

        agents = []
        tasks = []

        # 1. Specialist Agents (from personas)
        for persona in selected_personas:
            backstory = persona.backstory
            if "{job_description}" in backstory:
                backstory = backstory.format(job_description=job_description)

            specialist_agent = Agent(
                role=persona.name,
                goal=persona.goal,
                backstory=backstory,
                llm=crew_model,
                verbose=True,
                allow_delegation=False,
            )

            specialist_task = Task(
                description=(
                    f"Analyze the candidate's CV: {cv_content[:15000]} based on your expertise. "
                    f"Consider the job description: {job_description}"
                ),
                expected_output=f"A detailed critique from the perspective of a {persona.name}.",
                agent=specialist_agent,
                async_execution=True,
            )
            agents.append(specialist_agent)
            tasks.append(specialist_task)

        # 2. Board Head (Synthesizer)
        board_head = Agent(
            role="Board Head for CV Excellence",
            goal="Synthesize all specialist findings into one final actionable recommendation",
            backstory=(
                "You are the leader of the AI - CV Advisory Board. Your job is to take all reports and create "
                "a definitive guide for the candidate."
            ),
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        final_recommendation_task = Task(
            description=textwrap.dedent(
                """
                Review all specialist reports and the original CV.
                Provide a final recommendation focusing on CRITIQUE and ADVICE.
                Include: Executive Summary, Specialist Summaries, Top 3 Critical Missing Elements,
                Strategic Advice, and Actionable Next Steps.
                Use rich markdown formatting.
            """
            ),
            expected_output="A comprehensive board recommendation report focusing on critique and strategic advice.",
            agent=board_head,
            context=tasks,
        )
        agents.append(board_head)
        tasks.append(final_recommendation_task)

        # 3. Minimal Changes Agent
        optimizer_agent = Agent(
            role="Targeted Resume Optimizer",
            goal="Identify specific keywords and phrasing tweaks to align with the job description.",
            backstory="You are a Resume Surgeon. You focus on keywords, impact phrasing, and removing irrelevance.",
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        optimization_task = Task(
            description=(
                f"Analyze CV: {cv_content[:15000]} against Job: {job_description}. "
                "CRITICAL: Do NOT rewrite the whole CV. Your goal is to provide a conversational yet professional list of specific recommendations. "
                "Instead of a rigid structure, write it as advice: 'You are missing X or Y keywords', 'I would recommend changing this paragraph/bullet point to this...', 'Consider removing Z because...'. "
                "Make it feel like a human expert giving quick, high-impact feedback."
            ),
            expected_output="A conversational list of high-impact advice and specific phrasing recommendations.",
            agent=optimizer_agent,
        )
        agents.append(optimizer_agent)
        tasks.append(optimization_task)

        # 4. Reformatter Agent (Final CV)
        reformatter_agent = Agent(
            role="Expert CV Reformatter",
            goal="Rewrite the candidate CV into a professional, modern Markdown format incorporating board feedback.",
            backstory=(
                "You are a professional CV writer. You preserve all professional depth while reframing for " "maximum impact."
            ),
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        reformat_task = Task(
            description=textwrap.dedent(
                f"""
                Review FULL CV: {cv_content[:15000]}
                Additional Info: {user_answers}

                YOUR GOAL: Produce a FINAL CV that is a polished version of the original.

                CRITICAL INSTRUCTIONS:
                1. PRESERVE EVERYTHING: You must include ALL sections from the original CV.
                   - **IMPORTANT**: Check the VERY END of the content for Education, Certifications, and Languages.
                   - Contact Info (Links, LinkedIn, GitHub, Email, Phone) - DO NOT OMIT.
                   - Professional Summary
                   - Experience (ALL roles, dates, and companies)
                   - Education (Degrees, Universities, Dates) - DO NOT OMIT.
                   - Skills (Technical, Soft, Tools)
                   - Projects / Publications / Awards (if present)

                2. APPLY MINIMAL CHANGES:
                   - Only integrate the specific keyword/phrasing tweaks from the 'Targeted Resume Optimizer'.
                   - Do NOT summarize or shorten descriptions unless explicitly told to.
                   - Do NOT remove any section.

                3. FORMATTING:
                   - Output CLEAN Markdown.
                   - Use `## Section Name` for headers.
                   - Use `### Role/Title` for sub-headers.
                   - Use `- ` for bullet points.
                   - Ensure links are formatted as `[Link Text](URL)`.
                   - Do NOT start with ```markdown or any code block syntax. Just return the raw markdown content.
            """
            ),
            expected_output="The complete, polished CV with all original sections and minimal improvements, formatted in clean Markdown.",
            agent=reformatter_agent,
            context=[optimization_task],
        )
        agents.append(reformatter_agent)
        tasks.append(reformat_task)

        # Speed Optimization: Use Process.hierarchical for parallel execution if multiple specialists,
        # or stick to sequential with async tasks.
        # Actually, for pure speed with independent specialists + final synthesis,
        # ensuring async_execution=True on specialists is key (already done).
        # We can also try to reduce the model overhead by setting `max_rpm` or `language` if applicable.

        # However, a common speedup is to use a specific manager_llm if hierarchical,
        # but here we use sequential with dependencies.

        # To further speed up, we can disable `memory` (if enabled by default) which adds latency.
        analysis_crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable memory to speed up processing
            embedder=(
                {"provider": "google", "config": {"model": "models/embedding-001"}}
                if config.llm_provider == "Google"
                else None
            ),
        )

        logger.info("Analysis crew successfully created.")
        return analysis_crew
