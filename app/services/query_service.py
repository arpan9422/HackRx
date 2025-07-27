from app.services.embedder import get_embedding
from app.utils.pinecone_client import index
from app.services.logic import enhance_query
import google.generativeai as genai
from app.services.elasticSearch.elasticQuerySearch import elasticSearchByQuery
from typing import List, Dict, Any
import logging

# Initialize model once at module level to avoid repeated initialization
MODEL = genai.GenerativeModel("gemini-2.0-flash")

async def query_documents(user_query: str, top_k: int = 5, similarity_threshold: float = 0.7) -> str:
    """
    Efficiently query documents using RAG with optimizations for performance.
    """
    try:
        async def _run_query(query: str) -> str:
            # Step 1: Get embedding of the query
            query_vector = get_embedding(query)

            # Step 2: Query Pinecone
            response = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )

            # Step 3: Filter matches
            high_quality_matches = [
                match.get('metadata', {}).get('text', '').strip()
                for match in response.get('matches', [])
                if match.get('score', 0) >= similarity_threshold
            ]
            high_quality_matches = [text for text in high_quality_matches if text]

            # Step 4: Prepare context
            max_context_length = 3000
            context_parts, current_length = [], 0

            for text in high_quality_matches:
                if current_length + len(text) > max_context_length:
                    break
                context_parts.append(text)
                current_length += len(text)

            context = "\n\n".join(context_parts)
            elasticData = elasticSearchByQuery(query)
            # print(context)
            # Step 5: Prompt
            prompt = f"""Based on the following context, provide a concise and accurate answer.

            Context:
            context from vector search:
            {context}

            context from elastic search:
            {elasticData}

            Question: {query}

            Instructions:
            - Answer in 2-3 sentences maximum
            - If the answer can be Yes/No, start with that
            - If the context doesn't contain the answer, say "The provided information doesn't contain an answer to this question"
            - Be specific and factual

            Answer: """

            # Step 6: Generate response
            response = MODEL.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=150,
                    top_p=0.8,
                    top_k=40
                )
            )

            return response.text.strip()

        # First attempt
        response_text = await _run_query(user_query)

        if "provided information doesn't contain an answer" in response_text.lower():
            print("⚠️ No answer found — retrying with enhanced query...")
            enhanced_query = await enhance_query(user_query)
            response_text = await _run_query(enhanced_query)

        print("GENERATED RESPONSE:")
        print("-" * 30)
        print(response_text)
        print("=" * 50)

        return response_text

    except Exception as e:
        logging.error(f"Error in query_documents: {str(e)}")
        print(f"Error in query_documents: {str(e)}")
        return "I encountered an error while processing your question. Please try again."


async def query_documents_batch(queries: List[str], top_k: int = 5) -> List[str]:
    """
    Process multiple queries efficiently in batch.
    
    Args:
        queries: List of user queries
        top_k: Number of top matches per query
    
    Returns:
        List of responses corresponding to each query
    """
    results = []
    
    # Get all embeddings at once if your embedder supports batch processing
    try:
        for query in queries:
            result =await query_documents(query, top_k)
            results.append(result)
    except Exception as e:
        logging.error(f"Batch processing error: {str(e)}")
        results = ["Error processing query" for _ in queries]
    
    return results


# Optional: Add caching decorator for frequently asked questions
from functools import lru_cache

@lru_cache(maxsize=100)
def query_documents_cached(user_query: str, top_k: int = 5) -> str:
    """
    Cached version of query_documents for frequently asked questions.
    Use this for queries that are likely to be repeated.
    """
    return query_documents(user_query, top_k)