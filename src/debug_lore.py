import requests
from bs4 import BeautifulSoup

def debug_lore():
    url = "https://lore.kernel.org/qemu-devel/"
    print(f"Fetching {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Check standard lore structure (usually tables)
        rows = soup.find_all("tr")
        print(f"Total <tr> tags: {len(rows)}")
        
        # Check for subject links
        # Lore usually has subject in <td class="s"><a href="...">Subject</a></td>
        links = soup.select("td.s a")
        print(f"Links found with 'td.s a': {len(links)}")
        
        if len(links) == 0:
            print("No links with td.s a. Printing first 5 'a' tags:")
            all_links = soup.find_all("a")
            for a in all_links[:5]:
                print(f"  {a}")
                
        else:
            print("Links found! First 3:")
            for l in links[:3]:
                print(f"  Href: {l.get('href')} | Text: {l.get_text(strip=True)[:50]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_lore()
