import streamlit as st
import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from src.rag.engine import QemuRAG

st.set_page_config(page_title="QEMU Debugger RAG", layout="wide")

st.title("QEMU Simulation Debugging Assistant")
st.markdown("Retrieving knowledge from Source Code, Docs, Wiki, and Bootloader specs.")

# Initialize RAG engine
@st.cache_resource
def get_engine():
    try:
        return QemuRAG()
    except Exception as e:
        st.error(f"Failed to initialize RAG: {e}")
        return None

engine = get_engine()

query = st.text_input("Describe your QEMU error or problem:")

if query:
    if engine:
        with st.spinner("Searching knowledge base..."):
            # 1. Retrieve Context
            docs = engine.retrieve_context(query)
            
            # Show Context in Expander
            with st.expander("Retrieved Context (Source Code & Docs)"):
                for i, doc in enumerate(docs):
                    source = doc.metadata.get("source", "unknown")
                    path = doc.metadata.get("file_path", doc.metadata.get("original_url", ""))
                    st.markdown(f"**[{i+1}] Source:** `{source}` - `{path}`")
                    st.code(doc.page_content[:500] + "...", language="c" if "source_code" in source else "text")
            
            # 2. Generate Answer
            st.subheader("Solution")
            try:
                answer = engine.ask(query)
                st.markdown(answer)
            except Exception as e:
                st.error(f"Generation failed (Likely missing API Key): {e}")
    else:
        st.error("RAG Engine not ready. Did you run the ingestion pipeline?")

st.sidebar.markdown("### Status")
if os.path.exists("data/chroma_db"):
    st.sidebar.success("Vector DB Found")
else:
    st.sidebar.warning("Vector DB Not Found - Run Ingestion")
