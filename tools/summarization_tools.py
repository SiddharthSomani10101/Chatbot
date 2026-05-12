

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
    model="gpt-4o-mini",
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
        Generates context for a given user query by performing similarity search
        on the vector database.

        Depending on the query type, it retrieves relevant chunks of information
        from the HR policy documents to provide accurate and concise answers.

        Returns:
        - A string containing the most relevant context for answering the query.
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