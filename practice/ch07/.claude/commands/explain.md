---
description: 用白話解釋指定檔案或程式碼片段
argument-hint: <檔案路徑或程式碼片段>
allowed-tools: Read, Grep, Glob
---

# /explain

請用繁體中文、給初學者看的方式解釋：**$ARGUMENTS**

要求：

1. 第一行固定輸出 `[command:explain] 目標：$ARGUMENTS`
2. 先用一句話說明這段程式在做什麼
3. 逐段（或逐函式）解釋邏輯
4. 列出你注意到的問題；若違反專案規則（`.claude/rules/`），用 `[rule:<規則名>]` 標示
