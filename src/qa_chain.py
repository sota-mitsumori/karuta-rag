import os
import sys
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


from .config import OPENAI_API_KEY, INDEX_DIR

# PDFファイル名（パス） → 表示用ルール名
SOURCE_DISPLAY_NAMES = {
    "kyougi_kitei.pdf": "競技規定",
    "kyougi_saisoku.pdf": "競技細則",
    "kyougi_saisoku_dantai.pdf": "競技細則（団体）",
    "kyougikai_kitei.pdf": "競技会規定",
}


def _source_to_display_name(source: str) -> str:
    """メタデータの source パスから表示用ルール名を返す"""
    if not source:
        return "公式文書"
    basename = os.path.basename(source).lower()
    return SOURCE_DISPLAY_NAMES.get(basename, basename.replace(".pdf", ""))


def _format_context_with_sources(docs: list[Document]) -> str:
    """検索されたドキュメントを「【ルール名】本文」形式で連結する"""
    parts = []
    for doc in docs:
        name = _source_to_display_name(doc.metadata.get("source", ""))
        parts.append(f"【{name}】\n{doc.page_content}")
    return "\n\n".join(parts)


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

    # 「コンテキスト以外は答えない」＋ 根拠ルール名を明示
    system_template = """\
        あなたは競技かるた公式PDFからのみ回答を行うアシスタントです。
        質問自体の正確性についても検討した上で、コンテキストに従って回答してください。
        回答では、根拠としたルール名を必ず明示してください。例：「競技規定によると、」「競技会規定によると、」のように、該当するルール名を冒頭または文中で示してください。複数のルールにまたがる場合はそれぞれ言及してください。
        """
    human_template = """\
        質問:
        {question}

        コンテキスト（【】内がルール名です）:
        {context}

        上記のコンテキスト以外の情報は一切使わずに答えてください。回答のどこかで、根拠としたルール名（競技規定・競技細則・競技会規定など）を「〇〇によると」の形で明示してください。
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

    # RAG チェーン（検索 → 出典付きコンテキスト整形 → プロンプト → LLM）
    qa_chain = (
        RunnablePassthrough.assign(**{"context": lambda x: _format_context_with_sources(retriever.invoke(x["question"]))})
        | prompt
        | llm
        | StrOutputParser()
    )
    # invoke には question だけ渡すので、辞書で渡す
    def chain_invoke(question: str):
        return qa_chain.invoke({"question": question})
    return chain_invoke

def answer_query(query: str) -> str:
    """
    単発クエリを受け取って回答文字列だけを返す
    """
    chain = get_qa_chain()
    output = chain(query)
    return str(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.qa_chain '<your question>'")
        sys.exit(1)

    question = sys.argv[1]
    print(answer_query(question))

