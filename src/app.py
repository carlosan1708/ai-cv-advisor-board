import streamlit as st
import os
import yaml
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, List
import operator

# --- Initial Setup ---
st.set_page_config(page_title="CV Excellence Council", layout="wide")
load_dotenv()

# Initialize session state variables
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY", "")
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.0-flash-exp"
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = []

# Debugging: Confirm library availability
try:
    import pypdf
except ImportError:
    st.error("pypdf not found in the running environment. Please run: pip install pypdf")

# --- State Definition ---
class AgentState(TypedDict):
    cv_content: str
    rag_reference_results: str
    web_best_practices: str
    # Use a dictionary to store dynamic agent results
    agent_reports: Annotated[dict, operator.ior]
    final_critique: str

# --- Side Panel: Configuration ---
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Persona Set Selection
    st.subheader("👤 Council Personas")
    
    # Use absolute path for personas directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persona_dir = os.path.join(base_dir, "personas")
    
    persona_files = {
        "General Career": os.path.join(persona_dir, "general.yaml"),
        "IT Specialist": os.path.join(persona_dir, "it_specialist.yaml")
    }
    selected_set = st.selectbox("Select Persona Set", options=list(persona_files.keys()))
    
    # Load YAML if set changed or not initialized
    if "current_persona_set" not in st.session_state or st.session_state.current_persona_set != selected_set:
        try:
            with open(persona_files[selected_set], 'r', encoding='utf-8') as f:
                persona_data = yaml.safe_load(f)
                st.session_state.custom_agents = persona_data
                st.session_state.current_persona_set = selected_set
        except Exception as e:
            st.error(f"Error loading personas: {e}")

    st.divider()
    
    # Load default from .env if available
    default_api_key = os.getenv("GOOGLE_API_KEY", "")
    google_api_key = st.text_input("Google API Key", type="password", value=default_api_key)
    
    col_save, col_reset = st.columns(2)
    with col_save:
        if st.button("Save Config"):
            st.session_state.google_api_key = google_api_key
            # Refresh model list when API key is saved
            if "available_models" in st.session_state:
                del st.session_state.available_models
            st.success("API Key saved!")
    
    with col_reset:
        if st.button("🔄 Reset App"):
            # Clear everything but the API key if already set in .env
            for key in list(st.session_state.keys()):
                if key != "google_api_key" or not os.getenv("GOOGLE_API_KEY"):
                    del st.session_state[key]
            st.rerun()

    # Model Selection
    if st.session_state.get("google_api_key"):
        if "available_models" not in st.session_state:
            try:
                genai.configure(api_key=st.session_state.google_api_key)
                models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        models.append(m.name.replace('models/', ''))
                st.session_state.available_models = sorted(models)
            except Exception as e:
                st.error(f"Error fetching models: {e}")
                st.session_state.available_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash"]
        
        # Try to default to Gemini 2.0 Flash
        default_model = "gemini-2.0-flash-exp"
        if default_model not in st.session_state.available_models:
            default_model = "gemini-1.5-flash" if "gemini-1.5-flash" in st.session_state.available_models else st.session_state.available_models[0]

        selected_model = st.selectbox(
            "Select Gemini Model", 
            options=st.session_state.available_models,
            index=st.session_state.available_models.index(default_model) if default_model in st.session_state.available_models else 0
        )
        st.session_state.selected_model = selected_model
    else:
        st.session_state.selected_model = "gemini-2.0-flash-exp"

    st.divider()
    st.title("🤖 Custom Agents")
    
    # Dynamic Agent Management
    # Use a copy of the list to avoid mutation issues during iteration
    updated_agents = []
    for i, agent in enumerate(st.session_state.custom_agents):
        # Unique keys based on persona set to avoid widget stale values
        set_prefix = st.session_state.get("current_persona_set", "General").replace(" ", "_")
        with st.expander(f"Agent {i+1}: {agent['name']}", expanded=False):
            name = st.text_input(f"Name", value=agent['name'], key=f"{set_prefix}_name_{i}")
            prompt = st.text_area(f"System Prompt", value=agent['prompt'], key=f"{set_prefix}_prompt_{i}")
            if st.button(f"Remove Agent {i+1}", key=f"{set_prefix}_remove_{i}"):
                st.session_state.custom_agents.pop(i)
                st.rerun()
            updated_agents.append({"name": name, "prompt": prompt})
    
    # Only update the list of agents, don't trigger state mismatch if we just loaded from YAML
    st.session_state.custom_agents = updated_agents

    if st.button("➕ Add Specialist Agent"):
        st.session_state.custom_agents.append({"name": "New Specialist", "prompt": "You are a specialist. Analyze the CV from your perspective."})
        st.rerun()

    st.divider()
    st.title("📚 Reference Library")
    st.write("Upload successful CV examples to guide the RAG agent.")
    reference_files = st.file_uploader("Upload Successful CVs", accept_multiple_files=True, type=['pdf', 'txt'], key="refs")
    
    if st.button("Process References") and reference_files:
        if not st.session_state.get("google_api_key"):
            st.error("Please provide a Google API Key first.")
        else:
            with st.spinner("Indexing reference CVs..."):
                docs = []
                for uploaded_file in reference_files:
                    temp_path = f"./temp_ref_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    if uploaded_file.name.endswith(".pdf"):
                        loader = PyPDFLoader(temp_path)
                        docs.extend(loader.load())
                    elif uploaded_file.name.endswith(".txt"):
                        with open(temp_path, "r") as f:
                            from langchain.schema import Document
                            docs.append(Document(page_content=f.read(), metadata={"source": uploaded_file.name}))
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                splits = text_splitter.split_documents(docs)
                
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=st.session_state.google_api_key)
                vectorstore = Chroma.from_documents(
                    documents=splits, 
                    embedding=embeddings, 
                    persist_directory="./chroma_db",
                    collection_name="reference_cvs"
                )
                st.session_state.vectorstore = vectorstore
                st.success(f"Indexed {len(reference_files)} reference documents.")

# --- Agents Definition ---
def get_llm(api_key, model):
    return ChatGoogleGenerativeAI(
        model=model, 
        google_api_key=api_key,
        temperature=0.2
    )

def rag_specialist_agent(state: AgentState, config):
    """Analyzes the CV against successful examples in the RAG database."""
    cv_content = state["cv_content"]
    api_key = config["configurable"]["api_key"]
    model = config["configurable"]["model"]

    if "vectorstore" not in st.session_state:
        return {"rag_reference_results": "No reference CVs provided for comparison."}
    
    vectorstore = st.session_state.vectorstore
    docs = vectorstore.similarity_search(cv_content, k=3)
    context = "\n\n".join([d.page_content for d in docs])
    
    llm = get_llm(api_key, model)
    prompt = f"""You are a CV Specialist. Compare the candidate's CV content with these successful CV examples.
    Identify what patterns, keywords, or structures the candidate is missing or could adopt from the successful examples.

    Candidate's CV:
    {cv_content}

    Successful CV Examples (Context):
    {context}
    
    Analysis:"""
    response = llm.invoke(prompt)
    return {"rag_reference_results": response.content}

def web_search_agent(state: AgentState, config):
    """Searches for modern best practices and market trends for the candidate's role."""
    cv_content = state["cv_content"]
    api_key = config["configurable"]["api_key"]
    model = config["configurable"]["model"]
    
    llm = get_llm(api_key, model)
    role_extraction = llm.invoke(f"Extract the primary job role or target industry from this CV content: {cv_content[:1000]}")
    role = role_extraction.content
    
    search = DuckDuckGoSearchRun()
    search_query = f"best practices for {role} CV resume 2024 2025"
    search_results = search.run(search_query)
    
    prompt = f"""You are a Market Trends Expert. Based on these search results about CV best practices for {role}, 
    evaluate the candidate's CV. Highlight modern standards they should follow.

    Candidate's CV:
    {cv_content}

    Web Search Results:
    {search_results}
    
    Analysis:"""
    response = llm.invoke(prompt)
    return {"web_best_practices": response.content}

def custom_specialist_agent(state: AgentState, config):
    """A generic specialist agent that uses its persona-specific prompt."""
    # Find which specialist this is based on the node name
    # We can't easily get the node name inside the function in LangGraph without complex setup,
    # so we'll look for a unique marker in the config or just use the agent_id if we can pass it.
    # Actually, LangGraph allows passing metadata or specific config per node.
    
    # For this implementation, we'll assume the config has the specific agent's data
    agent_name = config["configurable"].get("agent_name", "Unknown Specialist")
    agent_prompt = config["configurable"].get("agent_prompt", "")
    
    cv_content = state["cv_content"]
    rag_info = state["rag_reference_results"]
    web_info = state["web_best_practices"]
    api_key = config["configurable"]["api_key"]
    model = config["configurable"]["model"]
    
    llm = get_llm(api_key, model)
    full_prompt = f"""{agent_prompt}
    
    Candidate's CV: {cv_content[:2000]}
    RAG Reference Analysis: {rag_info}
    Web Trend Analysis: {web_info}
    
    Provide your specific analysis based on your persona."""
    response = llm.invoke(full_prompt)
    return {"agent_reports": {agent_name: response.content}}

def council_recommender_agent(state: AgentState, config):
    """Synthesizes all results into a final recommendation."""
    cv_content = state["cv_content"]
    rag_info = state["rag_reference_results"]
    web_info = state["web_best_practices"]
    agent_reports = state["agent_reports"]
    
    api_key = config["configurable"]["api_key"]
    model = config["configurable"]["model"]
    
    specialist_summaries = ""
    for name, report in agent_reports.items():
        specialist_summaries += f"- {name}: {report}\n"
    
    llm = get_llm(api_key, model)
    prompt = f"""You are the Council Head for CV Excellence. Synthesize the findings from all your specialists into a final, actionable recommendation for the candidate.
    
    You MUST provide a clear summary of each specialist's contribution in your final output.
    
    Specialist Reports:
    - RAG Reference Expert: {rag_info}
    - Market Trends Expert: {web_info}
    {specialist_summaries}
    
    Your Final Recommendation should include:
    1. Executive Summary
    2. Specialist Summaries (briefly summarize what EVERY specialist found)
    3. Key Strengths
    4. Critical Missing Elements
    5. Modern Formatting/Content Improvements
    6. A 'Verdict' on readiness.
    
    Final Recommendation:"""
    response = llm.invoke(prompt)
    return {"final_critique": response.content}

# --- LangGraph Workflow ---
def create_graph(custom_agents):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("reference_specialist", rag_specialist_agent)
    workflow.add_node("trends_specialist", web_search_agent)
    
    # Add dynamic nodes for custom agents
    agent_node_names = []
    for i, agent in enumerate(custom_agents):
        node_name = f"specialist_{i}"
        
        # We use a helper function to create a specialized version of the node
        # that knows its own index to fetch its configuration.
        def make_agent_node(agent_idx):
            def agent_node(state, config):
                # Fetch specific agent data from the global list in config
                agent_data = config["configurable"]["custom_agents"][agent_idx]
                specific_config = config.copy()
                specific_config["configurable"] = config["configurable"].copy()
                specific_config["configurable"]["agent_name"] = agent_data["name"]
                specific_config["configurable"]["agent_prompt"] = agent_data["prompt"]
                return custom_specialist_agent(state, specific_config)
            return agent_node

        workflow.add_node(node_name, make_agent_node(i))
        agent_node_names.append(node_name)
    
    workflow.add_node("council_head", council_recommender_agent)
    
    workflow.set_entry_point("reference_specialist")
    workflow.add_edge("reference_specialist", "trends_specialist")
    
    # All specialists run in parallel after web_specialist
    for node_name in agent_node_names:
        workflow.add_edge("trends_specialist", node_name)
        workflow.add_edge(node_name, "council_head")
    
    # If no custom agents, go straight to council_head
    if not agent_node_names:
        workflow.add_edge("trends_specialist", "council_head")
        
    workflow.add_edge("council_head", END)
    
    return workflow.compile()

# --- UI Layout ---
st.title("📄 CV Excellence Council")
st.markdown("Collaborative AI deliberation to perfect your CV.")

if not st.session_state.get("google_api_key"):
    st.info("👈 Please enter your Google API Key in the sidebar to start.")
else:
    cv_file = st.file_uploader("Upload your CV for Analysis", type=['pdf', 'txt'], key="user_cv")

    if cv_file:
        if st.button("Analyze CV"):
            with st.spinner("The Council is reviewing your CV..."):
                # Read CV Content
                cv_content = ""
                temp_path = f"./temp_user_{cv_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(cv_file.getbuffer())
                
                if cv_file.name.endswith(".pdf"):
                    loader = PyPDFLoader(temp_path)
                    cv_content = "\n".join([d.page_content for d in loader.load()])
                else:
                    cv_content = cv_file.read().decode("utf-8")
                
                os.remove(temp_path)

                # Run Agentic Workflow
                # We pass the list of agents to create_graph
                app = create_graph(st.session_state.custom_agents)
                
                initial_state = {
                    "cv_content": cv_content,
                    "rag_reference_results": "",
                    "web_best_practices": "",
                    "agent_reports": {},
                    "final_critique": ""
                }
                
                # We need to use a per-node configuration for the dynamic specialists
                # LangGraph 0.2+ handles this via config in the node calls
                # However, for simplicity in a single app.invoke, we'll use a wrapper or 
                # just rely on the fact that we can pass specific configs per node if we were using a more complex setup.
                # Here, we'll modify the custom_specialist_agent to look for its own data based on the node name.
                
                def get_config(node_name):
                    # Helper to get specific config for a specialist node
                    if node_name.startswith("specialist_"):
                        idx = int(node_name.split("_")[1])
                        agent = st.session_state.custom_agents[idx]
                        return {
                            "agent_id": idx,
                            "agent_name": agent["name"],
                            "agent_prompt": agent["prompt"],
                            "api_key": st.session_state.google_api_key,
                            "model": st.session_state.selected_model
                        }
                    return {
                        "api_key": st.session_state.google_api_key,
                        "model": st.session_state.selected_model,
                        # For the council_head to know about all agents
                        "agent_reports": st.session_state.custom_agents 
                    }

                # Refined approach: Use the 'config' parameter of invoke and node-specific logic
                # LangGraph allows passing a config to the whole invoke.
                # To handle node-specific data, we'll pass the whole agent list in the config.
                
                main_config = {
                    "configurable": {
                        "api_key": st.session_state.google_api_key,
                        "model": st.session_state.selected_model,
                        "custom_agents": st.session_state.custom_agents
                    }
                }
                
                # Update the specialist agent to find its own data from the shared list
                # (I'll need to tweak the custom_specialist_agent slightly)
                
                final_state = app.invoke(initial_state, config=main_config)
                
                # Display Results
                st.divider()
                st.header("📋 Council's Final Recommendation")
                st.markdown(final_state["final_critique"])
                
                with st.expander("🔍 View Detailed Agent Reports"):
                    report_keys = list(final_state["agent_reports"].keys())
                    tab_labels = ["Reference Expert", "Trends Expert"] + report_keys
                    
                    tabs = st.tabs(tab_labels)
                    with tabs[0]:
                        st.write(final_state["rag_reference_results"])
                    with tabs[1]:
                        st.write(final_state["web_best_practices"])
                    for i, name in enumerate(report_keys):
                        with tabs[i+2]:
                            st.write(final_state["agent_reports"][name])
