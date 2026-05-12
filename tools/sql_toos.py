from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from db_queries import get_connection
import os



load_dotenv()
api_key = os.getenv("API_KEY")


class SQLPlan(BaseModel):
    operation_type: str
    reasoning_summary: str
    subquery: str


@tool
def execute_sql_queries(sql_query: str) -> str:
    """
    Executes a Read, Insert, Update, or Delete SQL query on the database.

    This tool is used by the agent to perform database operations.

    Allowed:
    - SELECT, INSERT, UPDATE, DELETE queries

    Example queries:
    - SELECT COUNT(*) FROM Employee
    - SELECT * FROM EmployeeAllocation
    - SELECT * FROM Employee WHERE allocated = 0
    - INSERT INTO Employee (name, email) VALUES ('John Doe', 'john.doe@example.com')
    - UPDATE Employee SET email = 'new.email@example.com' WHERE id = 1
    - DELETE FROM Employee WHERE id = 1

    Returns:
    - Query execution results as a string
    """

    print("query to execute = \n", sql_query)

    try:

        # -----------------------------
        # Safety Validation
        # -----------------------------
        cleaned_query = sql_query.strip().lower()

        if not cleaned_query.startswith(("select", "insert", "update", "delete")):
            return "ERROR: Only SELECT, INSERT, UPDATE, and DELETE queries are allowed."

        forbidden_keywords = [
            "drop",
            "alter",
            "truncate",
            "create"
        ]

        for keyword in forbidden_keywords:
            if keyword in cleaned_query:
                return f"ERROR: Forbidden SQL keyword detected: {keyword}"

        # -----------------------------
        # Database Execution
        # -----------------------------
        conn = get_connection()

        cursor = conn.execute(sql_query)

        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]

        # -----------------------------
        # Format Results
        # -----------------------------
        results = []

        for row in rows:
            results.append(dict(zip(columns, row)))
        
        print("results = \n ", results)

        return str(results)

    except Exception as e:

        return f"ERROR: {str(e)}"



@tool
def generate_sql_query(user_query: str) -> dict:
    """
    Processes a natural language request related to employee allocation
    and workforce management.

    The function may:
    - run SELECT queries to inspect current database state
    - analyze constraints and feasibility
    - determine whether INSERT, UPDATE, or DELETE operations are required
    - generate a structured execution plan for database modification

    Before executing any modification query, the generated plan should
    be shown to the user for confirmation.

    Returns:
    - inspection results
    - reasoning summary
    - proposed SQL operation details
    """
    print("running generate_sql_query")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
    )
        
    structured_llm = llm.with_structured_output(SQLPlan)

    result = structured_llm.invoke(
        f"""You are an enterprise SQL planning assistant.

        For the following user request:
        "{user_query}"

        Rules:
        1. Understand the business intent
        2. Decide whether INSERT, UPDATE, DELETE or SELECT is needed
        3. Generate a safe SQL query
        4. Provide a short reasoning summary

        Return structured output with 
        - operation_type: one of "SELECT", "INSERT", "UPDATE", "DELETE"
        - reasoning_summary: a brief explanation of your reasoning
        - subquery: the SQL query you propose to run 
        """)
    
    print("result =", result)

    return result