"""把發票資料匯出成 Markdown 表格。

沿用 CsvGenerator／ExcelGenerator 的共同模式：
COLUMNS 欄位定義、ext 副檔名、validate() → render() → save()。
"""
COLUMNS = ["invoice_id", "customer", "amount"]


def _escape(value):
    # 「|」會被當成欄位分隔、換行會切斷表格列，兩者都要處理
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


class MarkdownGenerator:
    ext = "md"

    def __init__(self, rows):
        self.rows = rows

    def validate(self):
        for r in self.rows:
            for c in COLUMNS:
                if c not in r:
                    raise KeyError(f"missing column: {c}")

    def render(self):
        self.validate()
        lines = [
            "| " + " | ".join(COLUMNS) + " |",
            "| --- | --- | ---: |",
        ]
        for r in self.rows:
            cells = [_escape(r["invoice_id"]), _escape(r["customer"]), f'{r["amount"]:.2f}']
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines) + "\n"

    def save(self, path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(self.render())
        return path
