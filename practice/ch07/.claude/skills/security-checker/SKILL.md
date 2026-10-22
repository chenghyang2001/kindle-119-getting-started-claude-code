---
name: security-checker
description: 檢查程式碼的安全問題（寫死的密碼／API key／token、SQL 注入、XSS、不安全的比對）。當使用者要求安全檢查、審查 PR、或程式碼涉及登入／認證／密碼時使用。
---

# Security Checker

對指定檔案做安全檢查，輸出第一行固定為 `[skill:security-checker]`。

## 檢查清單

1. **寫死的機密**：`password`、`secret`、`token`、`apiKey` 等變數被指定為字串常數 → 🔴 高風險
2. **明文比對密碼**：用 `===` / `==` 直接比對密碼，沒有 hash（bcrypt 等）→ 🔴
3. **注入**：字串串接組 SQL / shell 指令 → 🔴
4. **XSS**：把使用者輸入塞進 `innerHTML` → 🟡
5. **洩漏敏感資訊到 log**：`console.log` 印出密碼或 token → 🔴

## 輸出格式

| 嚴重度 | 檔案:行號 | 問題 | 建議修法 |
| --- | --- | --- | --- |

最後一行：`發現 N 個問題（🔴 x / 🟡 y）`
