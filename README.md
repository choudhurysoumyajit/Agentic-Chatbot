# Agentic Chatbot

A small Streamlit, LangGraph, and Groq proof of concept. The main application is a stateful chatbot with a sidebar that lets the user create conversations and switch between older conversations.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- A valid Groq API key

## Setup

Install the dependencies from `pyproject.toml`:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key
```

`python-dotenv` loads this value when the backend is imported. Keep `.env` out of version control.

## Run the App

Start the threaded Streamlit application:

```bash
uv run streamlit run app_thread.py
```

The older `app_simple.py` file is a minimal single-thread example. It is useful for understanding the basic chat call, but `app_thread.py` is the main application.

## Application Control Flow

Streamlit reruns the entire Python script after most UI interactions. The app therefore uses `st.session_state` to preserve values between reruns. The important values are:

| Key | Purpose |
| --- | --- |
| `chat_history` | Messages currently displayed by the UI, represented as dictionaries with `role` and `content`. |
| `thread_id` | The conversation currently selected by the user. |
| `chat_threads` | The ordered list of known thread IDs used to build the sidebar. |

### 1. Backend import and helper functions

At startup, `app_thread.py` imports the compiled `chatbot` graph, Streamlit, LangChain message classes, and `uuid`.

`generate_thread_id()` creates a unique UUID string for a new conversation.

`add_thread(thread_id)` checks whether an ID is already in `chat_threads`. If it is not present, the ID is appended. Appending preserves creation order; the sidebar later calls `reversed(...)`, so the newest thread appears first.

`load_chat_history(thread_id)` reads the selected thread from LangGraph:

1. It builds a LangGraph configuration containing the requested `thread_id`.
2. It calls `chatbot.get_state(config)` to retrieve that thread's checkpointed state.
3. It reads the state's `messages` value.
4. It converts LangChain messages into the simpler dictionaries expected by the Streamlit renderer.
5. It keeps human and AI messages and ignores other message types.

### 2. Initial session setup

The app initializes missing session values in this order:

1. If `chat_history` does not exist, it is initialized to an empty list.
2. If `thread_id` does not exist, a UUID is generated for the first conversation.
3. If `chat_threads` does not exist, it is initialized to an empty list.
4. The current `thread_id` is passed to `add_thread`, ensuring the current conversation is visible in the sidebar.

Because these values live in `st.session_state`, they survive Streamlit reruns for the current browser session.

### 3. Creating a new conversation

The sidebar renders a `New Chat` button. When it is clicked:

1. `reset_chat()` clears the UI's `chat_history`.
2. It generates and stores a new `thread_id`.
3. It adds that ID to `chat_threads`.
4. `st.rerun()` immediately redraws the app using the new, empty conversation.

The new thread does not receive a LangGraph checkpoint until the first message is sent. It still appears in the sidebar because it has already been registered in `chat_threads`.

### 4. Displaying and selecting older conversations

The sidebar loops over `reversed(st.session_state["chat_threads"])`. This means IDs are shown in reverse creation order, with the most recently created thread first.

Each ID is rendered as a button with the ID as its label and key. When a thread button is clicked:

1. The selected ID becomes the current `thread_id`.
2. `load_chat_history(thread_id)` retrieves messages from that thread's LangGraph checkpoint.
3. The returned messages replace the current UI `chat_history`.
4. `st.rerun()` redraws the page and shows the selected conversation.

The UI list and the backend history have different responsibilities: `chat_threads` remembers which conversations should be offered in the sidebar, while LangGraph stores the messages associated with each ID.

### 5. Rendering the current conversation

After the sidebar logic, the app loops through `chat_history`. For each dictionary:

1. `message["role"]` selects the Streamlit chat-message style (`user` or `assistant`).
2. `message["content"]` is displayed inside that message block.

This happens on every rerun, so the selected thread and its complete history are rendered consistently.

### 6. Receiving and streaming a user message

`st.chat_input(...)` returns the submitted text or `None` when no message was submitted. The `if user_input:` guard prevents the backend from being called for an empty submission.

When a user submits text:

1. The user message is appended to the UI `chat_history`.
2. It is displayed immediately in a `user` chat block.
3. A LangGraph configuration is built with the current `thread_id`.
4. The text is wrapped in a LangChain `HumanMessage`.
5. `chatbot.stream(...)` invokes the graph in message-streaming mode.
6. `st.write_stream(...)` displays each AI content chunk as it arrives.
7. Only chunks that are instances of `AIMessage` are displayed.
8. Once streaming finishes, the assembled assistant text is appended to the UI `chat_history`.

The same `thread_id` is sent on every turn, which allows the checkpointer to associate later prompts with the correct conversation.

## Backend Control Flow

`agentic_chatbot_backend.py` defines and compiles the LangGraph workflow.

### Environment and model

`load_dotenv()` loads values from `.env`. `ChatGroq` is then configured with the `openai/gpt-oss-20b` model and a temperature of `0.7`. The model receives the message history supplied by the graph.

### Graph state

`ChatState` is a `TypedDict` with one field:

```python
messages: Annotated[list[BaseMessage], add_messages]
```

The field contains LangChain message objects. `add_messages` is the reducer used by LangGraph to merge new messages into the existing list instead of replacing the entire history.

### Chat node

`chat_node(state)` receives the current graph state, extracts `state["messages"]`, and passes the complete message list to the Groq model. It returns the model response inside a one-item `messages` list. The graph reducer adds that AI response to the thread history.

### Graph compilation and checkpoints

The graph is assembled as:

```text
START -> chat_node -> END
```

`MemorySaver` stores graph state in memory. When the app invokes or streams the graph with a configuration containing `thread_id`, LangGraph uses that ID to read and update the corresponding conversation. `chatbot.get_state(...)` uses the same ID to restore a conversation when the user selects it in the sidebar.

`MemorySaver` is process-local and non-durable: restarting the Streamlit process clears the backend's saved messages. The current sidebar thread list is also stored only in Streamlit session state, so production use would require a durable checkpointer and persistent thread metadata.

## Simple Example Flow

For a first prompt, the runtime sequence is:

```text
User submits text
    -> app appends the user message to chat_history
    -> app sends HumanMessage + current thread_id to chatbot.stream
    -> LangGraph loads that thread's state
    -> chat_node sends all messages to Groq
    -> graph returns AI message chunks
    -> Streamlit renders chunks and stores the completed answer
```

For an older conversation, the sequence is:

```text
User clicks a sidebar thread
    -> app sets thread_id
    -> app calls chatbot.get_state(thread_id)
    -> app converts checkpoint messages to chat_history dictionaries
    -> Streamlit reruns and renders the selected conversation
```

## Project Structure

```text
.
├── app_thread.py                # Main Streamlit UI with conversation threads
├── app_simple.py                # Minimal single-thread Streamlit example
├── agentic_chatbot_backend.py   # LangGraph workflow, Groq model, and checkpointer
├── chatbot_workflow.ipynb       # Notebook prototype for experimenting with the graph
├── pyproject.toml               # Project metadata and dependencies
├── README.md                    # Project documentation
└── src/
        └── agentic_chatbot/
                └── __init__.py          # Package scaffold
```

## Known Limitations and Next Steps

- `MemorySaver` loses conversations when the process restarts; replace it with a durable checkpointer for production.
- Thread labels are currently UUIDs; store a generated title or the first prompt for more readable sidebar labels.
- The UI and backend currently rely on valid Groq credentials; add user-facing error handling for missing or invalid credentials.
- Add automated tests for message reduction, thread switching, and new-chat behavior.
- Move the prototype into a cleaner package structure as the application grows.
