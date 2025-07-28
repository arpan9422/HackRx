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
INDEX_NAME = os.getenv("INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configure Gemini ---
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

# --- Extract keywords from a sentence using Gemini ---
# def extract_keywords(query):
#     prompt = f"""
#     Extract the top 5 most important keywords or key phrases from the following query, comma separated only (no numbering or bullets):

#     "{query}"
#     """

#     try:
#         response = model.generate_content(prompt)
#         keywords = response.text.strip()
#         return keywords
#     except Exception as e:
#         print(f"❌ Gemini keyword extraction failed: {e}")
#         return query  # fallback to original query if Gemini fails

# --- Extract keywords from a sentence using KeyBERT ---
def extract_keywords(query: str, top_n: int = 5) -> str:
    keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=top_n)
    # Remove single/double quotes from each keyword
    cleaned_keywords = [kw.replace('"', '').replace("'", "") for kw, _ in keywords]
    return ", ".join(cleaned_keywords)



# --- Extract keywords from a sentence using Spacy ---
# def extract_keywords(query: str, top_n: int = 5) -> str:
#     doc = nlp(query)

#     # Use noun chunks + named entities as keywords
#     keywords = set()

#     # Noun chunks like "insurance policy", "waiting period"
#     for chunk in doc.noun_chunks:
#         keywords.add(chunk.text.lower())

#     # Named entities like "ICICI", "Diabetes", "April 2023"
#     for ent in doc.ents:
#         keywords.add(ent.text.lower())

#     # Limit to top N keywords
#     keywords = list(keywords)[:top_n]

#     return ", ".join(keywords)

# --- Function to get top match from ElasticSearch using extracted keywords ---
def search_best_clause(user_query):
    keywords = extract_keywords(user_query)
    # print(f"🔍 Extracted keywords: {keywords}")

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

    # First try with extracted keywords
    response = run_search(keywords)

    # Fallback to full query if needed
    if not response["hits"]["hits"]:
        # print("⚠️ No match with keywords. Trying full query...")
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
    # print(hit["_source"].get("metadata", {}))
    return {
        "score": hit["_score"],
        "text": hit["_source"]["metadata"]["text"],  # since actual text is here
        "source_doc": hit["_source"].get("source_doc"),
        "clause_id": hit["_source"].get("clause_id"),
        "metadata": hit["_source"].get("metadata", {})
    }

# --- Final function to import ---
def elasticSearchByQuery(user_query):
    return search_best_clause(user_query)

##### TESTING ONLY #####
if __name__ == "__main__":
    user_query = input("🧠 Enter your query: ")
    result = elasticSearchByQuery(user_query)

