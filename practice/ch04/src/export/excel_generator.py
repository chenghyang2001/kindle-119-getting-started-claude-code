# no openpyxl on the build box, so we write a tab separated file excel can open
import csv
import io

COLUMNS = ["invoice_id", "customer", "amount"]


class ExcelGenerator:
    ext = "xls.tsv"

    def __init__(self, rows):
        self.rows = rows

    def validate(self):
        for r in self.rows:
            for c in COLUMNS:
                if c not in r:
                    raise KeyError(f"missing column: {c}")

    def render(self):
        self.validate()
        buf = io.StringIO()
        w = csv.writer(buf, delimiter="\t", lineterminator="\r\n")
        w.writerow([c.upper() for c in COLUMNS])
        total = 0.0
        for r in self.rows:
            total += r["amount"]
            w.writerow([r["invoice_id"], r["customer"], f'{r["amount"]:.2f}'])
        w.writerow(["", "TOTAL", f"{total:.2f}"])
        return buf.getvalue()

    def save(self, path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            f.write(self.render())
        return path
