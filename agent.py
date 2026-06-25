# agent.py
import os
import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools import tools
from models import DegreePlan

# 1. Define the State
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    degree_plan: DegreePlan
    step_count: int

# 2. Initialize the LLM and bind tools
llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b")
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define the Nodes
def agent_node(state: GraphState):
    """Calls the LLM with the current messages and state."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Increment step count
    current_steps = state.get("step_count", 0)
    return {"messages": [response], "step_count": current_steps + 1}

# 4. Define the Routing Logic (Edges)
def should_continue(state: GraphState):
    """Determines whether to execute a tool, end, or stop due to limits."""
    messages = state["messages"]
    last_message = messages[-1]
    current_steps = state.get("step_count", 0)
    max_steps = int(os.getenv("AGENT_MAX_STEPS", 10))
    
    # Hard step limit check
    if current_steps >= max_steps:
        return "end"
        
    # If LLM didn't call a tool, we are done
    if not last_message.tool_calls:
        return "end"
        
    # Otherwise, execute the requested tool
    return "continue"

# 5. Build and Compile the Graph
workflow = StateGraph(GraphState)

workflow.add_node("agent", agent_node)
workflow.add_node("tool_executor", ToolNode(tools))

workflow.set_entry_point("agent")

# Add conditional routing from the agent
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tool_executor",
        "end": END
    }
)

# After a tool runs, always go back to the agent to evaluate the result
workflow.add_edge("tool_executor", "agent")

app_graph = workflow.compile()