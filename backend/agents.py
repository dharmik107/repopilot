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
    # Just pass through or initialize if needed
    return {"retry_count": state.get("retry_count", 0)}

def retrieval_agent(state: AgentState):
    vector_store = get_vector_store()
    # Boost k on retries to get more context
    k = 5 if state["retry_count"] == 0 else 10
    
    # Use refined query if available, otherwise original
    search_query = state.get("query", state["query"])
    docs = vector_store.similarity_search(search_query, k=k)
    doc_texts = [f"File: {d.metadata.get('source', 'unknown')}\nContent: {d.page_content}" for d in docs]
    return {"retrieved_docs": doc_texts}

def evaluator_agent(state: AgentState):
    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    prompt = f"""
    User Query: {state['query']}
    
    Current Context Found:
    {docs_text}
    
    Task: Evaluate if the provided context contains enough information to answer the User Query accurately.
    Consider:
    - If the user asks for a project name, look for headers in README or package names.
    - If the user asks for purpose, look for descriptions.
    - If the user asks for code details, look for relevant functions/classes.
    
    Answer ONLY 'YES' if it's sufficient, or 'NO' if more information is needed.
    """
    evaluation = llm.invoke([HumanMessage(content=prompt)]).content.strip().upper()
    # Clean up the output in case LLM adds extra text
    evaluation = "YES" if "YES" in evaluation else "NO"
    return {"evaluation": evaluation}

def query_refiner(state: AgentState):
    # Try to rephrase the query to find broader or more specific info
    prompt = f"Original Query: {state['query']}\n\nWe couldn't find enough info in the code. Rephrase this query to better find general project metadata, README content, or project headers in a vector database search. Only output the new query."
    refined_query = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    return {"query": refined_query, "retry_count": state["retry_count"] + 1}

def response_agent(state: AgentState):
    docs_text = "\n\n---\n\n".join(state["retrieved_docs"])
    if state["evaluation"] == "YES":
        prompt = f"""
        User Query: {state['query']}
        
        Context:
        {docs_text}
        
        Answer the user's question clearly and concisely based ONLY on the provided context. 
        If it's about the project name or purpose, extract it from the most relevant file (like README).
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content
    else:
        # Final fallback - attempt best guess based on what was found
        prompt = f"""
        User Query: {state['query']}
        
        Context (Incomplete):
        {docs_text}
        
        We couldn't find a perfect answer, but based on this incomplete context, provide the most helpful response possible.
        If you truly have no clue, say "I'm sorry, I'm not able to find the relevant information in the repository to answer your question perfectly."
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content
    return {"response": response}

# Routing logic
def should_continue(state: AgentState):
    if state["evaluation"] == "YES":
        return "generate"
    elif state["retry_count"] < 2:
        return "retry"
    else:
        return "generate"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("query_agent", query_agent)
builder.add_node("retrieval_agent", retrieval_agent)
builder.add_node("evaluator_agent", evaluator_agent)
builder.add_node("query_refiner", query_refiner)
builder.add_node("response_agent", response_agent)

builder.set_entry_point("query_agent")
builder.add_edge("query_agent", "retrieval_agent")
builder.add_edge("retrieval_agent", "evaluator_agent")

builder.add_conditional_edges(
    "evaluator_agent",
    should_continue,
    {
        "generate": "response_agent",
        "retry": "query_refiner"
    }
)

builder.add_edge("query_refiner", "retrieval_agent")
builder.add_edge("response_agent", END)

graph = builder.compile()

def solve_query(query: str):
    initial_state = {
        "query": query,
        "retrieved_docs": [],
        "evaluation": "",
        "response": "",
        "retry_count": 0
    }
    result = graph.invoke(initial_state)
    return result["response"]
