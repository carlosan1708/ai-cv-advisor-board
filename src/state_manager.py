from typing import Any, List, Optional

import streamlit as st

from models import AppConfig, JobInfo
from services.config_service import ConfigService


class StateManager:
    """Manages the application state, abstracting Streamlit's session_state."""

    def __init__(self):
        self._ensure_initialized()

    def _ensure_initialized(self):
        is_online = ConfigService.get_is_online()
        config = AppConfig(
            is_online=is_online,
            llm_provider="Google",
            api_key=ConfigService.get_env_api_key("Google") if is_online else "",
            selected_model=ConfigService.get_cheap_model("Google") if is_online else "",
        )

        defaults = {
            "step": 0,
            "config": config,
            "job": JobInfo(),
            "cv_content": "",
            "cv_filename": "",
            "selected_persona_names": [],
            "custom_agents": [],
            "crew_result": None,
            "interview_questions": [],
            "user_answers": {},
            "interview_done": False,
            "board_agents": [],
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @property
    def step(self) -> int:
        return st.session_state.step

    @step.setter
    def step(self, value: int):
        st.session_state.step = value

    @property
    def config(self) -> AppConfig:
        return st.session_state.config

    @property
    def job(self) -> JobInfo:
        return st.session_state.job

    def next_step(self):
        st.session_state.step += 1
        st.rerun()

    def prev_step(self):
        st.session_state.step -= 1
        st.rerun()

    def reset(self):
        st.session_state.step = 1
        st.session_state.cv_content = ""
        st.session_state.cv_filename = ""
        st.session_state.job = JobInfo()
        st.session_state.crew_result = None
        st.session_state.interview_questions = []
        st.session_state.user_answers = {}
        st.session_state.interview_done = False
        st.session_state.board_agents = []
        st.rerun()

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def update_job(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.job, key):
                setattr(self.job, key, value)


# Singleton instance for easy access
state_manager = StateManager()
