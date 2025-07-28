# Intelligent Document Query System (for HackRx 6.0)

Empowering professionals to instantly query dense documents with AI-driven, context-aware answers.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green?logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-LLM-yellow?logo=google)
![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-4B8BBE?logo=pinecone)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-Search-orange?logo=elasticsearch)

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)


---

## Overview
**Core Problem:** Professionals in insurance, legal, and HR spend excessive time manually searching dense, unstructured documents—a process that is inefficient and error-prone.

**Our Solution:** This system leverages Large Language Models (LLMs) to automate document querying. Users ask questions in plain English and receive instant, context-aware answers sourced directly from their documents.

**Core Technology:** Built around a Retrieval Augmented Generation (RAG) pipeline with a hybrid search strategy for accuracy and reliability.

---

## Key Features
- **Natural Language Understanding:** Query documents in plain English—no technical jargon required.
- **Hybrid Search:** Combines vector search (Pinecone) and keyword search (Elasticsearch) for high-precision retrieval.
- **Factual & Grounded Responses:** Uses Google Gemini to generate answers strictly based on retrieved document context, minimizing hallucinations.
- **Secure & Scalable API:** Asynchronous FastAPI backend with token-based authentication.
- **Modular Architecture:** Clean, maintainable, and extensible codebase.

---

## System Architecture
### Data Ingestion Pipeline
1. **Document Upload** → 2. **Text Chunking** → 3. **Embedding Generation** → 4. **Data Indexing** (Pinecone & Elasticsearch)

### Query Retrieval Pipeline
1. **Receive User Query** → 2. **Hybrid Search** (Vector + Keyword) → 3. **Context Augmentation** → 4. **Answer Synthesis** (Google Gemini)

---

## Tech Stack

| Category    | Technologies                                 |
|-------------|----------------------------------------------|
| Backend     | Python, FastAPI                              |
| AI / ML     | Google Gemini, LangChain                     |
| Database    | Pinecone (Vector DB), Elasticsearch (Search) |
| Libraries   | Uvicorn, Pydantic, python-dotenv, PyPDF      |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- Git



### Installation
```bash
git clone <YOUR_REPOSITORY_URL>
cd <repository-name>
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/Mac:
source venv/bin/activate
pip install -r requirements.txt
```


### Environment Variables
Create a `.env` file in the root directory with the following keys:
```
GOOGLE_API_KEY=<your_google_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
PINECONE_ENVIRONMENT=<your_pinecone_env>
PINECONE_INDEX_NAME=<your_pinecone_index>
HACKRX_SECRET_TOKEN=<your_secret_token>
```

---

## Usage

### Running the Server
```bash
python -m uvicorn app.main:app --reload
```



### API Endpoint
- **Endpoint:** `POST /api/v1/hackrx/run`
- **Description:** Submit questions about a document and receive context-aware answers.
- **Authentication:** Requires Bearer token in the `Authorization` header.



#### Example `curl` Request
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["<document_text_1>", "<document_text_2>"],
    "questions": ["What is the claim process?", "Who is the beneficiary?"]
  }'
```

#### Example Response
```json
{
  "answers": [
    "The claim process is outlined in section 3...",
    "The beneficiary is listed as John Doe."
  ]
}
```



---
## Project Structure
```text
app/
├── core/security.py
├── routes/query_router.py, upload_router.py
├── services/query_service.py
├── config.py
└── main.py
.env
requirements.txt
```


