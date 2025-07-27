from langchain.vectorstores import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# Embedder
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Pinecone setup
vectorstore = Pinecone.from_existing_index("your-index", embedding)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Chat model (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Retrieval QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

query = "Summarize clause 4 of the agreement"
result = qa_chain.run(query)
print(result)
