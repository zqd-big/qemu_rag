# QEMU Real-time Issue Crawler & RAG System

This project is a comprehensive system designed to crawl, index, and retrieve QEMU-related knowledge from the entire network, including StackOverflow, Official Docs, Wiki, Mailing Lists, and Source Code.

## 📂 Project Structure
- `src/`: Python source code for crawlers (loaders), RAG engine, and UI.
- `QEMU_知识库_导出/`: **[Important]** Pre-crawled knowledge base text files (StackOverflow, Docs, Wiki) ready for import into AnythingLLM or other RAG tools.
- `data/chroma_db/`: Local vector database (ChromaDB) storing the embedded knowledge.
- `*.bat`: Windows batch scripts for easy execution.

## 🚀 How to Run

### 1. Web Interface (GUI)
Double-click `start_app.bat` to launch the Streamlit web interface in your browser.
You can query the knowledge base purely for debugging QEMU issues.

### 2. Command Line (CLI)
Query the knowledge base quickly via terminal:
```powershell
& "C:\Program Files\Python310\python.exe" src/ask_qemu.py "Your question here"
```

### 3. Background Scraper
Double-click `start_scheduler.bat` to keep the scraper running in the background. It will fetch new StackOverflow questions every hour.

## 🧠 Knowledge Export (For AnythingLLM)
If you wish to use this data with **AnythingLLM** and local models (Ollama/Huawei):
1.  Open the folder `QEMU_知识库_导出`.
2.  Drag the `.txt` files into your AnythingLLM workspace.
3.  Let AnythingLLM re-embed the data using your local model.

## 🛠️ Advanced: Re-building the Database
To manually trigger a full crawl (Warning: takes ~30-60 mins):
```powershell
run_ingestion.bat --full
```
To run an incremental update (fast):
```powershell
run_ingestion.bat --incremental
```

## Dependencies
- Python 3.10+
- `pip install -r requirements.txt`
