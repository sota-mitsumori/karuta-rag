import os
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
load_dotenv()

from src.qa_chain import answer_query

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("question", "")
    try:
        ans = answer_query(q)
    except Exception as e:
        app.logger.error(e)
        ans = "エラーが発生しました。もう一度お試しください。"
    return jsonify({"answer": ans})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
