from app.services.embedder import get_embedding
from app.utils.pinecone_client import index
import google.generativeai as genai
from app.services.elasticSearch.elasticQuerySearch import elasticSearchByQuery
from typing import List, Dict, Any
import logging

# Initialize model once at module level to avoid repeated initialization
MODEL = genai.GenerativeModel("gemini-2.0-flash-exp")

def query_documents(user_query: str, top_k: int = 5, similarity_threshold: float = 0.7) -> str:
    """
    Efficiently query documents using RAG with optimizations for performance.
    
    Args:
        user_query: The user's question
        top_k: Number of top matches to retrieve
        similarity_threshold: Minimum similarity score to include results
    
    Returns:
        Generated response based on retrieved context
    """
    try:
        # Step 1: Get embedding of the user query (cached if possible)
        query_vector = get_embedding(user_query)

        # Step 2: Query Pinecone with optimized parameters
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            include_values=False  # Don't return vectors to save bandwidth
        )

        # Step 3: Filter and extract high-quality matches
        high_quality_matches = []
        for match in response.get('matches', []):
            # Filter by similarity threshold
            if match.get('score', 0) >= similarity_threshold:
                text = match.get('metadata', {}).get('text', '').strip()
                if text:  # Only include non-empty text
                    high_quality_matches.append(text)

        # Early return if no good matches found
        # if not high_quality_matches:
        #     return "I couldn't find relevant information to answer your question. Please try rephrasing or asking about a different topic."

        # Step 4: Optimize context preparation
        # Limit total context length to prevent token overflow
        max_context_length = 3000  # Adjust based on your model's context window
        context_parts = []
        current_length = 0
        
        for text in high_quality_matches:
            if current_length + len(text) > max_context_length:
                break
            context_parts.append(text)
            current_length += len(text)
        
        context = "\n\n".join(context_parts)  # Double newline for better separation
        elasticData = elasticSearchByQuery(user_query)
        
        # print(f"vector : {context}")
        print(f"elastic : {elasticData}")

        # Print/log the context being used
        print("=" * 50)
        print("CONTEXT USED FOR RESPONSE:")
        print("=" * 50)
        print(context)
        print("=" * 50)

        # Step 5: Optimized prompt with clear instructions
        prompt = f"""Based on the following context, provide a concise and accurate answer.

            Context:
            context from vector search:
            {context}
            
            context from elastic search:
            {elasticData}

            Question: {user_query}

            Instructions:
            - Answer in 2-3 sentences maximum
            - If the answer can be Yes/No, start with that
            - If the context doesn't contain the answer, say "The provided information doesn't contain an answer to this question"
            - Be specific and factual

            Answer:"""

        # Step 6: Generate response with optimized parameters
        response = MODEL.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more focused responses
                max_output_tokens=150,  # Limit response length
                top_p=0.8,
                top_k=40
            )
        )

        final_response = response.text.strip()
        
        # Print/log the generated response
        print("GENERATED RESPONSE:")
        print("-" * 30)
        print(final_response)
        print("=" * 50)
        
        return final_response

    except Exception as e:
        logging.error(f"Error in query_documents: {str(e)}")
        return "I encountered an error while processing your question. Please try again."


def query_documents_batch(queries: List[str], top_k: int = 5) -> List[str]:
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
            result = query_documents(query, top_k)
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