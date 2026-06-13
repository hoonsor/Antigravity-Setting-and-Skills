# global-skills

> 專案存放 Antigravity AI 代理的所有全域自訂技能與工作流。

## 📖 專案簡介 (Overview)

本專案是用於儲存與管理 Google Antigravity AI 代理之「全域技能 (Global Skills)」的核心倉庫。這些技能提供了 AI 代理在面對複雜的程式開發、系統自動化、測試與除錯等任務時所需的重要能力。

### 為何需要此專案？
在與 AI 進行程式設計或自動化協作時，AI 往往缺乏與本地特定系統相匹配的私有化工具與領域知識。本專案透過結構化的 `.md` 說明文件、輔助腳本與模板，將各種常用的開發模式（如 React 19 Best Practices、Zustand Store 建立等）和自動化任務（如專案狀態掃描、Git 自動化推送等）封裝為「全域技能」。這使得 AI 能夠在不同專案的 Session 中隨時調用這些技能，實現「越用越聰明」與「無縫協作」的核心目標。

### 核心價值
相比於每次對話都要重新解釋開發規範或手動編寫腳本，本專案提供了一個集中的技能中心，有效減輕了 AI 代理的 context 負載。同時，透過定期清理無用、冗餘的技能（如其他語言或非本國特定的自動化工具），我們得以下降系統負擔，確保 AI 代理在調用工具時精準無誤，最大化提升全 swarm 協作的效率。

---

## ✨ 核心功能 (Key Features)

- **全域技能架構**：整合了上千個 AI 自訂技能，為前端、後端、自動化等各領域提供即時的技術手冊與 SOP 指引。
- **專案狀態自動監控 (Project Monitor)**：透過內部腳本實時監控所有子專案的進度與變更歷程，並自動同步至專案狀態呈現網站。
- **Git 自動推送助手**：在代碼變更完成後，自動更新 README 文件，並提供語義化的 Commit 提交與遠端推送。
- **AntiGravity 專屬懶人包**：一鍵整合 NotebookLM MCP、Firebase MCP、GitHub CLI、Obsidian MCP (MCPVault)、生圖指引與開工/收工/專案初始化流程，極大簡化開發環境配置。

---

## 🛠 技術棧 (Tech Stack)

- **核心架構**：Google Antigravity (AGY) SDK, Model Context Protocol (MCP)
- **腳本語言**：Python 3.8+, PowerShell, Bash Shell
- **資料交換**：JSON, Markdown
- **版本控制**：Git, Conventional Commits

---

## 🚀 快速開始 (Quick Start)

### 環境要求
- Windows (推薦使用 PowerShell) 或 Linux/macOS
- Git CLI 已安裝且配置 SSH/HTTPS 權限
- 已安裝 Python 3.8+

### 安裝與運行

```bash
# 1. 複製此全域技能倉庫至您的 .gemini 設定目錄
git clone https://github.com/hoonsor/global-skills.git C:\Users\hoonsor\.gemini\config\skills

# 2. 執行全域專案監控同步腳本 (以 Windows 為例)
python C:\Users\hoonsor\.gemini\config\skills\hoonsor-project-monitor\scripts\sync_to_website.py
```

---

## 📁 專案結構 (Project Structure)

```text
skills/
 ├── 00-install-all/              # 一次安裝全部懶人包技能
 ├── 01-notebooklm/               # 連接 NotebookLM MCP 技能
 ├── 02-github/                   # 連接 GitHub CLI 技能
 ├── 03-firebase/                 # 連接 Firebase MCP 技能
 ├── 04-draw/                     # 生圖指引技能
 ├── 05-workflow/                 # 開工/收工/專案初始化流程技能
 ├── 06-obsidian/                 # 連接 Obsidian MCP (MCPVault) 技能
 ├── 09-AntiGravity專屬懶人包.md  # AntiGravity 懶人包核心指引文件
 ├── ab-test-setup/               # A/B 測試設置技能
 ├── hoonsor-project-monitor/     # 專案狀態監控與同步模組
 ├── hoonsor-git-push-assistant/  # Git 推送與 README 自動化助手
 ├── ...                          # 其他 1300+ 全域技能
 └── PROJECT_STATUS.md            # 本專案的進度與狀態追蹤
```

---

## 🔄 最新更新 (Recent Updates)

### v1.2.0 (2026-06-13)
- 安裝 AntiGravity 專屬懶人包核心指引文件及 7 個關聯的懶人包技能。
- 清除先前於 D 槽誤裝的檔案並完成正確的 C 槽本地安裝與 Git 推送。

### v1.1.0 (2026-06-08)
- 新增 `agent-reach` 全域技能，修復 Hatchling 打包 Bug，本地安裝並同步監控網站。

### v1.0.0 (2026-06-07)
- 執行全域技能清理（保留遊戲開發引擎相關技能，刪除 74 個冗餘無用技能）。
- 初始化 `PROJECT_STATUS.md` 與 `README.md`。

---
*Generated and maintained by Google Antigravity Architect*
