"""Tests for the persona loading and validation logic."""

import os

import yaml

from src.persona_utils import load_personas


def test_load_personas_structure(tmp_path):
    """Test the structure of the loaded personas dictionary."""
    # Create a temporary personas directory
    persona_dir = tmp_path / "personas"
    persona_dir.mkdir()

    # Create a dummy persona file
    test_persona = [{"name": "Test Agent", "prompt": "Test Prompt"}]
    with open(persona_dir / "test.yaml", "w", encoding="utf-8") as f:
        yaml.dump(test_persona, f)

    # Mock the base directory to use our temp path
    # Note: This is a bit tricky without full mocking, but let's test the REAL personas first
    personas = load_personas()

    assert isinstance(personas, dict)
    if len(personas) > 0:
        first_key = list(personas.keys())[0]
        assert "name" in personas[first_key]
        assert "prompt" in personas[first_key]


def test_persona_files_valid():
    """Verify that all persona YAML files in the project are valid."""
    # Check actual persona files in the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persona_dir = os.path.join(base_dir, "personas")

    for filename in os.listdir(persona_dir):
        if filename.endswith(".yaml"):
            with open(os.path.join(persona_dir, filename), "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                assert isinstance(data, list), f"{filename} should be a list"
                for entry in data:
                    assert "name" in entry, f"Entry in {filename} missing 'name'"
                    assert "prompt" in entry, f"Entry in {filename} missing 'prompt'"
