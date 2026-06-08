from langgraph.graph import StateGraph, START, END

from langgraph.graph import StateGraph

from agent.nodes import analyzer_node, generator_node
from agent.state import HealthAgentState

run_health_agent = (
    StateGraph(HealthAgentState)
    .add_node("analyzer", analyzer_node)
    .add_node("generator", generator_node)
    .add_edge(START, "analyzer")
    .add_edge("analyzer", "generator")
    .add_edge("generator", END)
    .compile()
)