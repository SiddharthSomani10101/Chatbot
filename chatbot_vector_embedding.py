 # Use LLM chain for compare
# Evaluate the result for comparision 
# Evalaute the result for summarization
# Evaluate the result for factual question answering
# similarity search for factual question answering change K to adapt according to situation


import streamlit as st
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tools import generate_sql_query, create_retrieval_tool, execute_sql_queries
from dotenv import load_dotenv
import os


def chatbot():

   load_dotenv()
   api_key = os.getenv("API_KEY")



   prompt = """
   You are an intelligent HR and Workforce Management Assistant.

   Responsibilities:
   - Answer HR policy questions
   - Explain company rules clearly
   - Handle employee allocation, shifts, roles, and streams
   - Assist with workforce balancing and operational decisions
   - Generate safe SQL-based workforce operations when required

   Available Tables:
   - Employee
   - Role
   - Shift
   - Stream
   - EmployeeAllocation

   Rules:
   1. Answer only using retrieved context, database results, or policy documents.
      If information is unavailable, say:
      "This is not explicitly defined in the available data."

   2. For policy questions:
      - use retrieval tools
      - do not assume missing rules

   3. For operational/database queries:
      - inspect current database state first
      - never assume values
      - use SQL tools when needed

   4. Allowed SQL operations:
      - SELECT
      - INSERT
      - UPDATE
      - DELETE

   5. Never generate schema-changing operations such as:
      - CREATE TABLE
      - ALTER TABLE
      - DROP TABLE
      - TRUNCATE TABLE

   6. For Insert/Update/Delete operations:
      - Always check current state before modifying
      - Never assume values or states
      - Generate operations only when necessary
      - Always ask user for confirmation before executing modifications when the operation is not a direct one mentioned by the user 
        e.g Move 3 least worked employees to Shift A. Mention the names of the employees and ask for confirmation before executing.   


   9. If the request is unclear:
      - ask clarification questions
      - never assume intent

   10. Keep responses:
      - professional
      - concise
      - operationally clear

   Available Tools:
   1. Retrieval Tool
      - retrieves HR policy context using vector search

   2. SQL Execution Tool
      - executes safe SQL queries
      - returns database results

   Examples:
   - What is the leave policy?
   - Compare contractor and employee leave rules
   - Show employees in Shift A
   - Create a new shift named A
   - Move least worked employees to Shift A
   - Rebalance employees across streams
   """




   



   st.set_page_config(page_title="GenAI Chatbot with Vector Embeddings", layout="wide")




   st.title("💬 GenAI Chatbot")

   # ---- Session State (IMPORTANT) ----
   if "messages" not in st.session_state:
      st.session_state.messages = []

   # ---- Display Chat History ----
   for message in st.session_state.messages:
      with st.chat_message(message["role"]):
         st.markdown(message["content"])


   def load_file(file_path):
      with open(file_path, "r", encoding="utf-8") as f:
         return f.read() 


   text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=400,
      chunk_overlap=20,
      separators = [
      "\n\\d+\\.\\s",        # matches "2. PASSWORD..."
      "\n\\d+\\.\\d+\\s",    # matches "2.1 Password..."
      "--------------------------------------------------",
      "\n\n",
      "\n",
   ]
   )

   hr_text = load_file("Policy_documents/hr_leave_policy.txt")
   large_text = load_file("Policy_documents/Large.txt")

   chunks = text_splitter.split_text(hr_text) + text_splitter.split_text(large_text)
   embeddings = OpenAIEmbeddings(api_key=api_key)

   db = FAISS.from_texts(chunks, embeddings)


   context_tool = create_retrieval_tool(db, chunks)


   # ---- Setup ----
   llm = ChatOpenAI(model="gpt-4o-mini",api_key=api_key)
   agent = create_agent(model=llm,system_prompt=prompt,tools=[context_tool, execute_sql_queries])

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

   # Add the original user message without context

      reply = response["messages"][-1].content

      # Store assistant message
      st.session_state.messages.append({"role": "assistant", "content": reply})

      with st.chat_message("assistant"):
         st.markdown(reply)




               
if __name__ == "__main__":
   chatbot()










