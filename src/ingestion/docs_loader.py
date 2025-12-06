from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup
import re

class QemuDocsLoader:
    def __init__(self, url="https://www.qemu.org/docs/master/"):
        self.url = url

    def load(self):
        print(f"Scraping QEMU Docs from {self.url}...")
        loader = RecursiveUrlLoader(
            url=self.url,
            max_depth=4,
            extractor=lambda x: Soup(x, "html.parser").text,
            prevent_outside=True,
            use_async=True,
            timeout=10,
            check_response_status=True
        )
        docs = loader.load()
        
        # Post-processing to clean up metadata and content
        cleaned_docs = []
        for doc in docs:
            # Simple Text cleaning
            content = re.sub(r'\n\s*\n', '\n\n', doc.page_content)
            doc.page_content = content
            doc.metadata["source"] = "official_docs"
            cleaned_docs.append(doc)
            
        print(f"Loaded {len(cleaned_docs)} documentation pages.")
        return cleaned_docs

if __name__ == "__main__":
    loader = QemuDocsLoader()
    # docs = loader.load()
