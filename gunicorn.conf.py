import os

# ワーカー数は「1」に固定（メモリ節約のため）
workers = 1

# ワーカークラスを「gthread」に変更（並行処理のため）
# OpenAIなどのAPI待ち中も、他の人のアクセスを処理できるようにします
worker_class = "gthread"

# スレッド数を指定（1つのワーカーの中で4つの処理を同時進行）
threads = 5

# タイムアウト（そのまま維持）
timeout = 120
keepalive = 5

# その他（そのまま維持）
loglevel = "info"
accesslog = "-"
errorlog = "-"
proc_name = "karuta-rag"
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"