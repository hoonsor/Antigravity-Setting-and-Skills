---
name: hoonsor-skill-hunter
description: 自動上網搜尋 GitHub 與熱門論壇上的開源 Antigravity 技能，統整列表後供使用者選擇並一鍵安裝至全域技能庫。說「#尋找新技能」或「找新技能」時載入。
---

# 技能獵人 (Skill Hunter)

這個技能專門用來協助使用者自動在網路上發掘、整理、並一鍵下載安裝社群開源的 Antigravity 擴充技能 (Skills)。

## 🎯 觸發條件
當使用者輸入 **`#尋找新技能`**、**`幫我找新技能`** 等關鍵字時載入。

## ⚙️ 執行工作流 (Agent Workflow)

當被觸發時，請 Agent 嚴格依照以下步驟執行：

### 步驟 1：主動聯網搜尋 (Scouting)
1. 呼叫 `search_web` 工具，使用精準搜尋指令尋找網路上的 Antigravity 技能。建議的搜尋語法：
   - `site:github.com "Antigravity" "SKILL.md"`
   - `site:github.com "Antigravity skill"`
   - `"Antigravity plugin" OR "Antigravity skills" github`
2. 若有需要，可以呼叫 `read_url_content` 進入特定的 GitHub 倉庫讀取 `README.md` 或 `SKILL.md` 來確認該技能的品質與真實用途。

### 步驟 2：統整與推薦 (Reporting)
1. 篩選出 3~5 個看起來最具實用性、評分高或有趣的技能。
2. 以 Markdown 表格形式向使用者進行簡報，格式如下：
   | 技能名稱 | 功能描述 | 來源 (GitHub URL) |
   | :--- | :--- | :--- |
   | ... | ... | ... |
3. **主動發問**：使用文字詢問使用者「請問您對上述哪個技能感興趣？需要我直接為您安裝哪幾個？」等待使用者回覆。

### 步驟 3：自動化安裝 (Installation)
當使用者指定要安裝某個技能後：
1. **目錄準備**：前往 `$env:USERPROFILE\.gemini\config\skills\`。
2. **下載方式**：
   - 如果來源是一個完整的 Git 倉庫，請使用 `run_command` 執行 `git clone <repo_url>` 將其 Clone 到全域技能庫目錄下。
   - 如果只是單一的 `SKILL.md` (例如 Gist)，請自動建立對應的資料夾，並用 `write_to_file` 或 `curl` 將檔案寫入。
3. **安全檢查與防呆**：
   - 確保安裝後的資料夾中確實存在 `SKILL.md`。
   - 確認是否有潛在的安全風險指令，並提醒使用者。

### 步驟 4：雲端備份與收尾 (Sync)
1. 安裝成功後，向使用者回報安裝完成。
2. **自動觸發同步**：在背景執行 `$env:USERPROFILE\.gemini\config\skills\hoonsor-sync-global-skills\sync.ps1`，將剛安裝的新技能安全地同步並備份至使用者的 GitHub 全域設定庫，確保雲端與本地一致。
