
from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, CachePolicy, interrupt
from langgraph.runtime import Runtime
from langgraph.types import RetryPolicy, TimeoutPolicy
from langgraph.errors import NodeError

from langchain_core.messages import (
    BaseMessage, SystemMessage, HumanMessage, ToolMessage
)
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from IPython.display import Image, display
from operator import add
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
from langgraph.graph import StateGraph

from agent.nodes import analyzer_node
from agent.state import HealthAgentState

run_health_agent = (
    StateGraph(HealthAgentState)
    .add_node("analyzer", analyzer_node)
    .add_edge(START, "analyzer")
    .add_edge("analyzer", END)
    .compile()
)