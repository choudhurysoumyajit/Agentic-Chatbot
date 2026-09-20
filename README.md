# Agentic Chatbot

A small LangGraph and Groq proof of concept for building a stateful chatbot workflow in Python.

## Current Progress

- Added a working Streamlit frontend in [`app.py`](app.py) for a simple chat UI.
- Added the LangGraph chatbot backend in [`agentic_chatbot_backend.py`](agentic_chatbot_backend.py).
- Loads environment variables with `python-dotenv` and reads the Groq API key from `.env`.
- Connects to Groq through LangChain's `ChatGroq` integration using the `openai/gpt-oss-20b` model.
- Defines a typed graph state containing a message history and uses `add_messages` to merge chat history correctly.
- Uses a single `chat_node` that sends the current conversation to the model and appends the response.
- Compiles the graph with `START -> chat_node -> END`.
- Adds LangGraph's in-memory `MemorySaver` checkpointer to support persistent state within the running session.
- Associates the conversation with a configurable `thread_id`, which is used when invoking the graph.
- Includes a working app entry point for local testing and UI interaction.

The core workflow is now implemented in the Python files rather than only in the notebook. The package entry point in [`src/agentic_chatbot/__init__.py`](src/agentic_chatbot/__init__.py) is still a scaffold and can be completed later.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- A Groq API key

## Setup

Install the project dependencies:

```bash
uv sync
```

Create a `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your-groq-api-key
```

Do not commit `.env` or expose the API key in the notebook.

## Run the App

Create a `.env` file in the project root with your Groq API key:

```env
GROQ_API_KEY=your-groq-api-key
```

Then start the Streamlit app:

```bash
uv run streamlit run app.py
```

This launches the chat UI, where you can type a prompt and receive a response from the LangGraph chatbot backend.

## Notebook Workflow

The earlier prototype still exists in [`chatbot_workflow.ipynb`](chatbot_workflow.ipynb). It remains useful for experimenting with the graph flow, but the project now also includes a runnable app-based version.

## Project Structure

```text
.
├── chatbot_workflow.ipynb     # Current chatbot prototype
├── pyproject.toml              # Project metadata and dependencies
└── src/
	└── agentic_chatbot/
		└── __init__.py         # Package entry point scaffold
```

## Next Steps

- Move the notebook workflow into the package source.
- Add tests for graph state updates, thread isolation, and chatbot responses.
- Add configuration and error handling for missing API credentials.
- Replace `MemorySaver` with a durable checkpointer for persistence across restarts.
- Decide whether to expose the interactive chatbot through the package CLI.
