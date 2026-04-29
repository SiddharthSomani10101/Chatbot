import streamlit as st
from openai import OpenAI
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

prompt = "Do "

# ---- Setup ----
llm = ChatOpenAI(model="gpt-4o-mini",api_key="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")
agent = create_agent(model=llm,system_prompt=prompt)

st.set_page_config(page_title="GenAI Chatbot", layout="wide")

st.title("💬 GenAI Chatbot")

# ---- Session State (IMPORTANT) ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Display Chat History ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- User Input ----
prompt = st.chat_input("Ask something...")

if prompt:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # ---- LLM Response ----

    response  = agent.invoke(
         {"messages": st.session_state.messages}
    )

    reply = response["messages"][-1].content

    # Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)