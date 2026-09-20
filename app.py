from agentic_chatbot_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import streamlit as st

st.title("Agentic Chatbot with Langgraph")

thread_id = 1
config = {"configurable": {"thread_id": thread_id}}

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

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

    with st.chat_message("assistant"):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]}, config=config,
                    stream_mode="messages")
            )
    
    st.session_state["chat_history"].append({"role": "assistant", "content": ai_message})

# Return the Reponse as a block

#    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
#    ai_message = response["messages"][-1].content
#
#    st.session_state["chat_history"].append({"role": "assistant", "content": ai_message})
#    with st.chat_message("assistant"):
#        st.text(ai_message)




    