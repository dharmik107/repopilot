import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from backend.vector_store import get_vector_store

# State definition
class AgentState(TypedDict):
    query: str
    retrieved_docs: List[str]
    evaluation: str
    response: str
    retry_count: int

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.0
)

# Nodes
def query_agent(state: AgentState):
    return {"retry_count": state.get("retry_count", 0)}

def retrieval_agent(state: AgentState):
    vector_store = get_vector_store()
    k = 6 if state["retry_count"] == 0 else 12
    search_query = state.get("query", state["query"])
    
    # Fast retrieval
    docs = vector_store.similarity_search(search_query, k=k)
    doc_texts = [f"[{d.metadata.get('source', 'src')}] {d.page_content}" for d in docs]
    return {"retrieved_docs": doc_texts}

def fast_evaluator_agent(state: AgentState):
    """Combines evaluation and refinement check for speed."""
    docs_text = "\n".join(state["retrieved_docs"][:3]) # Check top 3 for speed
    prompt = f"Query: {state['query']}\nContext Snippet: {docs_text}\nIs this enough to answer? (YES/NO)"
    
    res = llm.invoke([HumanMessage(content=prompt)]).content.strip().upper()
    evaluation = "YES" if "YES" in res else "NO"
    return {"evaluation": evaluation}

def query_refiner(state: AgentState):
    prompt = f"Question: {state['query']}\nFailed to find info. Rephrase for a high-level code search (look for README/headers/metadata). Just the query."
    refined_query = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    return {"query": refined_query, "retry_count": state["retry_count"] + 1}

def response_agent(state: AgentState):
    docs_text = "\n\n".join(state["retrieved_docs"])
    # Dynamic prompt based on evaluation
    if state["evaluation"] == "YES":
        sys_msg = "Answer based on context. Be concise. Identify project name/assets if asked."
    else:
        sys_msg = "Context is limited. Give your best helpful guess or admit missing info. Be fast."
    
    prompt = f"Context:\n{docs_text}\n\nUser: {state['query']}\n\nAssistant:"
    response = llm.invoke([HumanMessage(content=prompt)]).content
    return {"response": response}

# Routing
def fast_route(state: AgentState):
    if state["evaluation"] == "YES" or state["retry_count"] >= 1:
        return "generate"
    return "retry"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("query_agent", query_agent)
builder.add_node("retrieval_agent", retrieval_agent)
builder.add_node("fast_evaluator_agent", fast_evaluator_agent)
builder.add_node("query_refiner", query_refiner)
builder.add_node("response_agent", response_agent)

builder.set_entry_point("query_agent")
builder.add_edge("query_agent", "retrieval_agent")
builder.add_edge("retrieval_agent", "fast_evaluator_agent")

builder.add_conditional_edges(
    "fast_evaluator_agent",
    fast_route,
    {
        "generate": "response_agent",
        "retry": "query_refiner"
    }
)

builder.add_edge("query_refiner", "retrieval_agent")
builder.add_edge("response_agent", END)

graph = builder.compile()

def solve_query(query: str):
    initial_state = {"query": query, "retrieved_docs": [], "evaluation": "", "response": "", "retry_count": 0}
    result = graph.invoke(initial_state)
    return result["response"]
