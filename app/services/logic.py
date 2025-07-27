import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Set this up once at app startup, not every time
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def enhance_query(question: str) -> str:
    """
    Uses Gemini 2.0 Flash to rephrase a user query into a more specific one
    to improve semantic search relevance.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Gemini's API is synchronous, so run it in a thread
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def generate_response():
            full_prompt = (
                "You are a query rewriting expert for a legal and insurance document retrieval system using vector embeddings. "
                "Your goal is to convert user questions into concise, semantically rich, declarative-style search queries. "
                "The rewritten query must resemble how information is phrased in actual documents (e.g., contracts, policies, clauses), "
                "not as an instruction or request. Do NOT return multiple options. Return ONLY one refined version. "
                "Return only one single-line output with no formatting, no headings, and no options."
                "Avoid adding explanations or formatting. Do not say 'Find', 'Analyze', or 'Compare'.\n\n"
                f"Original question: {question}\n"
                "Rewritten embedding search query:"
            )

            return model.generate_content(full_prompt)

        with ThreadPoolExecutor() as executor:
            response = await asyncio.get_event_loop().run_in_executor(executor, generate_response)

        enhanced_q = response.text.strip()
        print(f"Original Query: {question} -> Enhanced Query: {enhanced_q}")
        return enhanced_q

    except Exception as e:
        print(f"Error enhancing query: {e}")
        return question  # Fallback to the original question
