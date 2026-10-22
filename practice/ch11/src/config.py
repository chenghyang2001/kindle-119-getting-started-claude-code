"""應用程式設定：機密一律從環境變數讀取"""
import os
import sys


def get_db_password():
    """取得資料庫密碼，缺少時明確報錯"""
    password = os.environ.get("APP_DB_PASSWORD")
    if not password:
        print("錯誤：缺少環境變數 APP_DB_PASSWORD", file=sys.stderr)
        sys.exit(1)
    return password
