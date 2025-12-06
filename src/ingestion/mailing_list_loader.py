import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import time
import random

class MailingListLoader:
    def __init__(self, limit=20):
        self.base_url = "https://lore.kernel.org/qemu-devel/"
        self.limit = limit # How many recent threads to check
        self.user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]

    def _get_soup(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        try:
            time.sleep(1) # Be polite but persistent
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                print(f"Failed to fetch {url}: Status {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        return None

    def load(self):
        print(f"Scraping QEMU Mailing List ({self.base_url})...")
        docs = []
        
        # The main page usually lists threads
        soup = self._get_soup(self.base_url)
        if not soup:
            return []

        # lore.kernel.org uses slightly different structures, often <table> rows
        # We look for links to threads
        # This is a basic parser for the index page
        rows = soup.select("pre") 
        # Actually lore uses a mix. Let's look for valid thread links.
        # A better approach for lore is looking for 'a' tags with hrefs that look like message IDs or threads
        
        
        # Parse links more generously since structure varies
        all_links = soup.find_all("a")
        print(f"Scanning {len(all_links)} links for threads...")
        
        links = []
        for a in all_links:
             href = a.get("href")
             if not href: continue
             
             # Heuristics for direct message/thread links in Lore
             # They oftens start with 'T' (thread) or are long ID hashes
             # e.g. "T/#u", "12345...", etc.
             # We filter out obvious non-thread links
             if href.startswith(("http", "mailto", "/ui", "help", "feed")): 
                 continue
                 
             full_link = self.base_url + href if not href.startswith("http") else href
             
             if full_link not in links:
                 links.append(full_link)
                 if len(links) >= self.limit:
                     break
        
        print(f"Found {len(links)} potential thread links.")

        count = 0
        for link in links:
            try:
                time.sleep(random.uniform(0.5, 1.5))
                t_soup = self._get_soup(link)
                if not t_soup:
                    continue
                
                # Cleanup
                for garbage in t_soup.select(".tnav, .h, .b, .head, .foot"): 
                     garbage.decompose()
                
                page_text = t_soup.get_text(separator="\n", strip=True)
                
                if len(page_text) < 200:
                    continue

                docs.append(Document(
                    page_content=page_text, 
                    metadata={"source": "qemu_mailing_list", "url": link}
                ))
                count += 1
                if count % 10 == 0:
                    print(f"  Scraped {count} threads...")
            except Exception as e:
                print(f"Skipping link {link}: {e}")

        print(f"Loaded {len(docs)} mailing list threads.")
        return docs

if __name__ == "__main__":
    loader = MailingListLoader(limit=5)
    docs = loader.load()
    for d in docs:
        print(f"Source: {d.metadata['url']}")
        print(d.page_content[:200])
        print("---")
