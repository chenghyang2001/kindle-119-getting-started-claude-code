#!/bin/bash
# 用 claude -p 對單一檔案做效能審查，報告存到 reports/
# 用法：scripts/review.sh <檔案路徑>
set -euo pipefail

# 清掉所有 CLAUDE 開頭的環境變數：在 Claude Code session 內呼叫時，
# 這些變數會讓子程序誤以為自己是巢狀 session（K119 第 11 章提醒）
for var_name in $(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true); do
  unset "$var_name"
done

target_file="${1:-}"
if [ -z "$target_file" ]; then
  echo "錯誤：請指定要審查的檔案，例如 scripts/review.sh src/orders.py" >&2
  exit 1
fi
if [ ! -f "$target_file" ]; then
  echo "錯誤：找不到檔案 $target_file" >&2
  exit 1
fi
command -v claude >/dev/null || { echo "錯誤：找不到 claude CLI" >&2; exit 1; }

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$repo_root/reports"
safe_name="$(echo "$target_file" | sed 's#[/\]#_#g')"
report_path="$repo_root/reports/perf-${safe_name}-$(date +%Y%m%d-%H%M%S).md"

prompt="你是效能審查員。請只針對效能問題審查以下檔案（時間複雜度、重複計算、不必要的記憶體配置、I/O）。
用繁體中文輸出 Markdown：先一行總評，再列出每個問題（行號、問題、嚴重度 高/中/低、建議改法與範例程式碼）。
不要修改任何檔案。

檔名：$target_file
\`\`\`
$(cat "$target_file")
\`\`\`"

echo "審查中：$target_file ..." >&2
# 檔案內容已放進 prompt，不需要工具，因此不給任何工具權限
if ! printf '%s' "$prompt" | claude -p --output-format text > "$report_path"; then
  echo "錯誤：claude -p 執行失敗" >&2
  rm -f "$report_path"
  exit 1
fi
echo "報告已存：$report_path"
