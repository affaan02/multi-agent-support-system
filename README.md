# Generative AI Multi-Agent Support System

## Overview
This repository contains a Generative AI-powered Multi-Agent System designed to assist customer support executives by seamlessly querying both structured SQL data and unstructured knowledge bases via natural language.

## Architecture
- **Orchestration**: `LangGraph` handles stateful routing (ReAct agent) to determine the appropriate tool for the user's query.
- **Model Context Protocol (MCP)**: `FastMCP` is utilized to expose the underlying data retrieval functions, decoupling the LLM reasoning from the database execution.
- **Structured Data**: `sqlite3` database for real-time customer profile and ticket history retrieval.
- **Unstructured Data**: `ChromaDB` (Vector DB) running a custom offline embedding function to securely process and retrieve policy context from PDFs.
- **LLM Engine**: `openai/gpt-oss-20b` via `Langchain-Groq` for high-speed routing and inference.
- **Frontend**: `Streamlit` providing the chat-based user interface.

## Project Setup & Usage
1. Clone this repository and ensure Python 3.10+ is installed.
2. Install dependencies: `pip install fastmcp langchain langgraph streamlit pypdf langchain-groq chromadb`
3. Ensure your `customers.db` and `policy.pdf` files are generated and located in the root directory.
4. Launch the UI: `streamlit run app.py`
5. Input your Groq API key in the sidebar and interact with the agent.