"""Main entry point for the AI CV Advisory Board application."""

import streamlit as st
from dotenv import load_dotenv

from state_manager import state_manager
from steps.config import render_config_step
from steps.job import render_job_step
from steps.personalize import render_personalize_step
from steps.results import render_results_step
from steps.team import render_team_step
from steps.upload import render_upload_step
from steps.welcome import render_welcome_step
from ui_components import render_footer, render_header, render_stepper

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="AI - CV Advisory Board",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Main UI ---
render_header()
if 0 < state_manager.step <= 5:
    render_stepper(state_manager.step)

# --- Routing ---
if state_manager.step == 0:
    render_welcome_step()
elif state_manager.step == 1:
    render_config_step()
elif state_manager.step == 2:
    render_upload_step()
elif state_manager.step == 3:
    render_job_step()
elif state_manager.step == 4:
    render_team_step()
elif state_manager.step == 5:
    render_results_step()
elif state_manager.step == 6:
    render_personalize_step()

render_footer()
