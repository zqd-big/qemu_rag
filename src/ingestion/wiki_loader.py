from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup

class QemuWikiLoader:
    def __init__(self, url="https://wiki.qemu.org/Main_Page"):
        self.url = url

    def load(self):
        print(f"Scraping QEMU Wiki from {self.url}...")
        loader = RecursiveUrlLoader(
            url=self.url,
            max_depth=2,
            extractor=lambda x: Soup(x, "html.parser").text,
            prevent_outside=True,
            use_async=True,
            timeout=10,
            check_response_status=True
        )
        try:
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = "qemu_wiki"
        except Exception as e:
            print(f"Error scraping wiki: {e}")
            return []
            
        print(f"Loaded {len(docs)} wiki pages.")
        return docs

if __name__ == "__main__":
    loader = QemuWikiLoader()
    # docs = loader.load()
