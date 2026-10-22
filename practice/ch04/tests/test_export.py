import pytest

from export.csv_generator import CsvGenerator
from export.excel_generator import ExcelGenerator

ROWS = [
    {"invoice_id": "INV-1", "customer": "Acme", "amount": 45.84},
    {"invoice_id": "INV-2", "customer": "王小明", "amount": 10},
]


def test_csv_render():
    out = CsvGenerator(ROWS).render()
    assert out.splitlines()[0] == "invoice_id,customer,amount"
    assert "INV-2,王小明,10.00" in out


def test_csv_missing_column():
    with pytest.raises(KeyError):
        CsvGenerator([{"invoice_id": "X"}]).render()


def test_excel_render_total():
    out = ExcelGenerator(ROWS).render()
    lines = out.split("\r\n")
    assert lines[0] == "INVOICE_ID\tCUSTOMER\tAMOUNT"
    assert lines[-2] == "\tTOTAL\t55.84"


def test_save(tmp_path):
    p = CsvGenerator(ROWS).save(tmp_path / "a.csv")
    assert p.read_text(encoding="utf-8").startswith("invoice_id")
