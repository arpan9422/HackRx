from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, source_name="document.pdf") -> list[str]:
    """
    Smartly chunks a large body of text into overlapping segments,
    maintaining semantic integrity without nltk.
    """
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Clean leading/trailing whitespace
    text = text.strip()

    # Use RecursiveCharacterTextSplitter with prioritized separators
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,         # You can tweak based on model limits
        chunk_overlap=200,      # More overlap = better context
        separators=[
            "\n\n",             # Paragraph
            "\n",               # Line break
            ". ",               # Sentence end
            " ",                # Word
            ""                  # Char-level fallback
        ]
    )

    chunks = splitter.split_text(text)

    # Add metadata like source and chunk index
    enhanced_chunks = [
        f"(Source: {source_name}, Chunk {i+1})\n\n{chunk.strip()}"
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]

    return enhanced_chunks