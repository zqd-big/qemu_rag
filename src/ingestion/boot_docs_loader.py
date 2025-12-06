from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup
import re

class BootDocsLoader:
    def __init__(self):
        self.sources = [
            # U-Boot Documentation
            "https://u-boot.readthedocs.io/en/latest/",
            # SeaBIOS
            "https://www.seabios.org/",
            # QEMU Firmware docs
            "https://www.qemu.org/docs/master/system/firmware.html"
        ]

    def load(self):
        all_docs = []
        for url in self.sources:
            print(f"Scraping Boot Docs from {url}...")
            # Customize max_depth based on source complexity
            depth = 3 if "readthedocs" in url else 2
            
            loader = RecursiveUrlLoader(
                url=url,
                max_depth=depth,
                extractor=lambda x: Soup(x, "html.parser").text,
                prevent_outside=True,
                use_async=True,
                timeout=10,
                check_response_status=True
            )
            try:
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = "boot_knowledge"
                    doc.metadata["original_url"] = url
                    # Simple cleanup
                    doc.page_content = re.sub(r'\n\s*\n', '\n\n', doc.page_content)
                    
                all_docs.extend(docs)
                print(f"Loaded {len(docs)} pages from {url}.")
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                
        return all_docs

if __name__ == "__main__":
    loader = BootDocsLoader()
    # docs = loader.load()
