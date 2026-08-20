# AI PR Agent

An intelligent agent system for automated pull request reviews and analysis using vector embeddings and skill-based architecture.

## Overview

This project provides an AI-powered solution for reviewing and analyzing pull requests. It leverages a modular skill system, vector embeddings, and a git server to provide comprehensive PR insights and feedback.

## Project Structure

- **agent_pr.py** - Main PR agent logic
- **agent.py** - Core agent implementation
- **git_server.py** - Git server integration for PR handling
- **skills_loader.py** - Dynamic skill loading and management
- **vector_server.py** - Vector embedding server for semantic analysis
- **skills/** - Collection of reusable agent skills
  - **revisao-pr/** - PR review skill with templates and references

## Features

- Automated PR review and analysis
- Skill-based architecture for extensibility
- Vector embedding support for semantic understanding
- Git integration for seamless workflow
- Modular design for easy customization

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-bits
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

Run the PR agent:
```bash
python agent_pr.py
```

## Architecture

### Skills System
Skills are modular components that extend the agent's capabilities. Each skill is self-contained with its own configuration and templates.

### Vector Server
Provides semantic search and embedding capabilities for intelligent PR analysis.

### Git Server
Handles git operations and integrates with repositories for PR management.

## Configuration

Configuration files and environment variables can be set up in the .env file. Refer to `.env.example` for available options.

## Contributing

Contributions are welcome! Please ensure your code follows the project's style guidelines and includes appropriate tests.

## License

[Add your license information here]

## Support

For issues, questions, or suggestions, please open an issue on the repository.
