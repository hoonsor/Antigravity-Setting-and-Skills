---
name: antigravity-workflow
description: AntiGravity 開工/收工/新專案初始化流程。說「開工」「收工」「初始化專案」時載入。
---

# 開工 / 收工 / 新專案初始化

## #開工
1. 檢查當前資料夾：
   - 若資料夾為空或無專案檔案，主動要求使用者提供 GitHub 專案倉庫網址。
   - 若使用者同時提供了網址（例如：「#開工 https://github.com/hoonsor/...」），則自動將該倉庫 clone/pull 到當前資料夾路徑。
2. 讀取 `ANTIGRAVITY.md`。
3. 讀取專案筆記重點（例如 `PROJECT_STATUS.md` 或專案筆記）。
4. 執行 `git status` 并檢視最近的 commit。
5. 回報狀態與建議下一步。

## #收工
1. 檢查敏感資料（API key、token、學生真名等）
2. 更新專案筆記（完成事項、下一步、踩坑）
3. 只在規則改變時更新 ANTIGRAVITY.md
4. 檢查 git status + diff
5. 只 stage 本次相關檔案（不用 `git add .`）
6. 確認後 commit + push
7. 回報同步結果

## 新專案初始化
先問：名稱、用途、資料夾、是否 GitHub repo、公開/私有、是否部署。
建立：ANTIGRAVITY.md、README.md、.gitignore、Git repo、GitHub repo、專案筆記。
若已存在 → 盤點後只補缺口，不覆蓋。
