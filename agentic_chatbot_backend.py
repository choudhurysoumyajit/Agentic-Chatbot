from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langgraph.graph.message import add_messages
#For persistance
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] #Reducer


def chat_node(state: ChatState):
    messages = state["messages"]
#send to llm
    response = llm.invoke(messages)
    return {"messages" : [response]}


checkpoint = MemorySaver()

graph = StateGraph(ChatState)
# Add nodes and edges to the graph
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpoint)

