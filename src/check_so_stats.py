import requests
from bs4 import BeautifulSoup
import re

def check_so_stats():
    # Sort by votes to match our ingestion, but we want to see total count
    url = "https://stackoverflow.com/questions/tagged/qemu?tab=votes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Checking {url}...")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for total count usually in "X questions"
        # The selector often is ".fs-body3" or similar near the top
        count_div = soup.select_one(".fs-body3")
        if count_div:
            text = count_div.get_text(strip=True)
            print(f"Raw count text: {text}")
            # Extract number
            match = re.search(r'([\d,]+)', text)
            if match:
                total_questions = int(match.group(1).replace(",", ""))
                print(f"Total Questions: {total_questions}")
                print(f"Total Pages (at 15 per page): {total_questions // 15}")
                print(f"Total Pages (at 50 per page): {total_questions // 50}")
            else:
                print("Could not parse number from text.")
        else:
            print("Could not find count element.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_so_stats()
