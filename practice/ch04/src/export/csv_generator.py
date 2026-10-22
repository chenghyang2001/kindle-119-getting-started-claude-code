import csv
import io

COLUMNS = ["invoice_id", "customer", "amount"]


class CsvGenerator:
    ext = "csv"

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
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in self.rows:
            w.writerow([r["invoice_id"], r["customer"], f'{r["amount"]:.2f}'])
        return buf.getvalue()

    def save(self, path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(self.render())
        return path
