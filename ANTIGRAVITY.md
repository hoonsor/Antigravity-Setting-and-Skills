# ANTIGravity 架構引導指南 (ANTIGRAVITY.md)

本文件定義了 `Antigravity-Setting-and-Skills` 專案的架構、技術細節與代理人協作規範，旨在讓所有 Antigravity AI 協作代理人能快速理解本專案，並確保開發標準的一致性。

---

## 🏗️ 專案技術棧與定位

本專案為 Antigravity AI 代理的**全域環境設定與自訂技能管理中心**，負責備份、同步與分發全域配置。

*   **技術定位**：設定備份與工具集成倉庫 (Configuration & Tooling Repository)。
*   **核心配置**：
    *   `config.json` — 全域系統權限許可與功能配置。
    *   `mcp_config.json.template` — 遮蔽個人金鑰後的 MCP 伺服器配置模板。
*   **外掛與擴充**：
    *   `plugins/` — 載入的擴充外掛套件（包含 Android CLI、Chrome DevTools、Firebase、Google Antigravity SDK 等）。
*   **技能中心**：
    *   `skills/` — 核心技能存放區，AI 可動態載入的 YAML/Markdown 動作指南。

---

## 📁 專案目錄結構說明

```text
c:\Users\hoonsor\.gemini\config\ (Git 倉庫根目錄)
 ├── .git/                        # Git 追蹤目錄
 ├── _meta_backups/               # 同步腳本備份的外部設定 (gemini.md 與 error-learning)
 ├── plugins/                     # AI 代理外掛套件定義
 │    ├── android-cli-plugin/     # Android CLI 工具外掛
 │    ├── chrome-devtools-plugin/ # Chrome DevTools 自動化外掛
 │    ├── firebase/               # Firebase 連接外掛
 │    └── google-antigravity-sdk/ # Google Antigravity SDK 核心外掛
 ├── skills/                      # 全域自訂技能目錄
 │    ├── 00-install-all/         # 一鍵安裝所有技能
 │    ├── hoonsor-preferences/    # 使用者個人偏好與創作風格技能 (v1.5.0 新增)
 │    ├── hoonsor-sync-global-skills/ # 本專案的核心備份同步技能與腳本
 │    └── ...                     # 其他約 60 個高頻核心技能
 ├── config.json                  # 全域權限許可 (Permission Grants)
 ├── mcp_config.json.template     # 已遮蔽金鑰之 MCP 伺服器設定模板
 ├── .gitignore                   # 排除個人隱私與本機路徑 (如 projects/)
 ├── ANTIGRAVITY.md               # 本架構引導指南 (本檔案)
 ├── PROJECT_STATUS.md            # 專案進度與版本歷程 (SemVer 規範)
 └── README.md                    # 專案說明與復原手冊
```

---

## ⚙️ 代理人協作與安全規範 (Always Do / Never Do)

### 🟢 永遠遵守 (Always Do)
1.  **語言限制**：所有對話與回覆必須**始終使用繁體中文**。
2.  **語意化版本 (SemVer)**：每次修改或發佈均需升級版本號（遵循 `vX.Y.Z` 規範），並更新 `PROJECT_STATUS.md` 中的版本歷程。
3.  **金鑰安全過濾**：在進行備份與同步前，必須確保 `mcp_config.json` 中的敏感 Token (如 `GITHUB_PERSONAL_ACCESS_TOKEN`) 已被過濾遮蔽，僅將安全模板 `mcp_config.json.template` 提交至 Git。
4.  **防錯檢索**：在進行任何高風險變更前，主動檢查 `hoonsor-error-learning` 中的 `quick_fixes.md`。

### 🔴 嚴禁執行 (Never Do)
1.  **嚴禁提交敏感私鑰**：絕對不能將含有真實 API Key、個人 Token 的 `mcp_config.json` 提交至 Git。
2.  **嚴禁提交 projects/ 目錄**：`.gemini\config\projects\` 內含本機特定專案的絕對實體路徑，必須維持在 `.gitignore` 排除名單中，嚴禁提交。
3.  **嚴禁隨機 Git Commit 雜湊版本**：所有變更在 `PROJECT_STATUS.md` 中必須對應明確的 SemVer 版本號，不可使用隨機產生的 hash 標示版本。

---
*Generated and maintained by Google Antigravity Architect*
