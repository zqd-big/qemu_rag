import os
import glob
from langchain_core.documents import Document

class QemuSourceLoader:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def load(self):
        docs = []
        # Walk through the repository
        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')  # don't visit .git directories
            
            for file in files:
                if file.endswith(('.c', '.h')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Basic content document
                        # We might want to split this differently later, but for now getting the raw code is step 1.
                        # Ideally we want to extract "functions" or "error blocks"
                        
                        # Optimization: Tag if it contains error reporting functions
                        has_error = any(x in content for x in ['error_report(', 'qemu_log(', 'warn_report(', 'error_setg('])
                        
                        metadata = {
                            "source": "source_code",
                            "file_path": rel_path,
                            "file_type": "c_source" if file.endswith('.c') else "header",
                            "has_error_reporting": has_error
                        }
                        
                        docs.append(Document(page_content=content, metadata=metadata))
                        
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        print(f"Loaded {len(docs)} source files.")
        return docs

if __name__ == "__main__":
    # Test run
    loader = QemuSourceLoader("data/source_code/qemu")
    # docs = loader.load() # Commented out to prevent auto-execution slowing down
