---
name: hoonsor-update-all-projects
description: 當使用者說「#全更新」或要求檢查/更新所有電腦登記的專案時載入此技能。會自動遍歷登記的專案，若設定有遠端 Git 倉庫則比對一致性，若不一致自動執行 pull --rebase 智慧合併，最後彙總狀態報告。
---

# #全更新 (Update All Projects)

此技能用於一鍵檢查並同步目前電腦在 AntiGravity (`~/.gemini/config/projects/*.json`) 中登記的所有專案。

## 觸發指令
* `#全更新`
* 「更新所有專案」、「全更新」

## 核心行為規則
1. 讀取 `C:\Users\hoonsor\.gemini\config\projects\` 目錄下的所有專案配置檔。
2. 針對每一個專案路徑檢測：
   - 是否存在以及是否為 Git 倉庫。
   - 是否有設定遠端倉庫（有 remote 才執行遠端同步檢測，若無則略過）。
3. 比對遠端追蹤分支與本地分支：
   - 先在背景執行 `git fetch --all --prune`。
   - 若本地 HEAD 與遠端一致，標記為「已是最新」。
   - 若本地與遠端不一致，採用智慧合併 `git pull --rebase`，將遠端更新與本地重疊。
4. 最終以清晰的表格形式輸出所有登記專案的同步檢測與合併報告。

## 執行指令
當觸發此技能時，請直接以 `run_command` 執行以下 PowerShell 自動化腳本：
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.gemini\config\skills\hoonsor-update-all-projects\update_all_projects.ps1"
```
執行完成後，將輸出表格與結果整理清楚呈現給使用者。
