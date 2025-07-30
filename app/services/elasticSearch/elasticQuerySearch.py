import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import google.generativeai as genai
from keybert import KeyBERT
import spacy

# --- Load environment variables ---
load_dotenv()

ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configure models ---
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Connect to Elasticsearch ---
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    api_key=ELASTIC_API_KEY,
    verify_certs=True
)

# --- Extract keywords from query using KeyBERT ---
def extract_keywords(query: str, top_n: int = 5) -> str:
    keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=top_n)
    cleaned_keywords = [kw.replace('"', '').replace("'", "") for kw, _ in keywords]
    return ", ".join(cleaned_keywords)


# --- Search top matching clause from Elasticsearch ---
def search_best_clause(user_query: str, index_name: str) -> dict:
    keywords = extract_keywords(user_query)

    def run_search(query_string):
        return es.search(index=index_name, body={
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

    # Try keyword-based query first
    response = run_search(keywords)

    # Fallback to raw user query if nothing found
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
        "text": hit["_source"]["metadata"]["text"],  # assuming actual text stored here
        "source_doc": hit["_source"].get("source_doc"),
        "clause_id": hit["_source"].get("clause_id"),
        "metadata": hit["_source"].get("metadata", {})
    }

# --- Public-facing function with index support ---
def elasticSearchByQuery(user_query: str, index_name: str) -> dict:
    return search_best_clause(user_query, index_name)

# --- Local test only ---
if __name__ == "__main__":
    query = input("🧠 Enter your query: ")
    namespace_index = input("📂 Enter the index name (namespace): ")
    result = elasticSearchByQuery(query, namespace_index)
    print(result)
