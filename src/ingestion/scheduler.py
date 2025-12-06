import time
import subprocess
import sys
import os
from datetime import datetime

def run_ingestion():
    print(f"[{datetime.now()}] Starting incremental ingestion...")
    # Call ingest_pipeline.py with --incremental
    # Using the same python interpreter
    try:
        subprocess.run([sys.executable, "-m", "src.ingest_pipeline", "--incremental"], check=True)
        print(f"[{datetime.now()}] Incremental ingestion finished.")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}] Ingestion failed: {e}")

def main():
    interval_minutes = 60 # Run every hour
    print(f"Scheduler started. Will run ingestion every {interval_minutes} minutes.")
    
    # Run once immediately
    run_ingestion()
    
    while True:
        try:
            print(f"Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
            run_ingestion()
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(60) # Wait a bit before retrying

if __name__ == "__main__":
    main()
