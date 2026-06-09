

from langchain.tools import tool
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_protocol import Literal
from dotenv import load_dotenv
import os



load_dotenv()
api_key = os.getenv("API_KEY")




class Category(BaseModel):
    category: Literal["summarize", "compare", "reasoning", "factual"]


llm = ChatOpenAI(
    model="gpt-5.4-nano",
    api_key=api_key,
)

structured_llm = llm.with_structured_output(Category)


def classify_query(query: str) -> str:

    response = structured_llm.invoke(
        f"""Classify the query into one of these categories:

         1. summarize  - The user is asking for a summary of the entire document.

         2. compare  - The user is asking for differences or similarities between two or more entities, policies, or concepts.

         3. reasoning  - The query requires combining information from multiple sections, interpreting rules, or answering "what happens", "why", or conditional scenarios.

        4. factual  - A direct question that can be answered from a single piece of information or section without combining multiple rules.

        Return JSON in the format:
        {{"category": "<one_of_the_above>"}}

        Query: {query}
        """
        )
    
    return response.category



def create_retrieval_tool(db, chunks):

    @tool
    def create_context(query: str) -> str:
        """

        Retrieves relevant HR policy and company document context
            using vector similarity search.

            This tool should be used when the user query requires:
            - HR policy information
            - company rules or compliance details
            - document summarization
            - comparison between policies or rules
            - reasoning across multiple document sections
            - factual answers from policy documents

            Examples:
            - What is the leave policy?
            - Summarize the remote work policy
            - Compare contractor and employee leave rules
            - What happens if an employee exceeds leave balance?

            Depending on the query type, the tool may:
            - summarize relevant sections
            - retrieve factual chunks
            - retrieve multiple sections for comparison or reasoning

            Returns:
            - Relevant document context that the agent can use
            to generate grounded and accurate responses
        
        """
        print("running generate_context")

        category = classify_query(query)
        print("category =", category)

        if category == "summarize":
            context = "\n\n".join(chunks)
        elif category == "factual":
            ans = db.similarity_search(query, k=1)
            context = "\n\n".join([doc.page_content for doc in ans])
        elif category == "compare":        
            ans = db.similarity_search(query, k=2)
            context = "\n\n".join([doc.page_content for doc in ans])

        return context
    
    return create_context