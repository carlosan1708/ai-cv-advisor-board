# AI - CV Advisor Board 📄🤖

An AI-powered multi-agent system designed to analyze and optimize CVs. It uses **CrewAI**, **Streamlit**, and **Google Gemini** (or OpenAI) to compare your CV against job descriptions and provide expert feedback from a "Board" of specialized agents.

> [!IMPORTANT]
> **Status: Work in Progress (MVP Phase)**
> This repository is currently under active development and should be considered a Minimum Viable Product (MVP).

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

## 🚀 Overview

Collaborative AI deliberation to perfect your CV. Specialized AI agents (the "Board") review your CV from multiple perspectives, providing actionable feedback and a professionally rewritten version.

![Demo](Demo.gif)

## 🏗️ Project Architecture

The application follows a scalable, service-oriented architecture designed for maintainability and growth:

```text
.
├── personas/           # YAML files defining specialist personas
├── src/                # Application source code
│   ├── app.py          # Main Streamlit entry point
│   ├── models.py       # Domain data models (Job, Persona, Config)
│   ├── state_manager.py# Centralized session state orchestration
│   ├── logger.py       # Structured application logging
│   ├── exceptions.py   # Custom domain exceptions
│   ├── services/       # Stateless business logic layer
│   │   ├── analysis_service.py # CrewAI orchestration
│   │   ├── cv_service.py       # PDF/Text processing
│   │   ├── job_service.py      # Job scraping & extraction
│   │   ├── persona_service.py  # Persona management
│   │   └── config_service.py   # LLM & System configuration
│   └── steps/          # Modular UI components for the wizard
├── scripts/            # Development and CI/CD utilities
├── tests/              # Automated test suite
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── README.md           # Project documentation
```

### Core Design Principles
- **Separation of Concerns**: UI code is decoupled from business logic.
- **Stateless Services**: Logic is encapsulated in reusable services.
- **Centralized State**: Application state is managed through a single `StateManager`.
- **Observability**: Built-in structured logging and custom error handling.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- A Google AI API Key (Gemini) or OpenAI API Key

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/carlosan1708/ai-cv-advisor-board
cd ai-cv-advisor-board
```

### 2. Set Up the Python Environment

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Install Dependencies:
```bash
pip install -r requirements.txt
```

#### Development Setup (Optional):
If you plan to contribute, install development tools and pre-commit hooks:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

To run pre-commit checks manually on all files:

```bash
pre-commit run --all-files
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your `GOOGLE_API_KEY` (or other keys as needed).

### 4. Run the Application

```bash
streamlit run src/app.py
```

The application will be available at `http://localhost:8501`.

## ✨ Features

- **Step-by-Step Wizard**: A guided process (Welcome, Config, Upload, Job, Team, Results).
- **Multi-Agent Collaboration**: Powered by **CrewAI** for sophisticated AI deliberation.
- **Job Targeting**: Analyze your CV against a specific LinkedIn job URL or manual description.
- **Custom Specialist Board**: Choose from pre-defined personas or create your own specialists.
- **Rich Markdown Reports**: Get beautifully formatted, actionable feedback.
- **Professional Rewrite**: Get an optimized version of your CV in Markdown or PDF.
- **Interactive UI**: Modern interface built with Streamlit.
- **Robust Observability**: Structured logging to `logs/app.log`.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Agent Orchestration**: [CrewAI](https://www.crewai.com/)
- **LLM Framework**: [LangChain](https://www.langchain.com/) / [LiteLLM](https://www.litellm.ai/)
- **LLM**: [Google Gemini](https://ai.google.dev/) (Default) or OpenAI
- **PDF Processing**: [PyPDF](https://pypi.org/project/pypdf/) & [FPDF2](https://py-pdf.github.io/fpdf2/)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International (CC BY-NC-ND 4.0)** License. See the [LICENSE](LICENSE) file for details.
