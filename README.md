# 競技かるたRAGシステム

競技かるたの競技規定・競技細則に関する質問に回答するRAG（Retrieval-Augmented Generation）システムです。

## 概要

このシステムは、競技かるたの公式PDF文書（競技規定・競技細則）をベクトルデータベースに格納し、自然言語での質問に対して関連する文書を検索して回答を生成します。

### 対応文書
- `kyougi_kitei.pdf` - 競技規定
- `kyougi_saisoku.pdf` - 競技細則
- `kyougi_saisoku_dantai.pdf` - 競技細則（団体）
- `kyougikai_kitei.pdf` - 競技会規定

## 機能

- **Web UI**: ブラウザベースのチャットインターフェース
- **LINE Bot**: LINEメッセージングアプリでの質問対応
- **REST API**: プログラムからの質問API

## 技術スタック

- **言語**: Python 3.13.1
- **RAGフレームワーク**: LangChain
- **埋め込みモデル**: OpenAI Embeddings
- **ベクトルデータベース**: FAISS
- **LLM**: GPT-4.1
- **Webフレームワーク**: Flask
- **PDF処理**: PyPDF

## セットアップ

### 1. 依存関係のインストール

```bash
make install
```

または

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. インデックスの構築

PDF文書からベクトルインデックスを構築します：

```bash
make index
```

または

```bash
python -m src.indexer
```

### 4. アプリケーションの起動

```bash
python app.py
```

## 使用方法

### Web UI

karuta-rag.onrender.com/

### LINE Bot

https://lin.ee/3xHScVr

### コマンドライン

```bash
python -m src.qa_chain "質問内容"
```

## プロジェクト構造

```
karuta-rag/
├── app.py                 # Flask Webアプリケーション
├── requirements.txt       # Python依存関係
├── Makefile              # ビルドコマンド
├── data/
│   └── karuta_rules_pdfs/  # 競技かるたPDF文書
├── src/
│   ├── __init__.py
│   ├── config.py         # 設定管理
│   ├── loader.py         # PDF読み込み・分割
│   ├── indexer.py        # ベクトルインデックス構築
│   ├── qa_chain.py       # RAGチェーン実装
│   └── utils.py          # ユーティリティ
├── templates/
│   └── index.html        # Web UIテンプレート
└── karuta_rules_faiss/   # FAISSインデックス保存先
```

## 設定

`src/config.py`で以下の設定を変更できます：

- `CHUNK_SIZE`: ドキュメント分割サイズ（デフォルト: 850）
- `CHUNK_OVERLAP`: チャンク間の重複文字数（デフォルト: 200）
- `PDF_DIR`: PDF文書の格納ディレクトリ
- `INDEX_DIR`: FAISSインデックスの保存ディレクトリ

## 開発

### テストの実行

```bash
make test
```

### インデックスの再構築

PDF文書を更新した場合は、インデックスを再構築してください：

```bash
make index
```

## 注意事項

- OpenAI APIキーが必要です
- PDF文書は`data/karuta_rules_pdfs/`ディレクトリに配置してください
- 初回実行時はインデックス構築が必要です

## ライセンス

このプロジェクトは競技かるたの2025年7月31日現在の公式文書を基にしています。