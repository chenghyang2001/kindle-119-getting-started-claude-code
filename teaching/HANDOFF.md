# K119 演練交接

## 原機器結果

本書沒有在其他機器演練過。書上的練習多半是拿讀者自己的既有專案操作，這裡每章先建最小示範專案再照書上提示詞做；差異以「和書上做法的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和書上做法的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-22 | 5 分 | 自建最小 Express 專案取代讀者既有專案；全自動一次跑完（書上逐步人工把關＋Plan mode）；通知只做 console 不接 SendGrid；不開 PR |
| 02 | 2026-10-22 | 3 分 | 用 uv 取代 venv＋pip；docs 用自寫 inspect 腳本產生（非 pdoc）以維持零依賴；Flask-Limiter 用 memory:// 不接 Redis；一個提示詞全自動跑完；pytest 21 passed |
| 03 | 2026-10-22 | 10 分 | 三步各自 commit，但計畫沒經人工審核；交易用假 db 快照回滾；npm 預設裝 TypeScript 7 與 ts-jest 不相容，自動降到 5.9.3（耗時主因） |
| 04 | 2026-10-22 | 3 分 | 舊專案與 bug 是自己先造的，探索/找原因少了真正摸索；Excel exporter 用 TSV 模擬；pytest 1 failed → 15 passed，doctest 3 passed |
| 05 | 2026-10-22 | 3 分 | Redis 換記憶體 store、時鐘可注入免真等 60 秒；TDD 紅燈 commit 是模組不存在的 collection 錯誤；43 → 56 passed |
| 06 | 2026-10-22 | 5 分 | 實裝 React 19／Vite 8／TS 7（較書新）；骨架手寫不用 npm create vite；用 claude -p 取代互動會話產元件＋hook；內層 claude -p 觸發本機全域 Stop hook 自動 commit；全域 CLAUDE.md 只寫範本到 templates/，md5 確認未變 |
| 07 | 2026-10-22 | 6 分 | isolated（--setting-sources project,local）；開窗先跳「允許外部 CLAUDE.md 匯入」，用 ↓＋Enter 選允許（wt-send 只支援 Esc）；hook 寫 settings.local.json；用 claude -p＋stream-json＋標記字串客觀驗證（書上互動目視）；全域 settings.json 開窗時被改成 LF 換行（內容同），已從備份還原 |
| 08 | 2026-10-22 | 4 分 | 衝突是兩個短命分支刻意改同一段 pricing.py；SendGrid 用 mock；不 push、不 gh pr create，改產生 PR.md；feature 分支未合回 main；main 7 passed、feature 9 passed |
| 09 | 2026-10-22 | 10 分 | 不接 PostgreSQL 改可注入記憶體 store；測試用 Vitest＋supertest（非 Jest）；ESLint 10 扁平設定，首次 lint 29 錯→0；實裝 TypeScript 6.0.3 與 typescript-eslint 相容未降版；耗時主因是修 lint 與裝套件 |
