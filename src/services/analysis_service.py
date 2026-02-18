from typing import Any, Callable, List, Optional, Tuple

from crewai import LLM, Agent, Crew, Process, Task

from logger import logger
from models import AppConfig, Persona
from prompts import (
    BOARD_HEAD_BACKSTORY,
    BOARD_HEAD_TASK_DESCRIPTION,
    OPTIMIZER_AGENT_BACKSTORY,
    OPTIMIZER_TASK_DESCRIPTION,
    REFORMATTER_AGENT_BACKSTORY,
    REFORMATTER_TASK_DESCRIPTION,
)


class AnalysisService:
    @staticmethod
    def _configure_llm(config: AppConfig) -> LLM:
        """Configures the LLM environment and returns the LLM instance."""
        if config.llm_provider == "Google":
            return LLM(model=f"gemini/{config.selected_model}", api_key=config.api_key)
        else:
            # For OpenAI, CrewAI expects "gpt-4o" or "openai/gpt-4o"
            return LLM(model=config.selected_model, api_key=config.api_key)

    @staticmethod
    def _create_specialist_agents(
        personas: List[Persona], cv_content: str, job_description: str, model: LLM
    ) -> Tuple[List[Agent], List[Task]]:
        """Creates specialist agents and their analysis tasks."""
        agents = []
        tasks = []

        for persona in personas:
            backstory = persona.backstory
            if "{job_description}" in backstory:
                backstory = backstory.format(job_description=job_description)

            specialist_agent = Agent(
                role=persona.name,
                goal=persona.goal,
                backstory=backstory,
                llm=model,
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

        return agents, tasks

    @staticmethod
    def create_analysis_crew(
        selected_personas: List[Persona],
        cv_content: str,
        job_description: str,
        config: AppConfig,
        user_answers: str = "",
        task_callback: Optional[Callable[[Any], None]] = None,
    ) -> Crew:
        """Creates and configures a CrewAI crew for CV analysis using domain models."""

        logger.info(f"Creating analysis crew with {len(selected_personas)} specialists...")

        crew_model = AnalysisService._configure_llm(config)

        agents = []
        tasks = []

        # 1. Specialist Agents
        specialist_agents, specialist_tasks = AnalysisService._create_specialist_agents(
            selected_personas, cv_content, job_description, crew_model
        )
        agents.extend(specialist_agents)
        tasks.extend(specialist_tasks)

        # 2. Board Head (Synthesizer)
        board_head = Agent(
            role="Board Head for CV Excellence",
            goal="Synthesize all specialist findings into one final actionable recommendation",
            backstory=BOARD_HEAD_BACKSTORY,
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        final_recommendation_task = Task(
            description=BOARD_HEAD_TASK_DESCRIPTION,
            expected_output="A comprehensive board recommendation report focusing on critique and strategic advice.",
            agent=board_head,
            context=specialist_tasks,  # Use specialist tasks as context
            callback=task_callback,
        )
        agents.append(board_head)
        tasks.append(final_recommendation_task)

        # 3. Minimal Changes Agent
        optimizer_agent = Agent(
            role="Targeted Resume Optimizer",
            goal="Identify specific keywords and phrasing tweaks to align with the job description.",
            backstory=OPTIMIZER_AGENT_BACKSTORY,
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        optimization_task = Task(
            description=OPTIMIZER_TASK_DESCRIPTION.format(
                cv_content_snippet=cv_content[:15000], job_description=job_description
            ),
            expected_output="A conversational list of high-impact advice and specific phrasing recommendations.",
            agent=optimizer_agent,
            callback=task_callback,
        )
        agents.append(optimizer_agent)
        tasks.append(optimization_task)

        # 4. Reformatter Agent (Final CV)
        reformatter_agent = Agent(
            role="Expert CV Reformatter",
            goal="Rewrite the candidate CV into a professional, modern Markdown format incorporating board feedback.",
            backstory=REFORMATTER_AGENT_BACKSTORY,
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        reformat_task = Task(
            description=REFORMATTER_TASK_DESCRIPTION.format(cv_content_snippet=cv_content[:15000], user_answers=user_answers),
            expected_output="The complete, polished CV with all original sections and minimal improvements, formatted in clean Markdown.",
            agent=reformatter_agent,
            context=[optimization_task],
            callback=task_callback,
        )
        agents.append(reformatter_agent)
        tasks.append(reformat_task)

        # Speed Optimization: Disable memory to speed up processing
        analysis_crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            embedder=(
                {"provider": "google", "config": {"model": "models/embedding-001"}}
                if config.llm_provider == "Google"
                else None
            ),
        )

        logger.info("Analysis crew successfully created.")
        return analysis_crew
