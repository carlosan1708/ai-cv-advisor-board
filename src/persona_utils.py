"""Utility functions for loading and managing agent personas from YAML files."""

import os

import streamlit as st
import yaml


def load_personas():
    """Load all agent personas from the personas directory.

    Returns:
        A dictionary mapping persona display names to their details.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persona_dir = os.path.join(base_dir, "personas")
    all_personas = {}
    if os.path.exists(persona_dir):
        for filename in os.listdir(persona_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                try:
                    with open(os.path.join(persona_dir, filename), "r", encoding="utf-8") as f:
                        personas = yaml.safe_load(f)
                        if personas:
                            for p in personas:
                                display_name = f"{p['name']} ({filename.split('.')[0]})"
                                all_personas[display_name] = p
                except Exception as e:
                    st.error(f"Error loading {filename}: {e}")
    return all_personas
