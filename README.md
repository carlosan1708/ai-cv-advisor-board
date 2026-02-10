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

## 🏗️ Project Structure

```text
.
├── personas/           # YAML files defining specialist personas
├── src/                # Application source code
│   ├── app.py          # Main Streamlit application
│   ├── crew_logic.py   # CrewAI orchestration logic
│   └── steps/          # UI steps for the wizard
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── README.md           # Project documentation
```

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

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Agent Orchestration**: [CrewAI](https://www.crewai.com/)
- **LLM Framework**: [LangChain](https://www.langchain.com/) / [LiteLLM](https://www.litellm.ai/)
- **LLM**: [Google Gemini](https://ai.google.dev/) (Default) or OpenAI
- **Search**: DuckDuckGo Search

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International (CC BY-NC-ND 4.0)** License. See the [LICENSE](LICENSE) file for details.
