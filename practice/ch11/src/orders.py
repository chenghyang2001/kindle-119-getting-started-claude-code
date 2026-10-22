"""訂單統計小模組（刻意留有效能問題，供審查練習）"""


def find_duplicate_ids(orders):
    """找出重複的訂單編號（O(n^2) 寫法）"""
    duplicates = []
    for i in range(len(orders)):
        for j in range(i + 1, len(orders)):
            if orders[i]["id"] == orders[j]["id"] and orders[i]["id"] not in duplicates:
                duplicates.append(orders[i]["id"])
    return duplicates


def build_report(orders):
    """組報表字串（迴圈內字串串接）"""
    report = ""
    for order in orders:
        report += f"{order['id']},{order['amount']}\n"
    return report


def total_by_customer(orders, customers):
    """每位客戶的消費總額（每位客戶都掃一次全部訂單）"""
    totals = {}
    for customer in customers:
        totals[customer] = sum(o["amount"] for o in orders if o["customer"] == customer)
    return totals


if __name__ == "__main__":
    sample = [
        {"id": 1, "customer": "A", "amount": 100},
        {"id": 2, "customer": "B", "amount": 50},
        {"id": 1, "customer": "A", "amount": 100},
    ]
    assert find_duplicate_ids(sample) == [1]
    assert total_by_customer(sample, ["A", "B"]) == {"A": 200, "B": 50}
    print(build_report(sample), end="")
    print("冒煙測試通過")
