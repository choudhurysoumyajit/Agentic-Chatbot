from agentic_chatbot_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import streamlit as st
import uuid

#Generate a unique thread id for each session
def generate_thread_id():   
    return str(uuid.uuid4())

#Add thread id to the conversation list
def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_chat_history(thread_id):
    state = chatbot.get_state({"configurable": {"thread_id": thread_id}})
    messages = state.values.get("messages", [])
    return [
        {"role": message.type, "content": message.content}
        for message in messages
        if message.type in {"human", "ai"}
    ]

# Once clicked the new Chat button, everything will clear out and a new window will open

def reset_chat():
    st.session_state["chat_history"] = []
    st.session_state["thread_id"] = generate_thread_id()
    add_thread(st.session_state["thread_id"])

    
st.title("Agentic Chatbot with Langgraph")

#Create Chat History when the app runs for the first time
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

#Create a thread id when app runs for the first time
if "thread_id" not in st.session_state:   
    st.session_state["thread_id"] = generate_thread_id()

     
#Create a list for storing all the chat threads
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []
add_thread(st.session_state["thread_id"])

#================== sidebar threading feature ==========================
st.sidebar.title("My Conversations")
# Creat e a new chat button
if st.sidebar.button("New Chat"):
    reset_chat()
    #Rerun the streamlit app to update the interface
    st.rerun()

# Display the list of chat threads in the sidebar in Reverse order (latest first)
for thread_id in reversed(st.session_state["chat_threads"]):
    if st.sidebar.button(thread_id, key=thread_id):
        st.session_state["thread_id"] = thread_id
        # Load the chat history for the selected thread
        st.session_state["chat_history"] = load_chat_history(thread_id)
        # Rerun the streamlit app to update the interface
        st.rerun()


# Loading the chat history from the session state

for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])

user_input = st.chat_input("Type Here: ")

if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    ## Streaming response from the chatbot
    # First add the mesaage to Chat history    

    thread_id = st.session_state["thread_id"]
    config = {"configurable": {"thread_id": thread_id}}

    with st.chat_message("assistant"):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]}, config=config,
                    stream_mode="messages")
                # Display only AI messages in the stream
                if isinstance(message_chunk, AIMessage)
            )
    
    st.session_state["chat_history"].append({"role": "assistant", "content": ai_message})

# Return the Reponse as a block

#    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
#    ai_message = response["messages"][-1].content
#
#    st.session_state["chat_history"].append({"role": "assistant", "content": ai_message})
#    with st.chat_message("assistant"):
#        st.text(ai_message)




    