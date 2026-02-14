"""
Supabaseにログを保存するモジュール
"""
import os
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon key または service_role key
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "chat_logs")  # デフォルトテーブル名

# Supabaseクライアント（設定がある場合のみ初期化）
supabase_client: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[logger] Supabaseクライアントの初期化に失敗しました: {e}")
        supabase_client = None


def log_chat(
    question: str,
    answer: str,
    channel: str = "web",  # "web" または "line"
    user_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> bool:
    """
    チャットログをSupabaseに保存
    
    Args:
        question: ユーザーの質問
        answer: アシスタントの回答
        channel: チャネル（"web" または "line"）
        user_id: ユーザーID（LINEの場合はLINE user_id、Webの場合は任意）
        metadata: 追加のメタデータ（任意）
    
    Returns:
        保存に成功した場合True、失敗した場合False
    """
    if not supabase_client:
        print("[logger] Supabaseクライアントが初期化されていません。環境変数を確認してください。")
        return False
    
    try:
        # テーブルに存在するカラムのみを含める
        log_data = {
            "question": question,
            "answer": answer,
            "channel": channel,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        # metadataからテーブルに存在するカラムのみを追加
        # 現在はip_addressカラムがないため、metadataは無視
        # ip_addressも保存したい場合は、sql/add_ip_address_column.sqlを実行してください
        if metadata:
            # ip_addressカラムが存在する場合のみ追加（テーブルにカラムを追加した後）
            if "ip_address" in metadata:
                log_data["ip_address"] = metadata["ip_address"]
            pass
        
        # Supabaseに挿入
        response = supabase_client.table(SUPABASE_TABLE).insert(log_data).execute()
        
        if response.data:
            print(f"[logger] ログを保存しました: {channel} - {question[:50]}...")
            return True
        else:
            print(f"[logger] ログの保存に失敗しました（レスポンスが空）")
            return False
            
    except Exception as e:
        print(f"[logger] ログの保存中にエラーが発生しました: {e}")
        return False


def save_shared_conversation(token: str, messages: list[dict]) -> bool:
    """
    シェア用会話をSupabaseに保存
    messages: [{"question": "...", "answer": "..."}, ...]
    """
    if not supabase_client:
        return False
    try:
        supabase_client.table("shared_conversations").insert({
            "token": token,
            "messages": messages,
        }).execute()
        return True
    except Exception as e:
        print(f"[logger] 共有会話の保存に失敗: {e}")
        return False


def get_shared_conversation(token: str) -> Optional[list[dict]]:
    """
    トークンに紐づく会話を取得。存在しなければ None
    """
    if not supabase_client:
        return None
    try:
        r = supabase_client.table("shared_conversations").select("messages").eq("token", token).limit(1).execute()
        if not r.data or len(r.data) == 0:
            return None
        return r.data[0].get("messages")
    except Exception as e:
        print(f"[logger] 共有会話の取得に失敗: {e}")
        return None
