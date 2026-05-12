import streamlit as st
from openai import OpenAI
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

prompt = """
You are an intelligent HR Assistant for a company's HR Management System.

Your responsibilities include:
- Answering employee questions about HR policies
- Explaining company rules in a clear and concise way
- Assisting with employee-specific queries such as leave balance, manager info, and salary (only when data is available)

STRICT RULES:
1. You must answer ONLY if the answer is explicitly stated in the context.
   If the question requires interpretation or is ambiguous, respond:
   This is not explicitly defined in the document.

2. For policy-related questions:
   - Answer based only on company policy documents
   - Keep responses professional and structured
3. For employee-specific queries:
   - Use available tools or data
   - Do NOT guess values

4. Always be:
   - Professional
   - Concise
   - Helpful

5. If the question is unclear:
   - Ask a clarification question instead of assuming

6. Do NOT provide:
   - Legal advice
   - Personal opinions
   - Information outside HR scope

RESPONSE STYLE:
- Use bullet points when appropriate
- Keep answers short but informative
- Highlight key numbers (e.g., leave days, weeks)

"""

@tool
def read_hr_policy(_input: str = None) -> str:
    """
    Reads the HR leave policy document (hr_leave_policy.txt)
    and returns the full content including:
    - annual leave
    - sick leave
    - company rules
    """
    with open("hr_leave_policy.txt", "r", encoding="utf-8") as f:
        return f.read()
    

@tool
def read_large(_input: str = None) -> str:
    """
    Reads the Large.txt document that defines IT policies, support procedures,
    security protocols, and compliance requirements for all employees
    and returns the full content including
    """
    with open("Large.txt", "r", encoding="utf-8") as f:
        return f.read()    


# ---- Setup ----
llm = ChatOpenAI(model="gpt-4o-mini",api_key="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")
agent = create_agent(model=llm,tools=[read_hr_policy, read_large],system_prompt=prompt)

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

    # print("response =", response)

    reply = response["messages"][-1].content

    # Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)
