import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import google.generativeai as genai

# --- Load environment variables ---
load_dotenv()

ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configure Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Connect to Elasticsearch ---
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    api_key=ELASTIC_API_KEY,
    verify_certs=True
)

# --- Extract keywords from a sentence using Gemini ---
def extract_keywords(query):
    prompt = (
        "Extract the top 5 most important keywords or key phrases from the following query, "
        "comma separated only (no numbering or bullets):\n\n"
        f'"{query}"'
    )

    try:
        response = model.generate_content(prompt)
        keywords = response.text.strip()
        return keywords
    except Exception as e:
        print(f"❌ Gemini keyword extraction failed: {e}")
        return query  # fallback

# --- Function to search clause using extracted keywords ---
def search_best_clause(user_query):
    keywords = extract_keywords(user_query)

    def run_search(query_string):
        return es.search(index=INDEX_NAME, body={
            "size": 1,
            "query": {
                "match": {
                    "metadata.text": {
                        "query": query_string,
                        "operator": "OR",
                        "fuzziness": "AUTO"
                    }
                }
            }
        })

    # Try with extracted keywords
    response = run_search(keywords)

    # Fallback to original query if no result
    if not response["hits"]["hits"]:
        response = run_search(user_query)

    if not response["hits"]["hits"]:
        return {
            "score": 0.0,
            "text": "❌ No relevant clause found.",
            "source_doc": None,
            "clause_id": None,
            "metadata": {}
        }

    hit = response["hits"]["hits"][0]
    return {
        "score": hit["_score"],
        "text": hit["_source"]["metadata"]["text"],
        "source_doc": hit["_source"].get("source_doc"),
        "clause_id": hit["_source"].get("clause_id"),
        "metadata": hit["_source"].get("metadata", {})
    }

# --- Final importable function ---
def elasticSearchByQuery(user_query):
    return search_best_clause(user_query)

##### TESTING ONLY #####
if __name__ == "__main__":
    user_query = input("🧠 Enter your query: ")
    result = elasticSearchByQuery(user_query)
    print(result)
