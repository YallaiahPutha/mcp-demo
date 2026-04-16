# MCP Proof of Concept: Ollama + Pure MCP Tools

This project demonstrates a **Model Context Protocol (MCP)** implementation. It bridges a local LLM (**Ollama**) with external tools (Arithmetic, Weather, and Web Search) and provides both a **Command Line Interface (CLI)** and a **REST API**.

## 🏗️ Architecture
- **MCP Server (`server.py`)**: A standard MCP server hosting local tools.
- **MCP Client (`client.py`)**: A CLI tool to interact with the LLM and tools directly.
- **MCP API (`api.py`)**: A FastAPI wrapper that turns the MCP logic into a web service.
- **LLM**: Ollama (running `llama3.1`) serves as the reasoning engine.

## 📋 Prerequisites

1.  **Install Ollama**: [Download here](https://ollama.ai/)
2.  **Pull a Tool-Compatible Model**:
    ```bash
    ollama pull llama3.1
    ```
3.  **Python 3.10+** installed.

## 🚀 Setup & Installation

1. **Install required Python libraries**:
   ```bash
   pip install mcp ollama duckduckgo-search httpx fastapi uvicorn
