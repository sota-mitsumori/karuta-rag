import openai
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .loader import load_and_split
from .config import OPENAI_API_KEY, INDEX_DIR

def build_index():
    """
    ドキュメントチャンクから埋め込みを生成し、FAISS インデックスを構築して保存する
    """
    openai.api_key = OPENAI_API_KEY

    chunks = load_and_split()

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(INDEX_DIR)
    print(f"[indexer] インデックスを '{INDEX_DIR}' に保存しました。")

if __name__ == "__main__":
    build_index()