import sys
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai.chat_models.base import ChatOpenAI
from langchain.chains import RetrievalQA
from .config import OPENAI_API_KEY, INDEX_DIR

def get_qa_chain(k: int = 3, temperature: float = 0.0) -> RetrievalQA:
    """
    RetrievalQA チェーンを構築して返す
    k: 上位何件を検索するか
    temperature: 生成モデルの温度パラメータ
    """
    openai.api_key = OPENAI_API_KEY

    embeddings = OpenAIEmbeddings()

    # allow_dangerous_deserialization=True を設定してローカルインデックスを安全にロード
    vectorstore = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4.1-mini", temperature=temperature),
        chain_type="stuff",
        retriever=retriever
    )
    return qa_chain

def answer_query(query: str) -> str:
    """
    単発クエリを受け取って回答を返す
    """
    chain = get_qa_chain()
    response = chain.invoke({"query": query})
    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.qa_chain '<your question>'")
        sys.exit(1)

    question = sys.argv[1]
    print(answer_query(question))

