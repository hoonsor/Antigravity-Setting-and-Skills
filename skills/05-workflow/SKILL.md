---
name: antigravity-workflow
description: AntiGravity 開工/收工/新專案初始化流程。說「開工」「收工」「初始化專案」時載入。
---

# 開工 / 收工 / 新專案初始化 / 架構生成

## #開工
1. 檢查當前資料夾：
   - 若資料夾為空或無專案檔案，主動要求使用者提供 GitHub 專案倉庫網址。
   - 若使用者同時提供了網址（例如：「#開工 https://github.com/hoonsor/...」）：
     - **檢查遠端分支**：在進行 `git clone` 之前，先利用 `git ls-remote --heads <URL>` 查詢該遠端倉庫的所有分支。
     - **分支確認與防呆 (重要)**：
       - 如果查詢結果顯示遠端除了預設主分支外，**還存在其他分支**，**請先暫停執行 clone**，並主動列出所有分支名稱向使用者確認：「*偵測到該遠端倉庫除了 main 之外，還有以下分支：[列出分支清單]。請問您本次是要使用 main 主分支作業，還是要在特定分支上作業？*」
       - 待使用者回答後，執行 `git clone <URL>`，並自動切換到使用者指定的對應分支（`git checkout <分支名稱>`）。
       - 如果遠端只有單一主分支，則直接執行 `git clone` 即可。
   - 若為新建立的空白專案（無 `ANTIGRAVITY.md`），自動套用「通用 ANTIGRAVITY.md 模板」建立初步架構。
2. 讀取 `ANTIGRAVITY.md`。若專案已成型但缺乏該檔案，應提示使用者使用 `#架構` 指令自動生成。
3. 讀取專案筆記重點（例如 `PROJECT_STATUS.md` 或專案筆記）。
4. 執行 `git status` 并檢視最近的 commit。
5. 回報狀態與建議下一步。

## #收工
1. 檢查敏感資料（API key、token、學生真名等）
2. 更新專案筆記（完成事項、下一步、踩坑）
3. 檢查專案修改情形，同步更新 `ANTIGRAVITY.md`（若技術棧、目錄結構或開發規則有變動）
4. 檢查 git status + diff
5. 只 stage 本次相關檔案（不用 `git add .`）
6. 確認後 commit + push
7. 回報同步結果

## #架構
當專案已成型（已有程式碼檔案），但資料夾中缺少 `ANTIGRAVITY.md` 檔時，使用者輸入 `#架構` 指令，你必須：
1. 掃描整個專案資料夾的所有主要程式碼檔案與目錄結構。
2. 分析技術棧（主要語言、框架、相依套件檔如 package.json/requirements.txt 等）。
3. 根據分析結果，自動在專案根目錄下產製對應的 `ANTIGRAVITY.md` 檔案，填入該專案的實際技術細節與核心結構。

## 新專案初始化
先問：名稱、用途、資料夾、是否 GitHub repo、公開/私有、是否部署。
建立：ANTIGRAVITY.md、README.md、.gitignore、Git repo、GitHub repo、專案筆記。
若已存在 → 盤點後只補缺口，不覆蓋。

---

## 📄 通用 ANTIGRAVITY.md 模板 (Template Reference)
```markdown
# ANTIGRAVITY 專案指導原則 (Project Guidelines)

> [!NOTE]
> 本文件是本專案的「最高指導原則（Source of Truth）」。Agent 在每次開工或開啟新對話時，必須優先閱讀此文件，並嚴格遵守以下約定。

---

## 📖 專案基本資訊 (Project Info)
*   **專案名稱**：<請填寫專案名稱>
*   **專案目標**：<簡述這個專案是要解決什麼問題，或提供什麼功能>
*   **目標客群 / 使用場景**：<例如：給學生使用的學習工具、內部自動化腳本等>

---

## 🛠 技術棧與環境要求 (Tech Stack & Environment)
*   **開發語言**：<例如：Python 3.11 / TypeScript / Kotlin 等>
*   **核心框架/庫**：<例如：FastAPI / React 19 / PyTorch 等>
*   **套件管理工具**：<例如：npm / pip / uv / poetry 等>
*   **環境變數檔**：本專案使用 `.env` 管理私鑰，嚴禁將私鑰直接寫入代碼或提交至 Git。

---

## 📁 專案目錄結構規範 (Directory Structure)
> 為了保持程式碼整潔，請將檔案建立在以下約定的目錄中：
*   src/：<放置核心邏輯與源碼>
*   tests/：<放置單元測試與整合測試檔案>
*   docs/：<放置專案相關說明文件>

---

## 🛡️ 開發守則與代碼風格 (Development & Coding Standards)
*   **命名規範**：<例如：變數使用 camelCase，Python 函數使用 snake_case>
*   **註解規範**：所有公共 API 與複雜邏輯必須撰寫詳細註解（中文說明）。
*   **Git 分支管理**：
    *   開發分支：<例如：請在 feature/ 相關分支上開發>
    *   主要分支：<例如：main 分支為生產環境，需通過 PR 合併>

---

## ⚠️ 絕對禁止事項 (Never Do)
1.  **嚴禁提交敏感資訊**：嚴禁將 API Keys、Tokens、密碼、或個人隱私資訊寫死在程式碼中。
2.  **嚴禁直接破壞主分支**：未經測試與確認前，禁止對 main/master 分支進行強制推送 (--force)。
3.  **嚴禁覆蓋既有功能**：在修改代碼前，必須確認不會破壞已存在的正常功能，必要時先執行現有測試。
```

