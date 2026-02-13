import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import PDF_DIR, CHUNK_SIZE, CHUNK_OVERLAP

def load_and_split():
    """
    PDF を読み込んでチャンクに分割し、チャンクのリストを返す
    """
    docs = []
    for fname in os.listdir(PDF_DIR):
        if not fname.lower().endswith('.pdf'):
            continue
        path = os.path.join(PDF_DIR, fname)
        loader = PyPDFLoader(path)
        docs.extend(loader.load())
   

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(docs)
    return chunks

if __name__ == "__main__":
    chunks = load_and_split()
    print(f"[loader] {len(chunks)} チャンクを読み込みました。")
