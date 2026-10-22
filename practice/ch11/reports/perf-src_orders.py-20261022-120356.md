# `src/orders.py` 效能審查

**總評：** 三個函式都有效能問題。`find_duplicate_ids` 和 `total_by_customer` 用了 O(n²) 或 O(C·N) 的巢狀掃描，資料量一大就會明顯變慢，這兩個應優先修正；`build_report` 的字串串接問題較輕。三個都能改成單次掃描 O(n)，而且輸出和原本一樣。

---

### 1. 第 7–10 行：`find_duplicate_ids` 用兩兩比對找重複
- **問題：** 雙層迴圈要比對 n(n−1)/2 次，複雜度 O(n²)。另外 `not in duplicates` 是在 list 上線性搜尋，所以最壞情況是 O(n²·k)，k 為重複 id 的數量。每次比對還會重複取用 `orders[i]["id"]` 三次。訂單到 1 萬筆時大約要比對 5,000 萬次。
- **嚴重度：** 🔴 高
- **建議：** 用 `collections.Counter` 一次算出每個 id 出現幾次，複雜度 O(n)。`Counter` 會保留插入順序，所以結果照「第一次出現」排列，和原本一樣。如果改用 seen set，在「第二次出現」時才加入，順序可能和原本不同。
```python
from collections import Counter

def find_duplicate_ids(orders):
    """找出重複的訂單編號（O(n)，依第一次出現的順序回傳）"""
    id_counts = Counter(order["id"] for order in orders)
    return [order_id for order_id, count in id_counts.items() if count > 1]
```
> 前提：`id` 必須可以 hash（int 或 str 都可以）。

---

### 2. 第 25–26 行：`total_by_customer` 為每位客戶重掃一次全部訂單
- **問題：** 外層跑 C 位客戶，內層的 `sum(...)` 每次都掃完 N 筆訂單，複雜度 O(C·N)。1,000 位客戶 × 10 萬筆訂單就是 1 億次比較。
- **嚴重度：** 🔴 高
- **建議：** 先把每位客戶的總額設成 0，再把訂單掃一次累加，複雜度 O(C + N)。這個寫法和原本行為一樣：沒有訂單的客戶是 0，不在 `customers` 名單裡的訂單會被忽略。
```python
def total_by_customer(orders, customers):
    """每位客戶的消費總額（訂單只掃一次）"""
    totals = dict.fromkeys(customers, 0)
    for order in orders:
        customer = order["customer"]
        if customer in totals:  # dict 查找為 O(1)
            totals[customer] += order["amount"]
    return totals
```

---

### 3. 第 16–18 行：`build_report` 在迴圈內用 `+=` 串接字串
- **問題：** Python 的字串不可變，理論上每次 `+=` 都要配置新字串並複製舊內容，最壞是 O(n²)。CPython 在某些情況會原地擴充，但這只是實作細節，不保證：PyPy、或字串同時被其他變數參照時，就不會有這個優化。
- **嚴重度：** 🟡 中
- **建議：** 改用 `"".join()` 一次組好。每行結尾的 `\n` 要保留，輸出才會完全相同。
```python
def build_report(orders):
    """組報表字串（join 一次配置）"""
    return "".join(f"{order['id']},{order['amount']}\n" for order in orders)
```

---

### 4. 第 14–19 行：`build_report` 先把整份報表放進記憶體（延伸建議）
- **問題：** 如果報表最後是要寫進檔案或網路，先組成一個完整大字串，記憶體用量是 O(n) 而且有峰值；訂單上百萬筆時會很明顯。
- **嚴重度：** 🟢 低（以目前的用途來看）
- **建議：** 另外提供串流版本，產生一行就寫出一行，不用另外組完整字串。
```python
def iter_report_lines(orders):
    """逐行產生報表內容，供串流寫檔使用"""
    for order in orders:
        yield f"{order['id']},{order['amount']}\n"

# 用法：直接寫檔，不另外組完整字串
# with open(path, "w", encoding="utf-8") as report_file:
#     report_file.writelines(iter_report_lines(orders))
```

---

### 摘要

| 行號 | 函式 | 原複雜度 | 改後 | 嚴重度 |
| --- | --- | --- | --- | --- |
| 7–10 | `find_duplicate_ids` | O(n²)，最壞 O(n²·k) | O(n) | 🔴 高 |
| 25–26 | `total_by_customer` | O(C·N) | O(C + N) | 🔴 高 |
| 16–18 | `build_report` | 最壞 O(n²) | O(n) | 🟡 中 |
| 14–19 | `build_report`（記憶體） | O(n) 峰值 | O(1) 串流 | 🟢 低 |

以上寫法都能讓檔案底部原有的 `assert` 冒煙測試照樣通過。依你的要求，沒有修改任何檔案。
