# app.py
import os
from flask import Flask, request, abort, render_template, jsonify
from dotenv import load_dotenv

# LINE SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# RAG チャット
from src.qa_chain import answer_query

# 環境変数ロード
load_dotenv()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)

# Web UI 用の簡易チャット履歴（プロセス内メモリ）
# [(user_question, assistant_answer), ...] の形で直近の会話を保持
WEB_CHAT_HISTORY: list[tuple[str, str]] = []

# LINE 用の簡易チャット履歴（ユーザーごと）
# {user_id: [(user_text, bot_reply), ...]}
LINE_CHAT_HISTORY: dict[str, list[tuple[str, str]]] = {}

# LINE Bot API & Handler
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 既存の Web UI
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("question", "")

    # 直近の履歴をテキストにまとめる（ChatGPT 風のコンテキスト）
    history_lines: list[str] = []
    for i, (hq, ha) in enumerate(WEB_CHAT_HISTORY[-5:], start=1):
        history_lines.append(f"[{i}] ユーザー: {hq}")
        history_lines.append(f"    アシスタント: {ha}")
    history_text = "\n".join(history_lines)

    if history_text:
        full_query = (
            "以下はこれまでの会話履歴です。この履歴も考慮して、"
            "最後に示すユーザーの新しい質問に日本語で丁寧に回答してください。\n\n"
            f"{history_text}\n\n"
            "ここからが現在のユーザーの質問です:\n"
            f"{q}"
        )
    else:
        full_query = q

    try:
        ans = answer_query(full_query)
    except Exception:
        ans = "エラーが発生しました。"

    # 履歴を更新（直近の質問と回答を保存）
    WEB_CHAT_HISTORY.append((q, ans))

    return jsonify({"answer": ans})

# LINE Webhook エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# LINE メッセージイベント処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    user_text = event.message.text

    # ユーザー ID（個別の会話コンテキストを持つため）
    user_id = event.source.user_id if hasattr(event, "source") else "unknown"

    # ユーザーごとの履歴を取得（なければ空リスト）
    history = LINE_CHAT_HISTORY.get(user_id, [])

    # 直近の履歴をテキストにまとめる
    history_lines: list[str] = []
    for i, (hq, ha) in enumerate(history[-5:], start=1):
        history_lines.append(f"[{i}] ユーザー: {hq}")
        history_lines.append(f"    アシスタント: {ha}")
    history_text = "\n".join(history_lines)

    if history_text:
        full_query = (
            "以下はこれまでのLINEでの会話履歴です。この履歴も考慮して、"
            "最後に示すユーザーの新しい質問に日本語で丁寧に回答してください。\n\n"
            f"{history_text}\n\n"
            "ここからが現在のユーザーの質問です:\n"
            f"{user_text}"
        )
    else:
        full_query = user_text

    try:
        bot_reply = answer_query(full_query)
    except Exception:
        bot_reply = "申し訳ありません。回答できませんでした。"

    # ユーザーごとの履歴を更新
    history.append((user_text, bot_reply))
    LINE_CHAT_HISTORY[user_id] = history
    # LINE に返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bot_reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
