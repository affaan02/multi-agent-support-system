import streamlit as st
import httpx
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from mcp_server import get_customer_data as mcp_customer
from mcp_server import get_policy_info as mcp_policy

# Wrap MCP endpoints into LangChain tools
@tool
def customer_lookup(customer_name: str) -> str:
    """Use this to get customer profiles and past support ticket details."""
    return mcp_customer(customer_name)

@tool
def policy_lookup(query: str) -> str:
    """Use this to look up company policies, refund rules, and document info."""
    return mcp_policy(query)

# UI Setup
st.set_page_config(page_title="Support Multi-Agent", layout="wide")
st.title("Customer Support Multi-Agent System")
st.caption("Powered by LangGraph, FastMCP, and Groq")

api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("E.g., 'Overview of customer Ema' or 'What is the refund policy?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not api_key:
        st.error("Please paste your Groq API Key in the sidebar.")
        st.stop()

    # Bypass Canopy SSL interception
    custom_client = httpx.Client(verify=False)
    
    # Initialize LangGraph Agent
    llm = ChatGroq(
        groq_api_key=api_key, 
        model_name="openai/gpt-oss-20b", 
        temperature=0,
        http_client=custom_client
    )
    tools = [customer_lookup, policy_lookup]
    agent_executor = create_react_agent(llm, tools)

    with st.spinner("Agent processing across MCP databases..."):
        response = agent_executor.invoke({"messages": [("user", prompt)]})
        final_answer = response["messages"][-1].content
        
    st.session_state.messages.append({"role": "assistant", "content": final_answer})
    st.chat_message("assistant").write(final_answer)