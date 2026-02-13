# Gunicorn設定ファイル
# 本番環境でのタイムアウト設定を延長

import os
import multiprocessing

# ワーカーの数（CPUコア数 * 2 + 1、最小1）
workers = max(multiprocessing.cpu_count() * 2 + 1, 1)

# ワーカークラス（同期ワーカー）
worker_class = "sync"

# タイムアウト時間（秒）- OpenAI APIの応答を待つため120秒に設定
timeout = 120

# キープアライブタイムアウト
keepalive = 5

# ワーカーの接続数
worker_connections = 1000

# ログレベル
loglevel = "info"

# アクセスログ
accesslog = "-"

# エラーログ
errorlog = "-"

# プロセス名
proc_name = "karuta-rag"

# バインディング（環境変数PORTから取得、デフォルトは5000）
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
