import os
import io
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "data/chroma_db"
EXPORT_DIR = "knowledge_export"

def export_data():
    if not os.path.exists(PERSIST_DIRECTORY):
        print("Database not found!")
        return

    print("Loading Vector DB for Export...")
    # diverse retrieval
    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
    
    # Create export dir
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        
    print("Fetching all documents from database...")
    # Chroma 'get' fetches all if no args provided
    collection_data = db._collection.get(include=['documents', 'metadatas'])
    
    total_docs = len(collection_data['ids'])
    print(f"Found {total_docs} documents. Grouping by source...")
    
    # Group by source
    sources = {}
    for i in range(total_docs):
        doc_text = collection_data['documents'][i]
        meta = collection_data['metadatas'][i]
        source_name = meta.get('source', 'unknown')
        
        # Normalize source names
        if 'stackoverflow' in source_name:
            group = 'StackOverflow_QnA'
        elif 'wiki' in source_name:
            group = 'QEMU_Wiki'
        elif 'doc' in source_name:
            group = 'Official_Docs'
        elif 'mail' in source_name:
            group = 'Mailing_List'
        else:
            group = 'Other'
            
        if group not in sources:
            sources[group] = []
        
        # Format the entry for readability in the text file
        # Adding a separator that AnythingLLM might appreciate, but plain text is robust.
        entry = (
            f"=== SOURCE: {meta.get('url', 'N/A')} ===\n"
            f"TITLE: {meta.get('title', 'N/A')}\n"
            f"CONTENT:\n{doc_text}\n"
            f"==================================================\n\n"
        )
        sources[group].append(entry)
        
    print("Writing files...")
    for group, entries in sources.items():
        filename = os.path.join(EXPORT_DIR, f"{group}.txt")
        print(f"  -> Writing {len(entries)} items to {filename}...")
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(entries)
            
    print(f"\nExport Complete! Files are ready in: {os.path.abspath(EXPORT_DIR)}")

if __name__ == "__main__":
    export_data()
