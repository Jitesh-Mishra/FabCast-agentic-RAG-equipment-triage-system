with open("src/rag.py") as f:
    content = f.read()

old = '''from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "data/chroma_store"
COLLECTION = "fabcast_docs"

embeddings = OllamaEmbeddings(model="nomic-embed-text")'''

new = '''from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "data/chroma_store"
COLLECTION = "fabcast_docs"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")'''

count = content.count(old)
if count != 1:
    print(f"FAIL: expected 1 match, found {count}")
    raise SystemExit(1)

content = content.replace(old, new)
with open("src/rag.py", "w") as f:
    f.write(content)

print("rag.py patched successfully.")
print("HuggingFaceEmbeddings present:", "HuggingFaceEmbeddings" in content)
print("OllamaEmbeddings gone:", "OllamaEmbeddings" not in content)
