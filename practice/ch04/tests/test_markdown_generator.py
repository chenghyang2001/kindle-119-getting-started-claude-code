import pytest

from export.markdown_generator import MarkdownGenerator

ROWS = [
    {"invoice_id": "INV-1", "customer": "Acme", "amount": 45.84},
    {"invoice_id": "INV-2", "customer": "王小明", "amount": 10},
]


def test_render_table():
    lines = MarkdownGenerator(ROWS).render().splitlines()
    assert lines[0] == "| invoice_id | customer | amount |"
    assert lines[1] == "| --- | --- | ---: |"
    assert lines[3] == "| INV-2 | 王小明 | 10.00 |"


def test_empty_rows_only_header():
    assert len(MarkdownGenerator([]).render().splitlines()) == 2


def test_escape_pipe_and_newline():
    row = {"invoice_id": "X", "customer": "A|B\nC", "amount": 1}
    assert r"| X | A\|B C | 1.00 |" in MarkdownGenerator([row]).render()


def test_missing_column():
    with pytest.raises(KeyError):
        MarkdownGenerator([{"invoice_id": "X"}]).render()


def test_save(tmp_path):
    p = MarkdownGenerator(ROWS).save(tmp_path / "a.md")
    assert p.read_text(encoding="utf-8").startswith("| invoice_id")
