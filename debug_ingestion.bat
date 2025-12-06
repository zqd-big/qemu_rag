@echo off
echo [Batch] Starting Ingestion Process... > ingestion.log
echo [Batch] Installing dependencies... >> ingestion.log
python -m pip install langchain-community chromadb langchain-huggingface sentence-transformers -i http://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn >> ingestion.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [Batch] Dependency installation failed! Check log above. >> ingestion.log
    pause
    exit /b %ERRORLEVEL%
)

echo [Batch] Starting Python script... >> ingestion.log
python src/ingest_pipeline.py >> ingestion.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [Batch] Python script crashed! Check log above. >> ingestion.log
    pause
) else (
    echo [Batch] Ingestion finished successfully. >> ingestion.log
    pause
)
