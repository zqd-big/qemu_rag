import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "data/chroma_db"

def inspect():
    if not os.path.exists(PERSIST_DIRECTORY):
        print("Database not found!")
        return

    print("Loading Vector DB...")
    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
    
    # Get all documents (or a sample)
    print("\n--- Inspecting Stored Documents ---\n")
    # Count via collection get
    count = db._collection.count()
    print(f"Total Documents in DB: {count}")
    
    results = db.similarity_search("error", k=3)
    
    for i, doc in enumerate(results):
        print(f"Document {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Title: {doc.metadata.get('title', 'N/A')}")
        print(f"URL: {doc.metadata.get('url', 'N/A')}")
        print("-" * 20)
        print(doc.page_content[:500] + "...") # Preview content
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    inspect()
