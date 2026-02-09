from crewai import Agent, Task, Crew, Process
import os
import streamlit as st
import textwrap
from typing import List, Dict, Any

def create_crew(
    custom_agents_data: List[Dict[str, str]], 
    cv_content: str, 
    job_description: str, 
    api_key: str, 
    model: str, 
    provider: str = "Google"
) -> Crew:
    """
    Creates and configures a CrewAI crew for CV analysis.
    
    Args:
        custom_agents_data: List of agent personas (name and prompt).
        cv_content: The text content of the candidate's CV.
        job_description: The target job description (optional).
        api_key: API key for the LLM provider.
        model: Model name to use.
        provider: "Google" or "OpenAI".
        
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

    # 1. Market Trends Specialist
    trends_agent = Agent(
        role='Market Trends Expert',
        goal='Identify modern CV best practices and role-specific trends',
        backstory=textwrap.dedent("""
            You are an expert in the current job market, specializing in ATS optimization 
            and modern resume standards for 2024-2026.
        """),
        llm=crew_model,
        verbose=True,
        allow_delegation=False
    )
    
    trends_task = Task(
        description=f"Analyze modern CV standards for 2026 relevant to this candidate: {cv_content[:1000]}",
        expected_output="A report on modern CV standards and keywords for the candidate's target role.",
        agent=trends_agent
    )
    
    agents.append(trends_agent)
    tasks.append(trends_task)

    # 2. RAG Specialist (if enabled)
    if rag_enabled and "vectorstore" in st.session_state and st.session_state.vectorstore:
        collection = st.session_state.vectorstore
        # Query ChromaDB directly
        results = collection.query(
            query_texts=[cv_content[:2000]],
            n_results=3
        )
        context = "\n\n".join(results['documents'][0]) if results['documents'] else "No matching examples found."
        
        rag_agent = Agent(
            role='CV Benchmarking Specialist',
            goal='Compare the candidate CV against successful examples',
            backstory='You have access to a library of successful CVs and identify patterns that lead to hires.',
            llm=crew_model,
            verbose=True,
            allow_delegation=False
        )
        
        rag_task = Task(
            description=f"Compare this CV: {cv_content[:1000]} with these successful examples: {context}. Identify missing patterns.",
            expected_output="An analysis of how the candidate matches successful CV patterns.",
            agent=rag_agent
        )
        agents.append(rag_agent)
        tasks.append(rag_task)

    # 3. Custom Council Members (Specialists)
    for agent_data in custom_agents_data:
        try:
            formatted_prompt = agent_data['prompt'].format(job_description=job_description)
        except Exception:
            formatted_prompt = agent_data['prompt']
            
        specialist_agent = Agent(
            role=agent_data['name'],
            goal=f"Provide specialized analysis based on your persona: {agent_data['name']}",
            backstory=formatted_prompt,
            llm=crew_model,
            verbose=True,
            allow_delegation=False
        )
        
        specialist_task = Task(
            description=f"Analyze the candidate's CV: {cv_content[:2000]} based on your expertise. Consider the job description: {job_description}",
            expected_output=f"A detailed critique from the perspective of a {agent_data['name']}.",
            agent=specialist_agent,
            context=tasks
        )
        agents.append(specialist_agent)
        tasks.append(specialist_task)

    # 4. Council Head
    council_head = Agent(
        role='Council Head for CV Excellence',
        goal='Synthesize all specialist findings into one final actionable recommendation',
        backstory='You are the leader of the CV Excellence Council. Your job is to take all reports and create a definitive guide for the candidate.',
        llm=crew_model,
        verbose=True,
        allow_delegation=False # Disable delegation to avoid potential failures and retries
    )
    
    final_task = Task(
        description=textwrap.dedent("""
            Review all specialist reports and the original CV. 
            Provide a final recommendation including: 
            - Executive Summary
            - Specialist Summaries (brief)
            - Key Strengths
            - Critical Missing Elements
            - Actionable Next Steps
            - Final Verdict
            
            Use rich markdown formatting. Use H2 and H3 headers, bullet points, and bold text for emphasis.
            If appropriate, use a table for the final verdict summary.
        """),
        expected_output="A comprehensive and well-formatted final recommendation report in Markdown.",
        agent=council_head,
        context=tasks
    )
    agents.append(council_head)
    tasks.append(final_task)

    cv_crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    
    return cv_crew
