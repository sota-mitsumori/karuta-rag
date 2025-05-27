import sys
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai.chat_models.base import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


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

    # 「コンテキスト以外は答えない」ようにするためのプロンプト
    system_template = """\
        あなたは競技かるた公式PDFからのみ回答を行うアシスタントです。
        ドキュメントにない情報は知らないものとして「申し訳ありませんが、その情報は見つかりませんでした」と答えてください。
        """
    human_template = """\
        質問:
        {question}

        コンテキスト:
        {context}

        上記のコンテキスト以外の情報は一切使わずに答えてください。
        """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template),
    ])

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4.1-mini", temperature=temperature),
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )
    return qa_chain

def answer_query(query: str) -> str:
    """
    単発クエリを受け取って回答文字列だけを返す
    """
    chain = get_qa_chain()
    # invoke は {'result': '…回答…'} という辞書を返す
    output = chain.invoke({"query": query})
    # 'result' キーの値を取り出して文字列で返す
    if isinstance(output, dict) and "result" in output:
        return output["result"]
    # 万が一他の形式なら文字列化
    return str(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.qa_chain '<your question>'")
        sys.exit(1)

    question = sys.argv[1]
    print(answer_query(question))

