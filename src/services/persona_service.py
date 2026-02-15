from pathlib import Path
from typing import Dict

import yaml

from logger import logger
from models import Persona


class PersonaService:
    @staticmethod
    def load_personas() -> Dict[str, Persona]:
        """Loads all agent personas from the personas directory and returns them as Persona objects."""
        # Calculate path relative to this file's location
        # src/services/persona_service.py -> ../../personas
        base_dir = Path(__file__).parent.parent.parent
        persona_dir = base_dir / "personas"

        all_personas: Dict[str, Persona] = {}

        if not persona_dir.exists():
            logger.error(f"Persona directory not found at {persona_dir}")
            return {}

        logger.info(f"Loading personas from {persona_dir}")

        for file_path in persona_dir.glob("*.yaml"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if not data:
                        continue

                    for p_data in data:
                        persona = Persona(
                            name=p_data["name"],
                            role=p_data["role"],
                            goal=p_data["goal"],
                            backstory=p_data["backstory"],
                            tools=p_data.get("tools", []),
                        )
                        # Create a unique display name including the source file
                        display_name = f"{persona.name} ({file_path.stem})"
                        all_personas[display_name] = persona

            except Exception as e:
                logger.error(f"Error loading personas from {file_path.name}: {str(e)}")
                # We don't raise here to allow other files to load, but we log the error

        logger.info(f"Successfully loaded {len(all_personas)} personas.")
        return all_personas
