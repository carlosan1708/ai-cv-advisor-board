# CV Excellence Council 📄🤖

![Demo](demo.gif)

> [!IMPORTANT]
> **Status: Work in Progress (MVP Phase)**
> This repository is currently under active development and should be considered a Minimum Viable Product (MVP). Some features may be experimental, and breaking changes might occur as the project evolves.

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

An AI-powered multi-agent system designed to analyze and optimize CVs. It uses **LangGraph**, **Streamlit**, and **Google Gemini** to compare your CV against successful industry examples and modern market trends.

## 🚀 Overview

Collaborative AI deliberation to perfect your CV. This project provides a collaborative environment where specialized AI agents (the "Council") review your CV from multiple perspectives, including RAG-based comparison with successful examples and real-time web search for market trends.

## 🏗️ Project Structure

```text
.
├── chroma_db/          # Vector database files (ignored by git)
├── personas/           # YAML files defining specialist personas (General, IT Specialist)
├── scripts/            # Utility scripts (e.g., database setup)
├── src/                # Application source code
│   └── app.py          # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── .gitignore          # Git ignore rules
```

## Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- A Google AI API Key (Gemini)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/carlosan1708/agentic-rag-cv-council
cd agentic-rag-cv-council
```

### 2. Set Up the Python Environment

It is recommended to use a virtual environment to manage dependencies:

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

Create a `.env` file in the root directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and add your `GOOGLE_API_KEY`.

### 4. Run the Application

Once your environment is set up, start the Streamlit interface:

```bash
streamlit run src/app.py
```

The application will be available at `http://localhost:8501`.

## ✨ Features

- **Step-by-Step Wizard**: A guided 5-step process (Setup, Upload, Job Context, Team Assembly, Results) for a seamless user experience.
- **Dynamic Configuration**: Integrated setup for Google API Key and model selection directly within the onboarding flow.
- **Multi-Agent Collaboration**: Powered by **CrewAI** (formerly orchestrated by LangGraph) for sophisticated AI deliberation.
- **Optional Job Targeting**: Analyze your CV against a specific LinkedIn job URL or a manual description, or skip for a general professional review.
- **Reference RAG Agent**: (Optional) Upload successful CV examples to guide the AI in identifying winning patterns.
- **Custom Specialist Council**: Choose from pre-defined personas (Technical Recruiter, Soft Skills Coach, etc.) or create your own custom specialists.
- **Rich Markdown Reports**: Get beautifully formatted, actionable feedback including Executive Summaries, Key Strengths, and Next Steps.
- **Interactive UI**: Modern, centered interface built with Streamlit with clear progress tracking and navigation.

## 💡 Troubleshooting

- **pypdf error**: If you encounter issues reading PDF files, ensure `pypdf` is correctly installed: `pip install pypdf`.
- **API Key**: A valid Google Gemini API key is required. You can get one at [Google AI Studio](https://aistudio.google.com/).
- **Vector Store**: If you want to clear the reference library, you can delete the `chroma_db/` directory.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Agent Orchestration**: [LangGraph](https://www.langchain.com/langgraph)
- **LLM Framework**: [LangChain](https://www.langchain.com/)
- **LLM**: [Google Gemini](https://ai.google.dev/)
- **Vector Store**: [ChromaDB](https://www.trychroma.com/)
- **Search**: DuckDuckGo Search

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🛠️ Development

To maintain code quality, this project uses `black`, `isort`, and `flake8`. Configuration for these tools is located in `pyproject.toml`.

### Install Development Dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run Formatters and Linters:

- **Format code**:
  ```bash
  black .
  ```
- **Sort imports**:
  ```bash
  isort .
  ```
- **Lint code**:
  ```bash
  flake8 .
  ```

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International (CC BY-NC-ND 4.0)** License.

This means you are free to:
- **Share**: Copy and redistribute the material in any medium or format.

Under the following terms:
- **Attribution**: You must give appropriate credit.
- **NonCommercial**: You may not use the material for commercial purposes.
- **NoDerivatives**: If you remix, transform, or build upon the material, you may not distribute the modified material.

For any uses beyond the scope of this license (such as commercial use or creating derivatives), please reach out to the repository owner for explicit permission. See the [LICENSE](LICENSE) file for details.
