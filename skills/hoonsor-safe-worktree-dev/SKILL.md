---
name: hoonsor-safe-worktree-dev
description: 強制沙盒開發機制 (Safe Worktree Workflow)。在對現有 Git 專案進行任何程式碼修改前，自動建立並切換至獨立的 git worktree 目錄，確保原工作目錄與主分支的安全，避免修改失敗污染原始代碼。
---

# 🛡️ Safe Worktree Development Workflow (強制沙盒開發機制)

身為 Google Antigravity Architect，當使用者要求對現有專案進行「程式碼修改」、「新增功能」、「修復 Bug」等會變更原始碼的操作時，應主動觸發此技能，採用 `git worktree` 進行實體隔離的沙盒開發。

## 🎯 核心理念
*   **物理隔離**：傳統的 `git branch` 仍在同一個資料夾內修改檔案，切換分支時可能導致依賴庫（如 `node_modules`、`venv`）錯亂。
*   **防呆防爆**：透過 `git worktree` 在完全不同的實體資料夾中進行修改。改壞了？直接把整個沙盒資料夾刪除，原本的專案目錄毫髮無傷。

## 🚀 執行標準作業程序 (SOP)

當接收到程式碼修改任務時，請**嚴格依照以下順序執行**，不要直接在原目錄修改檔案：

### 1. 任務分析與命名
1. 分析使用者的修改需求。
2. 根據需求生成一個簡短且具描述性的分支名稱。
   - 格式：`<類型>/<簡短描述>`（例如：`feat/add-login-api`, `fix/header-css`, `task/refactor-db`）。

### 2. 建立隔離工作區 (Git Worktree)
1. 確保目前位於使用者的原始專案目錄下（且為 Git 倉庫）。若不是 Git 倉庫，請先建議使用者初始化 Git，或退回傳統開發模式。
2. 確定新的 Worktree 存放路徑。為了不弄亂使用者的資料夾結構，建議將其建立在原專案的「同層目錄」下，並加上後綴。
   - 假設原專案為：`D:\Projects\MyApp`
   - 新 Worktree 路徑應為：`D:\Projects\MyApp_worktrees\<分支名稱>` (若含斜線請轉為橫線，如 `MyApp_worktrees\feat-add-login`)。
3. 執行指令建立 Worktree 與新分支：
   ```bash
   git worktree add <新路徑> -b <新分支名稱>
   ```

### 3. 切換與沙盒開發
1. **主動告知使用者**：「*為了保護您的原始程式碼，我已為您開啟了實體隔離的 Worktree 沙盒：`<新路徑>`。接下來所有的修改與測試都將在此安全區進行。*」
2. 將所有後續的工具呼叫、程式碼讀寫、測試指令的 `Cwd`（工作目錄）切換至 `<新路徑>`。
3. 在此沙盒中完成所有使用者交辦的修改任務。

### 4. 任務驗證與收尾 (Acceptance & Cleanup)
當修改完成且測試無誤，並獲得使用者的確認後，執行收尾流程：
1. **若修改成功且滿意**：
   - 在 Worktree 目錄中執行 `git add .` 與 `git commit`。
   - 回到「原始專案目錄」，將該新分支合併回主分支：`git merge <新分支名稱>`。
2. **清理沙盒**：
   - 無論修改是否被採用，只要任務告一段落，回到「原始專案目錄」執行清理：
     ```bash
     git worktree remove <新路徑>
     git branch -d <新分支名稱>  # 視情況決定是否刪除該分支
     ```
   - 此操作會將實體沙盒資料夾安全移除，並保持原始環境乾淨。
