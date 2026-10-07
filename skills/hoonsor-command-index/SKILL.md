---
name: hoonsor-command-index
description: >
  快速指令索引總覽。當使用者輸入「#指令」、「列出指令」、「所有指令」、「指令清單」時載入此技能，
  列出所有已設定的快速指令（#開頭）及其功能說明、執行動作與適用場景。
---

# 📋 快速指令索引 (#指令)

> 當使用者輸入「**#指令**」時，請直接將下方表格與詳細說明，以清晰易讀的格式呈現給使用者。

---

## 🗂️ 指令總覽表

| # | 指令 | 對應技能 | 一句話說明 |
|---|------|----------|-----------|
| 1 | `#開工` | antigravity-workflow | 開啟專案、讀取架構文件、同步遠端最新代碼，開始工作 |
| 2 | `#收工` | antigravity-workflow | 檢查敏感資料、更新筆記、commit + push、備份 worktree |
| 3 | `#更新` | antigravity-workflow | 與 `#收工` 完全相同，適合階段性存檔同步 |
| 4 | `#合併` | antigravity-workflow | 將開發分支合併到主分支並推送部署 |
| 5 | `#分支` | antigravity-workflow | Clone 遠端倉庫或建立 Git Worktree 隔離分支 |
| 6 | `#初始化` | antigravity-workflow | Git 初始化 → GitHub 建庫 → 首次推送 → Vercel 部署 |
| 7 | `#架構` | antigravity-workflow | 掃描現有專案自動生成 `ANTIGRAVITY.md` 架構文件 |
| 8 | `#全更新` | hoonsor-update-all-projects | 一鍵檢查並同步電腦上所有登記專案與遠端倉庫 |
| 9 | `#同步` | hoonsor-sync-global-skills | 將全域設定與技能備份同步至 GitHub 遠端倉庫 |
| 10 | `#學習` | hoonsor-error-learning | 從對話中提取錯誤教訓，歸檔至知識庫避免重蹈覆轍 |
| 11 | `#狀態` | hoonsor-project-monitor | 將變更內容掃描同步並部署至監控網站 |
| 12 | `#喜好` | hoonsor-preferences | 分析對話中的偏好並記錄至 PREFERENCES.md |
| 13 | `#筆記` | hoonsor-note-from-chat | 從對話中擷取指定主題，生成 Obsidian 格式筆記 |
| 14 | `#指令` | hoonsor-command-index | 顯示本清單（你正在看的這個） |
| 15 | `#測試` | antigravity-workflow | 自動在背景啟動當前專案的開發伺服器 (如 npm run dev) |
| 16 | `#尋找新技能` | hoonsor-skill-hunter | 上網發掘社群熱門 Antigravity 技能並自動下載安裝 |
| 17 | `#分支接手` | hoonsor-branch-handoff | 建立 Git 交接分支與環境，產出詳盡交接文件供其他 AI 接手 |
| 18 | `#分支比較` | hoonsor-branch-compare | 評估其他 AI 接手完成的分支品質與差異，並提供合併建議 |

---

## 📖 各指令詳細說明

### 1. `#開工`
- **所屬技能**：`antigravity-workflow`
- **功能**：開啟每日/每次的開發工作階段
- **執行動作**：
  1. 檢查資料夾，若為空則要求提供 GitHub 倉庫網址
  2. 讀取 `ANTIGRAVITY.md` 與 `PROJECT_STATUS.md`
  3. **強制** `git fetch` → 檢查是否落後遠端 → 自動 `git pull --rebase`
  4. 檢視最近 3 筆 commit 記錄
  5. 回報專案狀態與建議下一步
- **適用場景**：每次開啟新對話要開始寫程式前

---

### 2/3. `#收工` / `#更新`
- **所屬技能**：`antigravity-workflow`
- **功能**：階段性或收尾時存檔同步至遠端
- **執行動作**：
  1. 檢查敏感資料（API key、token 等）
  2. 更新專案筆記（完成事項、踩坑記錄）
  3. 同步更新 `ANTIGRAVITY.md`
  4. `git status` + `git diff` → 只 stage 相關檔案 → commit + push
  5. 並行備份其他 worktree 分支
  6. 清理已合併的分支與 worktree
  7. 若為網站專案且在 main 分支，自動觸發 Vercel 部署
- **適用場景**：做完一個段落要存檔、或今日工作結束時

---

### 4. `#合併`
- **所屬技能**：`antigravity-workflow`
- **功能**：將功能分支合併到主分支
- **執行動作**：
  1. 檢查當前分支與未提交變更（防呆確認）
  2. 切到 main → `git pull origin main`
  3. 執行 `git merge <開發分支>`（遇衝突立即暫停回報）
  4. 推送 main 至遠端
  5. 切回原開發分支
- **適用場景**：功能開發完畢、測試通過後要合併至主線

---

### 5. `#分支`
- **所屬技能**：`antigravity-workflow`
- **功能**：建立新的開發分支環境
- **執行動作**：
  - **宇宙 A**（空資料夾 + GitHub URL）：Clone → 建立/切換分支
  - **宇宙 B**（空資料夾 + 本地專案路徑）：建立 Git Worktree 隔離開發
- **適用場景**：要開一個新功能分支、或從現有專案拉出獨立的開發環境

---

### 6. `#初始化`
- **所屬技能**：`antigravity-workflow`
- **功能**：為專案建立完整的 Git + GitHub + Vercel 基礎設施
- **執行動作**：
  1. 偵測是否已有 Git/遠端倉庫（智慧分流）
  2. 在 GitHub 建立新倉庫
  3. `git init` → `git remote add` → 首次 commit + push
  4. 若為網站專案，自動 Vercel 部署
- **適用場景**：新專案第一次要上傳到 GitHub 時

---

### 7. `#架構`
- **所屬技能**：`antigravity-workflow`
- **功能**：自動掃描專案並產生 `ANTIGRAVITY.md`
- **執行動作**：
  1. 掃描所有程式碼檔案與目錄結構
  2. 分析技術棧（語言、框架、依賴）
  3. 自動在根目錄產生 `ANTIGRAVITY.md`
- **適用場景**：專案已有程式碼但缺少架構文件時

---

### 8. `#全更新`
- **所屬技能**：`hoonsor-update-all-projects`
- **功能**：一鍵批次同步所有已登記的本地專案
- **執行動作**：
  1. 執行 PowerShell 自動化腳本
  2. 遍歷 `projects/*.json` 中的所有專案
  3. 對有遠端倉庫的專案執行 `git fetch` + `git pull --rebase`
  4. 彙總所有專案的同步狀態表
- **適用場景**：長時間沒碰電腦、想一次把所有專案拉到最新

---

### 9. `#同步`
- **所屬技能**：`hoonsor-sync-global-skills`
- **功能**：將全域設定與技能備份至 GitHub
- **執行動作**：
  1. 執行同步 PowerShell 腳本 `sync.ps1`
  2. 自動遮蔽 `mcp_config.json` 中的敏感金鑰
  3. 備份 `gemini.md` 與錯誤學習庫
  4. Git Pull Rebase → Commit → Push
- **適用場景**：修改了全域技能或設定後，要同步到 GitHub 備份

---

### 10. `#學習`
- **所屬技能**：`hoonsor-error-learning`
- **功能**：從當前對話中萃取錯誤教訓並歸檔
- **執行動作**：
  1. 掃描對話紀錄中的所有錯誤事件
  2. 識別「Token 浪費模式」（盲目重試、方向錯誤等 7 種）
  3. 萃取結構化教訓（根因分析、無效嘗試、正確解法）
  4. 持久化歸檔至 `error_lessons.md`、`quick_fixes.md`
  5. 評估是否升級為黃金法則寫入 `gemini.md`
  6. 產出學習報告
- **適用場景**：踩了坑、走了彎路後，想把這次經驗記錄下來

---

### 11. `#狀態`
- **所屬技能**：`hoonsor-project-monitor`
- **功能**：將變更掃描同步並部署至監控網站
- **執行動作**：
  1. 解析當前對話的變更指示（確認要更新什麼）
  2. 執行對應掃描腳本（技能/工作流/專案）
  3. 自動 Git commit + push 至監控網站倉庫
  4. 觸發 Vercel 部署更新 https://aiprohub.vercel.app/
- **適用場景**：完成了某項變更，想同步更新到監控網站上

---

### 12. `#喜好`
- **所屬技能**：`hoonsor-preferences`
- **功能**：分析並記錄使用者的偏好與風格
- **執行動作**：
  1. 回溯當前對話歷史
  2. 提取使用者表達的偏好（代碼風格、UI 美感、功能需求等）
  3. 歸納並寫入/更新 `PREFERENCES.md`
  4. 版本升級 + Git commit + push
  5. 回報新識別的偏好項目清單
- **適用場景**：想把這次對話中表達的喜好永久記錄下來

---

### 13. `#筆記`
- **所屬技能**：`hoonsor-note-from-chat`
- **功能**：從當前對話中擷取指定主題，生成 Obsidian Markdown 格式筆記
- **執行動作**：
  1. **主題確認**：解析 `#筆記` 後方的主題說明（若未指定則**立即詢問**，絕不自行生成）
  2. 搜尋當前對話紀錄中與主題相關的所有內容（含使用者附圖）
  3. **資訊正確性校驗**：以對話中最終確認的正確資訊為準，過時資訊不採用
  4. 生成含心智圖（Mermaid）、表格、Callout 的 Obsidian 筆記
  5. 儲存至 `D:\Obsidian\Hoonsor\●AI生成筆記\`，檔名格式 `YYYYMMDD-<主題>.md`
  6. 回覆檔案連結
- **適用場景**：對話中學到了某個知識或操作流程，想留存為結構化筆記
- **使用範例**：`#筆記 建立supabase的專案並取得DIRECT_URL`

---

### 14. `#指令`
- **所屬技能**：`hoonsor-command-index`（本技能）
- **功能**：顯示所有快速指令清單
- **執行動作**：載入本 SKILL.md 並呈現指令總覽表與詳細說明
- **適用場景**：忘記有哪些指令、或想查看某個指令的用法

---

### 15. `#測試`
- **所屬技能**：`antigravity-workflow`
- **功能**：自動在背景啟動當前專案的開發伺服器
- **執行動作**：偵測當前專案類型 (如 Node.js / Python)，並在背景自動執行對應的啟動指令 (如 `npm run dev`)，回報本地測試網址
- **適用場景**：專案開發到一個段落，想立刻看網頁結果，不想自己開 CMD 打指令時

---

### 16. `#尋找新技能`
- **所屬技能**：`hoonsor-skill-hunter`
- **功能**：上網發掘並自動下載安裝社群開源的 Antigravity 技能
- **執行動作**：聯網搜尋 GitHub 上的 Antigravity 技能，列出表格供選擇，確認後自動 clone 並同步
- **適用場景**：想找尋社群上有沒有大神寫好的特定功能擴充包時

---

### 17. `#分支接手`
- **所屬技能**：`hoonsor-branch-handoff`
- **功能**：打包當前未完成的專案狀態與進度，轉交給其他 AI 接續開發
- **執行動作**：建立 Git 交接分支與隔離 Worktree，打包重要設定檔與未提交變更（排除環境包），自動產出詳盡的交接文件與待辦功能矩陣
- **適用場景**：遇到瓶頸，想把目前做到一半的專案交給 Codex、Claude 或 DeepSeek Harness 等其他 AI 繼續開發時

---

### 18. `#分支比較`
- **所屬技能**：`hoonsor-branch-compare`
- **功能**：比較其他 AI 接手完成的分支與主幹的品質差異
- **執行動作**：客觀比較交接分支與主線的進度、效能、與代碼品質，自動產出評分報告並給出是否該合併的建議
- **適用場景**：其他 AI 完成工作後，想決定要不要把它的修改合併回我們的主幹時

---

## 💡 額外相關觸發詞（非 # 指令但常用）

| 觸發詞 | 對應技能 | 說明 |
|--------|----------|------|
| 「生圖」「畫圖」 | antigravity-draw | 使用內建生圖或 API 產生圖片 |
| 「執行修正任務」「pull plan」 | hoonsor-pull-plan | 從 Vercel 網站拉取任務計畫並逐項實作 |
| 「批量」「並行處理」 | hoonsor-gemini-subagent | 啟動子代理並行處理大量任務 |
| 「連接 GitHub」 | antigravity-github | 設定 GitHub CLI 連接 |
| 「連接 NotebookLM」 | antigravity-notebooklm | 設定 NotebookLM MCP |
| 「連接 Firebase」 | antigravity-firebase | 設定 Firebase MCP |
| 「連接 Obsidian」 | antigravity-obsidian | 設定 Obsidian MCP |
| 「全部安裝」 | antigravity-install-all | 一次安裝所有懶人包技能 |
| 「初始化專案」「新專案」 | antigravity-workflow | 新專案初始化完整流程 |
| 「管理 MCP」「修正 MCP」 | hoonsor-mcp-manager | 管理與修復 MCP 伺服器配置 |
