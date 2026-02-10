"""Main entry point for the AI CV Advisor Board application."""

import streamlit as st
from dotenv import load_dotenv

from session_utils import init_session_state
from steps.config import render_config_step
from steps.job import render_job_step
from steps.personalize import render_personalize_step
from steps.results import render_results_step
from steps.team import render_team_step
from steps.upload import render_upload_step
from steps.welcome import render_welcome_step
from ui_components import render_header, render_stepper

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="AI - CV Advisor Board",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Initialize State ---
init_session_state()

# --- Main UI ---
render_header()
if 0 < st.session_state.step <= 5:
    render_stepper(st.session_state.step)

# --- Routing ---
if st.session_state.step == 0:
    render_welcome_step()
elif st.session_state.step == 1:
    render_config_step()
elif st.session_state.step == 2:
    render_upload_step()
elif st.session_state.step == 3:
    render_job_step()
elif st.session_state.step == 4:
    render_team_step()
elif st.session_state.step == 5:
    render_results_step()
elif st.session_state.step == 6:
    render_personalize_step()
