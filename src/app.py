import streamlit as st
import os
import yaml
import chromadb
from pypdf import PdfReader
from llm_utils import get_available_models
from scraper import scrape_linkedin_job
from crew_logic import create_crew
import time

# --- Initial Setup ---
st.set_page_config(
    page_title="CV Excellence Council",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "Google"
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")
if "selected_model" not in st.session_state:
    st.session_state.selected_model = ""
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = []
if "selected_persona_names" not in st.session_state:
    st.session_state.selected_persona_names = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "cv_content" not in st.session_state:
    st.session_state.cv_content = ""
if "cv_filename" not in st.session_state:
    st.session_state.cv_filename = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "job_url" not in st.session_state:
    st.session_state.job_url = ""
if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "crew_result" not in st.session_state:
    st.session_state.crew_result = None

# --- Helpers ---
def load_personas():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persona_dir = os.path.join(base_dir, "personas")
    all_personas = {}
    if os.path.exists(persona_dir):
        for filename in os.listdir(persona_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                try:
                    with open(os.path.join(persona_dir, filename), 'r', encoding='utf-8') as f:
                        personas = yaml.safe_load(f)
                        if personas:
                            for p in personas:
                                display_name = f"{p['name']} ({filename.split('.')[0]})"
                                all_personas[display_name] = p
                except Exception as e:
                    st.error(f"Error loading {filename}: {e}")
    return all_personas

def reset_app():
    st.session_state.step = 1
    st.session_state.cv_content = ""
    st.session_state.cv_filename = ""
    st.session_state.job_description = ""
    st.session_state.job_url = ""
    st.session_state.job_text = ""
    st.session_state.crew_result = None
    st.rerun()

def next_step():
    st.session_state.step += 1
    st.rerun()

def prev_step():
    st.session_state.step -= 1
    st.rerun()

# --- Visual Stepper ---
steps = [
    {"label": "Setup"},
    {"label": "Upload"},
    {"label": "Job"},
    {"label": "Team"},
    {"label": "Results"}
]

def render_stepper():
    st.write("") # Spacer
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        step_num = i + 1
        with col:
            if st.session_state.step == step_num:
                st.markdown(f"#### 🔷 {step['label']}")
                st.progress(100)
            elif st.session_state.step > step_num:
                st.markdown(f"**✅ {step['label']}**")
                st.progress(100)
            else:
                st.markdown(f"⚪ {step['label']}")
                st.progress(0)
    st.write("---")

# --- Main App ---

st.title("CV Excellence Council")
render_stepper()

# --- Step 1: Configuration ---
if st.session_state.step == 1:
    st.header("Step 1: System Configuration")
    st.info("Let's get your AI environment set up first.")

    with st.container(border=True):
        st.subheader("🔑 Provider Selection")
        
        st.session_state.llm_provider = st.radio(
            "Select AI Provider",
            options=["Google", "OpenAI"],
            horizontal=True
        )
        
        api_key_input = st.text_input(
            f"Enter your {st.session_state.llm_provider} API Key", 
            type="password", 
            value=st.session_state.api_key,
            help=f"Required to access {st.session_state.llm_provider} models."
        )
        
        if api_key_input:
            st.session_state.api_key = api_key_input
            
            # Fetch Models
            cache_key = f"{st.session_state.llm_provider}_{api_key_input}"
            if "available_models" not in st.session_state or st.session_state.get("last_api_cache_key") != cache_key:
                try:
                    with st.spinner(f"Validating {st.session_state.llm_provider} API Key & Fetching Models..."):
                        st.session_state.available_models = get_available_models(api_key_input, st.session_state.llm_provider)
                        st.session_state.last_api_cache_key = cache_key
                except Exception as e:
                    st.error(f"Invalid API Key or Error: {e}")
                    st.session_state.available_models = []
            
            available_models = st.session_state.available_models
            
            if available_models:
                st.success(f"{st.session_state.llm_provider} API Key Validated!")
                
                # Internal mappings for Streamlit Community defaults
                internal_google = "gemini-2.0-flash-lite-preview-02-05"
                internal_openai = "gpt-4o-mini"
                
                # UI Display Names
                default_display_google = "Gemini 2.5 Flash-Lite"
                default_display_openai = "GPT-4.1-nano"
                
                is_local = os.getenv("RUN_MODE", "local") == "local"
                
                if is_local:
                    st.session_state.selected_model = st.selectbox(
                        f"Select {st.session_state.llm_provider} Model", 
                        options=available_models,
                        index=0
                    )
                else:
                    if st.session_state.llm_provider == "Google":
                        st.session_state.selected_model = internal_google
                        st.info(f"Using default model: **{default_display_google}**")
                    else:
                        st.session_state.selected_model = internal_openai
                        st.info(f"Using default model: **{default_display_openai}**")
            else:
                st.warning("No models found. Please check your API key.")

    col1, col2 = st.columns([1, 4])
    with col2:
        disabled = not (st.session_state.api_key and st.session_state.selected_model)
        if st.button("Next: Upload CV ➡️", type="primary", disabled=disabled, use_container_width=True):
            next_step()

# --- Step 2: CV Upload ---
elif st.session_state.step == 2:
    st.header("Step 2: Upload Your CV")
    st.markdown("Upload the Resume/CV you want to analyze.")

    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload PDF or TXT", type=['pdf', 'txt'])
        
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

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        if st.button("Next: Job Target ➡️", type="primary", disabled=not st.session_state.cv_content, use_container_width=True):
            next_step()

# --- Step 3: Job Context ---
elif st.session_state.step == 3:
    st.header("Step 3: Target Opportunity")
    st.markdown("What job are you applying for? This context is crucial for the council.")

    tab1, tab2 = st.tabs(["🔗 LinkedIn URL", "📝 Manual Description"])
    
    with tab1:
        st.session_state.job_url = st.text_input(
            "Paste LinkedIn Job URL", 
            value=st.session_state.job_url, 
            placeholder="https://www.linkedin.com/jobs/view/..."
        )
        if st.session_state.job_url:
            st.info("We will scrape the job details automatically.")

    with tab2:
        st.session_state.job_text = st.text_area(
            "Paste Job Description Text", 
            value=st.session_state.job_text, 
            height=200,
            placeholder="Key Responsibilities, Requirements, etc."
        )

    has_job_context = bool(st.session_state.job_url or st.session_state.job_text)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        btn_label = "Next: Assemble Council ➡️"
        if not has_job_context:
            btn_label = "Skip to Council (General Review) ➡️"
            
        if st.button(btn_label, type="primary", use_container_width=True):
             next_step()

# --- Step 4: Assemble Council ---
elif st.session_state.step == 4:
    st.header("Step 4: Assemble Your Personal Council")
    st.markdown("Select the AI experts who will critique your CV.")

    all_available_personas = load_personas()
    matchmaker_key = next((k for k in all_available_personas.keys() if "LinkedIn Matchmaker" in k), None)
    
    has_job_context = bool(st.session_state.job_url or st.session_state.job_text)
    
    if not st.session_state.selected_persona_names:
        if matchmaker_key and has_job_context:
             st.session_state.selected_persona_names = [matchmaker_key]

    display_options = []
    option_mapping = {}
    for k in all_available_personas.keys():
        label = k
        if k == matchmaker_key:
            label = f"⭐ {k} (Recommended)"
        display_options.append(label)
        option_mapping[label] = k

    selected_labels = st.multiselect(
        "Select Council Members",
        options=display_options,
        default=[l for l, k in option_mapping.items() if k in st.session_state.selected_persona_names]
    )
    
    selected_keys = [option_mapping[l] for l in selected_labels]
    st.session_state.selected_persona_names = selected_keys
    
    current_manual_agents = [a for a in st.session_state.custom_agents 
                             if not any(a['name'] == p['name'] for p in all_available_personas.values())]
    new_persona_agents = [all_available_personas[name].copy() for name in selected_keys]
    st.session_state.custom_agents = new_persona_agents + current_manual_agents

    with st.expander("🛠️ Add Custom Specialist (Advanced)", expanded=False):
        st.write("Create your own agent with a specific perspective.")
        new_name = st.text_input("Specialist Role", placeholder="e.g., Toxic Culture Detector")
        new_prompt = st.text_area("Analysis Instructions", placeholder="Analyze the CV for...")
        if st.button("Add Specialist"):
            if new_name and new_prompt:
                st.session_state.custom_agents.append({"name": new_name, "prompt": new_prompt})
                st.rerun()

    st.subheader("Current Team")
    if not st.session_state.custom_agents:
        st.warning("No agents selected.")
    else:
        for agent in st.session_state.custom_agents:
            st.success(f"👤 **{agent['name']}**")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            prev_step()
    with col2:
        if st.button("🚀 Start Analysis ➡️", type="primary", disabled=not st.session_state.custom_agents, use_container_width=True):
            next_step()

# --- Step 5: Results ---
elif st.session_state.step == 5:
    if st.session_state.crew_result is None:
        st.header("⏳ Council is Deliberating...")
        
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
        
        st.session_state.job_description = final_job_desc

        try:
            with st.spinner("Analyzing CV against Job Description..."):
                app = create_crew(
                    st.session_state.custom_agents, 
                    st.session_state.cv_content, 
                    st.session_state.job_description, 
                    st.session_state.api_key, 
                    st.session_state.selected_model,
                    st.session_state.llm_provider
                )
                st.session_state.crew_result = app.kickoff()
                st.rerun()
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            if st.button("Try Again"):
                st.rerun()
            st.stop()
    else:
        st.header("📋 Council Recommendation")
        st.balloons()
        
        tab1, tab2 = st.tabs(["📝 Final Report", "🔍 Detailed Analysis"])
        
        with tab1:
            with st.container(border=True):
                 report_content = str(st.session_state.crew_result.raw)
                 if report_content.startswith("```markdown"):
                     report_content = report_content.replace("```markdown", "", 1).rsplit("```", 1)[0]
                 elif report_content.startswith("```"):
                     report_content = report_content.replace("```", "", 1).rsplit("```", 1)[0]
                 
                 st.markdown(report_content)
            
        with tab2:
            for task_output in st.session_state.crew_result.tasks_output:
                with st.expander(f"Report: {task_output.description[:50]}..."):
                    st.write(task_output.raw)
        
        # --- Support Section ---
        st.divider()
        col_left, col_mid, col_right = st.columns([1, 2, 1])
        with col_mid:
            st.markdown(
                """
                <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
                    <p style="margin-bottom: 10px; font-weight: bold;">Enjoying the CV Excellence Council?</p>
                    <a href="https://www.buymeacoffee.com/carlosan1708" target="_blank">
                        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 180px !important;" >
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.divider()

        col1, col2 = st.columns([1, 1])
        with col1:
             if st.button("🔄 New Analysis", use_container_width=True):
                reset_app()
        with col2:
             st.download_button(
                 label="📥 Download Report",
                 data=str(st.session_state.crew_result.raw),
                 file_name="cv_analysis_report.md",
                 mime="text/markdown",
                 use_container_width=True
             )
