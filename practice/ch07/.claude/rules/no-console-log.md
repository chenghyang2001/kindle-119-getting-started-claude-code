---
paths:
  - "src/**/*.js"
  - "src/**/*.ts"
---

# 規則：禁止 console.log

`src/` 下的正式程式碼**不可以**出現 `console.log`。

- 原因：會把除錯資訊（甚至密碼、token）洩漏到正式環境的 log。
- 正確做法：改用專案的 logger（例如 `logger.debug()`），或在提交前移除。
- 審查或解釋程式碼時，發現 `console.log` 必須標示 `[rule:no-console-log]` 並指出行號。
