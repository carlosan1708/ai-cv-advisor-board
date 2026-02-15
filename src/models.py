from dataclasses import dataclass, field
from typing import List


@dataclass
class JobInfo:
    url: str = ""
    text: str = ""
    description: str = ""


@dataclass
class Persona:
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = field(default_factory=list)


@dataclass
class AppConfig:
    llm_provider: str = "Google"
    selected_model: str = ""
    api_key: str = ""
    is_online: bool = False
