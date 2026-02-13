import sys
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


from .config import OPENAI_API_KEY, INDEX_DIR

def get_qa_chain(k: int = 3, temperature: float = 0.0):
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
        質問自体の正確性についても検討した上で、コンテキストに従って回答してください。
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

    # OpenAI APIのタイムアウトを120秒に設定（Gunicornのタイムアウトと合わせる）
    llm = ChatOpenAI(
        model_name="gpt-5-mini",
        temperature=temperature,
        timeout=120.0,  # 秒単位
        max_retries=2,  # リトライ回数
    )

    # RAG チェーン（LCEL を利用）
    qa_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return qa_chain

def answer_query(query: str) -> str:
    """
    単発クエリを受け取って回答文字列だけを返す
    """
    chain = get_qa_chain()
    # LCEL チェーンは文字列を直接受け取り、そのまま回答文字列を返す
    output = chain.invoke(query)
    return str(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.qa_chain '<your question>'")
        sys.exit(1)

    question = sys.argv[1]
    print(answer_query(question))

