import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import time
import random

class StackOverflowLoader:
    def __init__(self, tag="qemu", sort="votes", max_pages=1):
        self.base_url = "https://stackoverflow.com"
        self.tag = tag
        self.sort = sort
        self.max_pages = max_pages
        # Rotate User-Agents to be polite and avoid immediate blocking
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
        ]

    def _get_soup(self, url):
        headers = {"User-Agent": random.choice(self.user_agents)}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            elif response.status_code == 429:
                print("Rate limited by StackOverflow. Waiting...")
                time.sleep(60) # Wait a minute
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        return None

    def load(self):
        print(f"Scraping StackOverflow for tag '[{self.tag}]'...")
        docs = []
        
        for i in range(1, self.max_pages + 1):
            list_url = f"{self.base_url}/questions/tagged/{self.tag}?tab={self.sort}&page={i}&pagesize=15"
            soup = self._get_soup(list_url)
            if not soup:
                continue

            questions = soup.select(".s-post-summary")
            print(f"Found {len(questions)} questions on page {i}")

            for q in questions:
                title_elem = q.select_one(".s-post-summary--content-title a")
                if not title_elem:
                    continue
                
                link = self.base_url + title_elem['href']
                title = title_elem.get_text(strip=True)
                
                # Fetch question detail
                # Be polite with rate limits
                time.sleep(random.uniform(1.0, 3.0))
                
                q_soup = self._get_soup(link)
                if not q_soup:
                    continue

                # Get Main Question Text
                question_body = q_soup.select_one(".js-post-body")
                q_text = question_body.get_text(strip=True) if question_body else ""

                # Get Answers (Checked or highly voted)
                answers = []
                for ans in q_soup.select(".answer"):
                    # Check if accepted
                    is_accepted = "js-accepted-answer" in ans.get("class", [])
                    score_elem = ans.select_one(".js-vote-count")
                    score = int(score_elem.get_text(strip=True)) if score_elem else 0

                    if is_accepted or score > 0:
                        ans_body = ans.select_one(".js-post-body")
                        if ans_body:
                            answers.append(f"[Score: {score}, Accepted: {is_accepted}]\n{ans_body.get_text(strip=True)}")

                if answers:
                    full_content = f"Question: {title}\n\n{q_text}\n\nAnswers:\n" + "\n---\n".join(answers)
                    
                    metadata = {
                        "source": "stackoverflow",
                        "title": title,
                        "url": link,
                        "tag": self.tag
                    }
                    
                    docs.append(Document(page_content=full_content, metadata=metadata))
        
        print(f"Loaded {len(docs)} StackOverflow threads.")
        return docs

if __name__ == "__main__":
    loader = StackOverflowLoader(max_pages=1)
    docs = loader.load()
    for d in docs[:2]:
        print(d.metadata['title'])
        print(d.page_content[:200])
        print("---")
