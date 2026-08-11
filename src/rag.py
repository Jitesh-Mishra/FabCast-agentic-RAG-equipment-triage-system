import os
import glob
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "data/chroma_store"
COLLECTION = "fabcast_docs"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def _build():
    raw_docs = []
    for path in sorted(glob.glob("docs/*.md")):
        with open(path, "r") as f:
            content = f.read()
        raw_docs.append(Document(page_content=content, metadata={"source": path.split("/")[-1]}))
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(raw_docs)
    print(f"Building vector store: {len(raw_docs)} docs -> {len(chunks)} chunks")
    return Chroma.from_documents(chunks, embeddings, persist_directory=PERSIST_DIR, collection_name=COLLECTION)


# Load the existing store if it's already been built; only rebuild if missing.
if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
    vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings, collection_name=COLLECTION)
else:
    vectordb = _build()


def retrieve(query: str, k: int = 3):
    """Retrieve the k most relevant doc chunks for a query. Used by the Diagnosis Agent."""
    return vectordb.similarity_search(query, k=k)
