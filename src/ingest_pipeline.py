import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from src.ingestion.source_code_loader import QemuSourceLoader
from src.ingestion.docs_loader import QemuDocsLoader
from src.ingestion.boot_docs_loader import BootDocsLoader
from src.ingestion.wiki_loader import QemuWikiLoader
from src.ingestion.so_loader import StackOverflowLoader
from src.ingestion.mailing_list_loader import MailingListLoader
import logging

# Configure logging to write to a file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

PERSIST_DIRECTORY = "data/chroma_db"


def get_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    return Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)

def process_and_add(docs, collection_name="default"):
    if not docs:
        logging.info(f"No documents to add for {collection_name}")
        return
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    logging.info(f"Adding {len(chunks)} chunks from {collection_name} to Vector DB...")
    
    db = get_vector_db()
    # Batch add to avoid memory issues if large
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        db.add_documents(batch)
        logging.info(f"Added batch {i//batch_size + 1}/{len(chunks)//batch_size + 1}")
    db.persist()

def ingest_incremental():
    """Only scrapes dynamic sources: StackOverflow and Mailing List"""
    logging.info("Starting Incremental Ingestion...")
    
    # Load StackOverflow
    logging.info("Loading StackOverflow (QEMU tag)...")
    # max_pages=1 for incremental frequent updates, or more for initial
    so_loader = StackOverflowLoader(max_pages=2) 
    so_pages = so_loader.load()
    process_and_add(so_pages, "StackOverflow")

    # Load Mailing List
    logging.info("Loading Mailing List Archives...")
    ml_loader = MailingListLoader(limit=10)
    ml_pages = ml_loader.load()
    process_and_add(ml_pages, "MailingList")
    
    logging.info("Incremental Ingestion Complete.")

def ingest_data():
    logging.info("Starting Full Ingestion...")
    
    # 1. Load Source Code
    logging.info("Loading Source Code...")
    source_loader = QemuSourceLoader("data/source_code/qemu")
    source_docs = source_loader.load()
    
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.C, chunk_size=2000, chunk_overlap=200
    )
    source_chunks = code_splitter.split_documents(source_docs)
    logging.info(f"Source Code split into {len(source_chunks)} chunks.")
    
    # Add to DB
    db = get_vector_db()
    db.add_documents(source_chunks)
    db.persist()
    
    # 2. Load Docs
    logging.info("Loading Official Docs...")
    docs_loader = QemuDocsLoader()
    doc_pages = docs_loader.load()
    process_and_add(doc_pages, "OfficialDocs")
    
    # 3. Load Boot Docs
    logging.info("Loading Boot Docs...")
    boot_loader = BootDocsLoader()
    boot_pages = boot_loader.load()
    process_and_add(boot_pages, "BootDocs")
    
    # 4. Load Wiki
    logging.info("Loading Wiki...")
    wiki_loader = QemuWikiLoader()
    wiki_pages = wiki_loader.load()
    process_and_add(wiki_pages, "Wiki")

    # 5. Dynamic Sources (Initial load)
    # We reuse the incremental logic but maybe with more depth if needed
    # For now just call it
    ingest_incremental()
    
    logging.info(f"Full Ingestion Complete. DB saved to {PERSIST_DIRECTORY}")

def ingest_full():
    """Deep ingestion: Source, Docs, Wiki, Deep SO, Deep ML"""
    logging.info("Starting FULL DEEP Ingestion. This will take a while...")
    
    # 1. Official Docs
    logging.info("Loading Official Docs...")
    docs_loader = QemuDocsLoader()
    doc_pages = docs_loader.load()
    process_and_add(doc_pages, "OfficialDocs")

    # 2. Wiki
    logging.info("Loading QEMU Wiki...")
    wiki_loader = QemuWikiLoader()
    wiki_pages = wiki_loader.load()
    process_and_add(wiki_pages, "Wiki")

    # 3. Deep StackOverflow (50 pages ~ 750 questions)
    logging.info("Deep Scraping StackOverflow (50 pages)...")
    so_loader = StackOverflowLoader(max_pages=50, sort="votes") # Get highest voted of all time
    so_pages = so_loader.load()
    process_and_add(so_pages, "StackOverflow_Deep")

    # 4. Deep Mailing List
    logging.info("Deep Scraping Mailing List (100 threads)...")
    ml_loader = MailingListLoader(limit=100)
    ml_pages = ml_loader.load()
    process_and_add(ml_pages, "MailingList_Deep")

    # 5. Source Code (If not already there, but we add it again to be safe or update)
    # Be careful with duplicates if not using an id-check. Chroma handles exact duplicates by ID if we generated them deterministically
    # But here we rely on content-based deduplication or just overwriting? 
    # Chroma standard add_documents might duplicate if IDs are null.
    # For this task, we accept some duplication risk for safety, or clear DB? 
    # Let's assume user wants to ADD to knowledge.
    
    logging.info("Full Ingestion Complete.")

    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--incremental":
            ingest_incremental()
        elif sys.argv[1] == "--full":
            ingest_full()
        else:
            ingest_data()
    else:
        ingest_data()
