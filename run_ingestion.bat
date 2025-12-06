@echo off
echo Starting Data Ingestion (This may take a while)...
cd /d "%~dp0"
"C:\Program Files\Python310\python.exe" -m src.ingest_pipeline
pause
