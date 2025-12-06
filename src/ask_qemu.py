import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from src.rag.engine import QemuRAG

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/ask_qemu.py \"Your question here\"")
        return

    query = sys.argv[1]
    print(f"\nQuestion: {query}\n")
    
    try:
        print("Initializing RAG Engine...")
        engine = QemuRAG()
        
        print("Searching Knowledge Base...")
        answer = engine.ask(query)
        
        print("\n--- Answer ---\n")
        print(answer)
        print("\n--------------\n")
        
        # Also show sources
        print("Sources Used:")
        docs = engine.retrieve_context(query)
        for i, doc in enumerate(docs):
            src = doc.metadata.get('source', 'Unknown')
            url = doc.metadata.get('url', 'N/A') 
            print(f"{i+1}. [{src}] {url}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure OPENAI_API_KEY is set in your environment if using OpenAI.")

if __name__ == "__main__":
    main()
