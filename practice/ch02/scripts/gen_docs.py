"""從 utils/calculator.py 的 docstring 產生 docs/index.html（純 HTML、無外部依賴）。"""
import html
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils import calculator  # noqa: E402

PAGE = """<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>calculator 文件</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 16px;line-height:1.6;color:#222;background:#fff}}
code,pre{{font-family:Consolas,monospace;background:#f4f4f4;border-radius:4px}}
pre{{padding:12px;overflow-x:auto}} h2{{border-bottom:1px solid #ddd}}
</style></head>
<body>
<h1>模組 <code>utils.calculator</code></h1>
<p>{module_doc}</p>
{functions}
</body></html>
"""


def render_function(func):
    """把單一函式的簽名與 docstring 轉成 HTML 區塊。"""
    signature = f"{func.__name__}{inspect.signature(func)}"
    doc = inspect.getdoc(func) or "（無說明）"
    return (f'<section><h2 id="{func.__name__}"><code>{html.escape(signature)}</code></h2>'
            f"<pre>{html.escape(doc)}</pre></section>")


def main():
    try:
        public_funcs = [obj for name, obj in inspect.getmembers(calculator, inspect.isfunction)
                        if not name.startswith("_") and obj.__module__ == calculator.__name__]
        page = PAGE.format(module_doc=html.escape(inspect.getdoc(calculator) or ""),
                           functions="\n".join(render_function(f) for f in public_funcs))
        out = ROOT / "docs" / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"已產生 {out.relative_to(ROOT)}（{len(public_funcs)} 個函式）")
    except OSError as exc:
        print(f"錯誤：寫檔失敗 {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
