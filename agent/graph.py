from langgraph.graph import StateGraph, START, END

from langgraph.graph import StateGraph

from agent.nodes import evaluator_node, route_after_eval
from agent.nodes import analyzer_node, generator_node
from agent.state import HealthAgentState

run_health_agent = (
    StateGraph(HealthAgentState)
    .add_node("analyzer", analyzer_node)
    .add_node("generator", generator_node)
    .add_node("evaluator", evaluator_node)
    .add_edge(START, "analyzer")
    .add_edge("analyzer", "generator")
    .add_edge("generator", "evaluator")
    .add_conditional_edges("evaluator", route_after_eval, {
        "generator": "generator",  # 不达标→回generator重写
        END: END
    })
    .compile()
)