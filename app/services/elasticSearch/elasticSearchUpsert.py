import os
import uuid
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# --- Load env vars ---
load_dotenv()
ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# --- Dynamic source doc (can also be passed via CLI) ---
SOURCE_DOC = "DummyPolicy.pdf"

# --- Connect to Elastic ---
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    api_key=ELASTIC_API_KEY,
    verify_certs=True
)

# --- Dummy chunks to insert ---
text_chunks = [
    {
        "text": "Clause 1: Coverage begins after 30 days of continuous enrollment.",
        "metadata": {"waiting_period": "30 days", "category": "General", "coverage_limit": None, "age_limit": None}
    },
    {
        "text": "Clause 2: Hospitalization due to accidents is covered from day one.",
        "metadata": {"waiting_period": "0 days", "category": "Emergency", "coverage_limit": None, "age_limit": None}
    },
    {
        "text": "Clause 3: Pre-existing conditions are not covered for the first 12 months.",
        "metadata": {"waiting_period": "12 months", "category": "Pre-existing", "coverage_limit": None, "age_limit": None}
    },
    {
        "text": "Clause 4: Daycare procedures are covered without any waiting period.",
        "metadata": {"waiting_period": "0 days", "category": "Daycare", "coverage_limit": None, "age_limit": None}
    },
    {
        "text": "Clause 5: Maternity benefits are applicable after a waiting period of 9 months.",
        "metadata": {"waiting_period": "9 months", "category": "Maternity", "coverage_limit": "50,000", "age_limit": None}
    },
    {
        "text": "Clause 6: OPD consultation charges are not reimbursed under this policy.",
        "metadata": {"waiting_period": None, "category": "Exclusion", "coverage_limit": None, "age_limit": None}
    },
    {
        "text": "Clause 7: Room rent is covered up to INR 5,000 per day.",
        "metadata": {"waiting_period": None, "category": "Hospitalization", "coverage_limit": "5000/day", "age_limit": None}
    },
    {
        "text": "Clause 8: ICU charges are reimbursed up to actuals within sum insured.",
        "metadata": {"waiting_period": None, "category": "Hospitalization", "coverage_limit": "Actuals", "age_limit": None}
    },
    {
        "text": "Clause 9: Organ donor expenses are covered under the basic sum insured.",
        "metadata": {"waiting_period": None, "category": "Transplant", "coverage_limit": "Within Sum Insured", "age_limit": None}
    },
    {
        "text": "Clause 10: Knee and hip replacement surgeries are covered after 3 months.",
        "metadata": {"waiting_period": "3 months", "category": "Orthopedic", "coverage_limit": None, "age_limit": None}
    },
    # ... add more clauses like this ...
]


# --- Create index if it doesn't exist ---
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "clause_id": {"type": "keyword"},
                    "text": {"type": "text"},
                    "source_doc": {"type": "keyword"},
                    "metadata": {"type": "object"}
                }
            }
        }
    )

# --- Delete old chunks for this source_doc ---
def delete_existing_chunks(source_doc):
    query = {
        "query": {
            "term": {
                "source_doc": source_doc
            }
        }
    }
    es.delete_by_query(index=INDEX_NAME, body=query)
    print(f"🗑️ Deleted old clauses for '{source_doc}'")

# --- Index new chunks ---
def index_chunks(chunks):
    for i, chunk in enumerate(chunks):
        doc = {
                
                "metadata": chunk["metadata"]
        }
        es.index(index=INDEX_NAME, document=doc)
        print(f"✅ Indexed clause {i+1}'")
        
def Upsert(text_chunks):
    index_chunks(text_chunks)
    return "All the clauses upserted successfully"

# --- Main ---
if __name__ == "__main__":
    delete_existing_chunks(SOURCE_DOC)
    print("🚀 Done deleting old clauses.")
