import os
from dotenv import load_dotenv

# .env ファイルから環境変数をロード
load_dotenv()

# OpenAI API キー
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# PDF が格納されたディレクトリ
PDF_DIR = os.getenv("PDF_DIR", "data/karuta_rules_pdfs")

# FAISS インデックス保存先ディレクトリ
INDEX_DIR = os.getenv("INDEX_DIR", "karuta_rules_faiss")

# ドキュメント分割設定
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "850"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))