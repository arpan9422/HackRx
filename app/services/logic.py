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
               "You rewrite user queries into single-line, declarative statements for searching legal or insurance documents. Avoid instructions or questions—make it match how clauses are phrased in actual policies. Return only one rewritten query, no formatting, no explanations.\n\nOriginal question: {question}\nRewritten:"

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
