"""LangGraph workflow for conversation analysis."""

from langgraph.graph import END, START, StateGraph

from app.application.analysis_agent.nodes.analysis import analysis_node
from app.application.analysis_agent.nodes.guardrail import guardrail_node
from app.application.analysis_agent.nodes.retrieval import retrieval_node
from app.domain.agent import GraphState


def create_graph():
    """Create the analysis agent graph with guardrail."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("analysis", analysis_node)

    # Add edges
    # START -> guardrail -> retrieval -> analysis -> END
    workflow.add_edge(START, "guardrail")
    workflow.add_edge("guardrail", "retrieval")
    workflow.add_edge("retrieval", "analysis")
    workflow.add_edge("analysis", END)

    return workflow.compile()


# Create a singleton instance
analysis_graph = create_graph()
