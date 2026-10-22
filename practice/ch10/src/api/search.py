"""多租戶（multi-tenant）文件搜尋 API。

本模組示範 K119 第 10 章的情境：search() 內有一段「依 tenant_id 過濾」的
安全關鍵程式碼（約第 47 行）。日後請 AI 加功能（例如分頁）時，
必須確認這段過濾沒有被拿掉，否則會造成跨租戶資料外洩。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """一筆可被搜尋的文件。"""

    id: int
    tenant_id: str
    title: str
    body: str


# 示範用的記憶體資料庫（正式環境應為 DB 查詢）
DOCUMENTS: list[Document] = [
    Document(1, "acme", "Acme 季報", "acme 第三季營收報告"),
    Document(2, "acme", "Acme 合約", "與供應商的機密合約"),
    Document(3, "globex", "Globex 季報", "globex 第三季營收報告"),
    Document(4, "globex", "Globex 人事", "globex 機密人事資料"),
    Document(5, "acme", "Acme 會議紀錄", "季報 review 會議"),
]


def _matches(doc: Document, query: str) -> bool:
    """標題或內文包含關鍵字（不分大小寫）即視為命中。"""
    needle = query.lower()
    return needle in doc.title.lower() or needle in doc.body.lower()


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _validate_pagination(page: int, page_size: int) -> None:
    """檢查分頁參數；bool 是 int 的子類別，要明確排除避免 True 被當成 1。"""
    if isinstance(page, bool) or not isinstance(page, int):
        raise TypeError("page 必須是整數")
    if isinstance(page_size, bool) or not isinstance(page_size, int):
        raise TypeError("page_size 必須是整數")
    if page < 1:
        raise ValueError("page 必須 >= 1（從 1 開始）")
    if not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(f"page_size 必須介於 1 到 {MAX_PAGE_SIZE}")


def search(
    tenant_id: str,
    query: str,
    documents: list[Document] | None = None,
    *,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> list[Document]:
    """搜尋屬於指定租戶的文件，回傳第 page 頁（1-based）的結果。"""
    if not tenant_id:
        raise ValueError("tenant_id 不可為空")
    if query is None:
        raise ValueError("query 不可為 None")
    _validate_pagination(page, page_size)
    source = DOCUMENTS if documents is None else documents
    # 安全關鍵：只回傳同租戶資料，避免跨租戶外洩
    scoped = [doc for doc in source if doc.tenant_id == tenant_id]
    matched = [doc for doc in scoped if _matches(doc, query)]
    # 分頁必須在租戶過濾之後切片，否則某頁可能混入他租戶資料
    start = (page - 1) * page_size
    return matched[start : start + page_size]
