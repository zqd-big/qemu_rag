@echo off
echo Starting QEMU RAG System...
cd /d "%~dp0"
& "C:\Program Files\Python310\python.exe" -m streamlit run src/ui/app.py
pause
