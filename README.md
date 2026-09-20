# Agentic Chatbot

A small LangGraph + Groq proof of concept for building a stateful chatbot workflow in Python.

## Current Progress

- Added a Streamlit chat interface in [app.py](app.py).
- Added the LangGraph chatbot backend in [agentic_chatbot_backend.py](agentic_chatbot_backend.py).
- Successfully configured the app to load environment variables through `python-dotenv`.
- Integrated LangChain's `ChatGroq` with the `openai/gpt-oss-20b` model.
- Built a typed graph state using `TypedDict` and `add_messages` for message history merging.
- Added a `chat_node` that sends the conversation to the LLM and returns the model response.
- Compiled the graph using `START -> chat_node -> END`.
- Added `MemorySaver` for in-memory conversation persistence within a session.
- Added a configurable `thread_id` pattern for graph invocation.

This is now a working prototype that can be run locally as a simple conversational app.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- A valid Groq API key

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key
```

Do not commit this file to version control.

## Run the App

Start the Streamlit UI:

```bash
uv run streamlit run app.py
```

Type a prompt in the chat box and the app will send it to the LangGraph chatbot backend.

## Important Notes

- The app currently expects a valid `GROQ_API_KEY` in the environment.
- `st.chat_input()` returns `None` when there is no submitted message, so the app should guard against empty input before creating a `HumanMessage`.
- The notebook prototype in [chatbot_workflow.ipynb](chatbot_workflow.ipynb) is still useful for experimenting with the graph flow, but the Python app is the main runnable version.

## Project Structure

```text
.
├── app.py                        # Streamlit chatbot UI
├── agentic_chatbot_backend.py    # LangGraph + Groq backend
├── chatbot_workflow.ipynb        # Notebook prototype
├── pyproject.toml                # Project metadata and dependencies
├── README.md                     # Project documentation
└── src/
    └── agentic_chatbot/
        └── __init__.py          # Package scaffold
```

## Next Steps

- Add input validation for empty or `None` chat submissions.
- Add error handling for missing or invalid Groq credentials.
- Add tests for state updates and thread behavior.
- Move the prototype into a cleaner package structure.
- Replace the in-memory checkpointer with a durable storage option for production use.
