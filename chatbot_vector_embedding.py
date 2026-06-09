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
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from tools import create_retrieval_tool 
from dotenv import load_dotenv
import os
from langsmith import Client as SmithClient
from langsmith import traceable
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool, QuerySQLDatabaseTool
from tools.sql_toos import SafeQuerySQLDatabaseTool, SafeQuerySQLCheckerTool
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain.agents.middleware import HumanInTheLoopMiddleware




def chatbot():

   # cache = InMemoryCache()

   # set_llm_cache(cache)

   load_dotenv()
   api_key = os.getenv("API_KEY")
   langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

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


   2. sql_db_query: 
      Input to this tool is a detailed and correct SQL query, output is a result from 
      the database. If the query is not correct, an error message will be returned. 
      If an error is returned, rewrite the query, check the query, and try again.  
      If you encounter an issue with Unknown column 'xxxx' in 'field list',
      use sql_db_schema to query the correct table fields.

   3. sql_db_schema: Input to this tool is a comma-separated list of tables, output 
      is the schema and sample rows for those tables. Be sure that the tables actually
        exist by calling sql_db_list_tables first! Example Input: table1, table2, table3

   4. sql_db_list_tables: 
      Input is an empty string, output is a comma-separated list of tables in the database.

   5. sql_db_query_checker:
     Use this tool to double check if your query is correct before executing it. Always use this tool before executing a query with sql_db_query!

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

   llm = ChatOpenAI(model="gpt-5.4-nano", api_key=api_key,temperature=0.1)
   #llm = ChatOpenAI(model="gpt-5.4-nano",api_key=api_key)
 
   db_connection = SQLDatabase.from_uri("sqlite:///KGP_OPS.db")

   toolkit = SQLDatabaseToolkit(db=db_connection, llm=llm, verbose=True)
   
   SafeQuerySQLDatabaseTool(db=db_connection, llm=llm, verbose=True)

   tools = toolkit.get_tools()

   for tool in tools:
      if tool.__class__ == QuerySQLDatabaseTool:
            tool.__class__ = SafeQuerySQLDatabaseTool
      if tool.__class__ == QuerySQLCheckerTool:
            tool.__class__ = SafeQuerySQLCheckerTool

   human_in_the_loop = HumanInTheLoopMiddleware(

   interrupt_on={
        "sql_db_query": {
            "allowed_decisions": [
                "approve",
                "reject"
                  ]
            }
         }
      )



   agent = create_agent(model=llm,system_prompt=prompt,tools=[context_tool]+tools)

   # ---- User Input ----
   prompt = st.chat_input("Ask something...")


   if prompt:
      # Store user message

      
      st.session_state.messages.append({"role": "user", "content": prompt})

      with st.chat_message("user"):
         st.markdown(prompt)

      # ---- LLM Response ----

      # print("\n\n\n  cache.data before: \n\n\n", cache.__dict__)


      @traceable(run_type="chain", project_name="first")
      def run_agent(agent, messages):
         return agent.invoke({"messages": messages})
      
      response = run_agent(agent, st.session_state.messages)

   # Add the original user message without context

      reply = response["messages"][-1].content

      # Store assistant message
      st.session_state.messages.append({"role": "assistant", "content": reply})

      with st.chat_message("assistant"):
         st.markdown(reply)

      # print("\n\n\n  cache.data: \n\n\n", cache.__dict__)




               
if __name__ == "__main__":
   chatbot()










