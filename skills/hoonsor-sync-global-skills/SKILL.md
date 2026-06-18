---
name: hoonsor-sync-global-skills
description: 協助將全域設定與技能自動備份並雙向同步至指定的 GitHub 倉庫 (https://github.com/hoonsor/Antigravity-Setting-and-Skills)，並在同步時自動過濾敏感金鑰。
---

# Sync Antigravity Settings and Skills (同步全域設定與技能)

這個技能專門用於備份與同步你所有的全域設定（如權限許可 `config.json`、外掛模組 `plugins/`）與全域技能（`skills/`）至遠端 GitHub 倉庫，以便在其他裝置上輕鬆進行設定同步與復原，同時透過 `.gitignore` 排除本機特定專案的 UUID 路徑設定 (`projects/`)。

## 觸發條件 (Trigger)
當使用者輸入「#同步」、要求「同步技能」、「備份設定」、「推送到遠端技能庫」，或者直接提到要將全域設定與技能推送到 GitHub (如 `hoonsor/Antigravity-Setting-and-Skills`) 時，請觸發此技能。

## 執行步驟 (Execution Steps)

當觸發此技能時，請依序執行以下步驟：

1. **執行同步 PowerShell 腳本**：
   為了保障資料一致性並避免手動執行指令產生錯誤，請使用 `run_command` 直接執行內建的 PowerShell 自動同步腳本。
   
   請執行以下指令：
   ```powershell
   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.gemini\config\skills\hoonsor-sync-global-skills\sync.ps1"
   ```

2. **確認腳本輸出日誌**：
   - 確認 `mcp_config.json` 的金鑰是否已成功被遮蔽，並生成 `mcp_config.json.template`。
   - 確認外部全域設定（如 `gemini.md` 和錯誤學習庫）已成功備份至 `config/_meta_backups/`。
   - 確認 Git 操作（Pull Rebase、Commit 與 Push）皆順利完成且無報錯。

3. **回報使用者**：
   執行完畢後，向使用者確認同步結果。明確告知拉取了哪些遠端更新（若有），或是推送了哪些本地變更。提醒使用者此機制已自動排除敏感金鑰並遮蔽個人路徑，同時將本地端與雲端保持最新狀態。

## 注意事項
- 執行 Push 時可能會遇到需要授權認證 (Credentials) 的狀況，如果遇到權限錯誤，須引導使用者確認是否有正確設定 GitHub SSH key 或登入 GitHub 的 Credential Manager。
- `mcp_config.json` 包含敏感的 `GITHUB_PERSONAL_ACCESS_TOKEN`，因此已被 `.gitignore` 排除。若在新電腦上使用，請複製 `mcp_config.json.template` 為 `mcp_config.json` 並手動填入自己的 Token。
- 本機專用專案路徑設定資料夾 `projects/` 亦已被 `.gitignore` 排除，避免造成跨電腦路徑錯亂。
