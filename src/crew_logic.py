"""Logic for creating and configuring CrewAI crews for CV analysis."""

import os
import textwrap
from typing import Dict, List

import streamlit as st
from crewai import Agent, Crew, Process, Task


def create_crew(
    custom_agents_data: List[Dict[str, str]],
    cv_content: str,
    job_description: str,
    api_key: str,
    model: str,
    provider: str = "Google",
    user_answers: str = "",
) -> Crew:
    """Create and configure a CrewAI crew for CV analysis.

    Args:
        custom_agents_data: List of agent personas (name and prompt).
        cv_content: The text content of the candidate's CV.
        job_description: The target job description (optional).
        api_key: API key for the LLM provider.
        model: Model name to use.
        provider: "Google" or "OpenAI".
        user_answers: Additional details provided by the user.

    Returns:
        A configured Crew object.
    """
    # Set the API key in environment for LiteLLM (which CrewAI uses)
    if provider == "Google":
        os.environ["GEMINI_API_KEY"] = api_key
        crew_model = f"gemini/{model}"
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        crew_model = f"openai/{model}" if not model.startswith("openai/") else model

    rag_enabled = os.getenv("ENABLE_RAG", "false").lower() == "true"

    agents = []
    tasks = []

    # 1. RAG Specialist (if enabled)
    if rag_enabled and "vectorstore" in st.session_state and st.session_state.vectorstore:
        collection = st.session_state.vectorstore
        # Query ChromaDB directly
        results = collection.query(query_texts=[cv_content[:2000]], n_results=3)
        context = "\n\n".join(results["documents"][0]) if results["documents"] else "No matching examples found."

        rag_agent = Agent(
            role="CV Benchmarking Specialist",
            goal="Compare the candidate CV against successful examples",
            backstory=("You have access to a library of successful CVs and identify patterns that lead to hires."),
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        rag_task = Task(
            description=(
                f"Compare this CV: {cv_content[:1000]} with these successful examples: {context}. "
                "Identify missing patterns."
            ),
            expected_output="An analysis of how the candidate matches successful CV patterns.",
            agent=rag_agent,
        )
        agents.append(rag_agent)
        tasks.append(rag_task)

    # 3. Custom Board Members (Specialists)
    for agent_data in custom_agents_data:
        try:
            formatted_prompt = agent_data["prompt"].format(job_description=job_description)
        except (KeyError, ValueError, IndexError):
            formatted_prompt = agent_data["prompt"]

        specialist_agent = Agent(
            role=agent_data["name"],
            goal=f"Provide specialized analysis based on your persona: {agent_data['name']}",
            backstory=formatted_prompt,
            llm=crew_model,
            verbose=True,
            allow_delegation=False,
        )

        specialist_task = Task(
            description=(
                f"Analyze the candidate's CV: {cv_content[:2000]} based on your expertise. "
                f"Consider the job description: {job_description}"
            ),
            expected_output=f"A detailed critique from the perspective of a {agent_data['name']}.",
            agent=specialist_agent,
            async_execution=True,
        )
        agents.append(specialist_agent)
        tasks.append(specialist_task)

    # 4. Board Head
    board_head = Agent(
        role="Board Head for CV Excellence",
        goal="Synthesize all specialist findings into one final actionable recommendation",
        backstory=(
            "You are the leader of the AI - CV Advisor Board. Your job is to take all reports and create "
            "a definitive guide for the candidate."
        ),
        llm=crew_model,
        verbose=True,
        allow_delegation=False,  # Disable delegation to avoid potential failures and retries
    )

    final_task = Task(
        description=textwrap.dedent(
            """
            Review all specialist reports and the original CV.
            Provide a final recommendation focusing on CRITIQUE and ADVICE.
            Do NOT write the CV itself here.

            Include:
            - Executive Summary of the Board's findings.
            - Specialist Summaries (brief critique from each board member).
            - Top 3 Critical Missing Elements that are hurting the candidate's chances.
            - Strategic Advice on how to reframe experience for the target role.
            - Actionable Next Steps.

            Use rich markdown formatting. Use H2 and H3 headers, bullet points, and bold text for emphasis.
        """
        ),
        expected_output="A comprehensive board recommendation report focusing on critique and strategic advice.",
        agent=board_head,
        context=tasks,
    )
    agents.append(board_head)
    tasks.append(final_task)

    # 5. Minimal Changes Agent
    minimal_changes_agent = Agent(
        role="Targeted Resume Optimizer",
        goal=(
            "Identify ONLY the specific sections, phrases, or bullet points that need to be "
            "added, removed, or tweaked to align with the job description."
        ),
        backstory=textwrap.dedent(
            """
            You are a Resume Surgeon. You do not rewrite the whole resume. You only touch what is necessary.
            Your job is to provide a list of specific, actionable changes to the existing CV to make it pass
            ATS filters and appeal to the hiring manager for THIS specific job.

            You focus on:
            1. Keywords to add (and where).
            2. Bullet points to rephrase for impact.
            3. Irrelevant information to remove.
        """
        ),
        llm=crew_model,
        verbose=True,
        allow_delegation=False,
    )

    minimal_changes_task = Task(
        description=textwrap.dedent(
            f"""
            Analyze the original CV: {cv_content[:4000]}
            Against the Job Description: {job_description}

            Provide a list of "Minimal Changes" to optimize this CV.
            Output must be a markdown list with the following sections:

            ## 1. Keywords to Add
            - [Keyword] (Suggested location: [Section Name])

            ## 2. Phrasing Tweaks
            - **Original:** "[Original Text]"
            - **Suggested:** "[New Text]"
            - **Reason:** [Brief explanation]

            ## 3. Items to Remove
            - [Text/Section] (Reason: [Brief explanation])

            ## 4. New Bullet Points to Add
            - [New Bullet Point] (Location: [Job/Section])

            Do NOT rewrite the whole CV. Only list the changes.
        """
        ),
        expected_output="A structured markdown list of specific, minimal changes to optimize the CV.",
        agent=minimal_changes_agent,
    )
    agents.append(minimal_changes_agent)
    tasks.append(minimal_changes_task)

    # 6. Exhaustive Rewrite Agent (Full CV Reformatter)
    cv_reformatter = Agent(
        role="Expert CV Reformatter",
        goal=(
            "Rewrite the candidate CV into a professional, modern Markdown format incorporating "
            "all board feedback and PRESERVING all essential professional details."
        ),
        backstory=textwrap.dedent(
            """
            You are a professional CV writer and designer. Your primary job is to take the original CV content
            and the comprehensive feedback from the Board of Advisors to produce a highly optimized,
            clean, and professional version of the CV.

            CRITICAL: You must NOT omit any professional experience, education, or core skills from the original CV.
            Your task is to REWRITE and REFRAME them for higher impact, not to summarize or remove them.
            Ensure the output is comprehensive and matches the professional depth of the original.
        """
        ),
        llm=crew_model,
        verbose=True,
        allow_delegation=False,
    )

    reformat_task = Task(
        description=textwrap.dedent(
            f"""
            1. Review the FULL original CV: {cv_content[:4000]}
            2. Consider these additional details provided by the candidate: {user_answers}
            3. Review the Board's recommendations provided in previous tasks.
            4. Rewrite the FULL CV in Markdown using the following structure:
               # [Full Name]
               [Email] | [Phone] | [LinkedIn] | [Location]

               ## Professional Summary
               [Refined summary based on board feedback]

               ## Key Expertise
               [Comprehensive list of skills, updated with keywords]

               ## Professional Experience
               [For EVERY job in the original CV:]
               ### [Job Title] @ [Company Name]
               *[Dates]*
               - [Achievement 1 with board-suggested metrics]
               - [Achievement 2 with board-suggested metrics]
               - [Preserve all other relevant bullets, but rewrite for impact]

               ## Education
               [Preserve ALL education details]

               ## Certifications & Projects
               [Preserve ALL certifications and key projects]

            Ensure the CV is comprehensive. DO NOT cut sections to make it shorter.
            Focus on QUALITY and IMPACT of the phrasing while retaining ALL original info.
        """
        ),
        expected_output=(
            "A comprehensive, perfectly formatted, and professional CV in Markdown that " "retains all original data points."
        ),
        agent=cv_reformatter,
        context=[final_task],
    )
    agents.append(cv_reformatter)
    tasks.append(reformat_task)

    cv_crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)

    return cv_crew
