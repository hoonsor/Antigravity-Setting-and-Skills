# Antigravity-Setting-and-Skills

> **版本號：** `v1.6.4`
> **最後更新：** 2026-06-18
> **GitHub：** [https://github.com/hoonsor/Antigravity-Setting-and-Skills](https://github.com/hoonsor/Antigravity-Setting-and-Skills)

---

## 📖 專案程式功能概述

此倉庫儲存與管理 Antigravity AI 代理的所有「全域設定與技能 (Antigravity Settings and Skills)」。包含全域權限許可 (`config.json`)、外掛模組 (`plugins/`)、自動化腳本、人機指南、測試工具與各種領域的專業知識，供 AI 協作時動態調用與執行。

---

## 📋 版本歷程及功能改變紀錄

| 版本 | 日期 | 類型 | 變更說明 |
|------|------|------|----------|
| v1.6.4 | 2026-06-18 | fix | 重構同步腳本、技能引導與還原指南中的硬編碼路徑，改用動態環境變數以支援異機還原無縫運作 |
| v1.6.3 | 2026-06-16 | feat | 修改 05-workflow 技能中 `#初始化` 流程，支援已存在 Git 設定且曾上傳/未上傳的偵測、Vercel 部署詢問及新遠端庫建立之互動分流 |
| v1.6.2 | 2026-06-16 | feat(pref) | 透過 `#喜好` 指令自動擷取對話紀錄，補充「詳盡功能閉環」、「編輯器進階要求」、「資料顯示細節」等開發規範至 `PREFERENCES.md` |
| v1.6.1 | 2026-06-16 | feat | 透過 `#喜好` 指令自動擷取對話紀錄，新增「功能開發與模塊完整度」等偏好設定至 `PREFERENCES.md` |
| v1.6.0 | 2026-06-16 | feat | 新增 `hoonsor-preferences` 技能的 `#喜好` 指令，支持自動擷取對話紀錄中的使用者偏好並寫入資料庫 |
| v1.5.2 | 2026-06-16 | fix | 修復 `scan_projects.py` 掃描器在讀取 ANSI/CP950 編碼的專案狀態文件時發生的解碼崩潰問題 |
| v1.5.1 | 2026-06-16 | docs | 建立 `ANTIGRAVITY.md` 架構引導指南文件，以符合全域專案架觀規範 |
| v1.5.0 | 2026-06-16 | feat | 新增 `hoonsor-preferences` 使用者個人偏好與創作風格全域技能，用於在任務交辦時記錄與參考使用者偏好 |
| v1.4.0 | 2026-06-14 | feat | 重構備份範圍至整個 config 目錄，新增自動遮蔽金鑰與本機特定路徑排除機制 |
| v1.3.1 | 2026-06-13 | chore | 同步全域設定（gemini.md）及 hoonsor-error-learning 錯誤學習最新備份檔 |
| v1.3.0 | 2026-06-13 | refactor | 建立 Skill Vault 冷儲存區，將 1061 個備用技能移出核心目錄，優化系統上下文載入效能 |
| v1.2.0 | 2026-06-13 | feat | 安裝 AntiGravity 懶人包核心指南與 7 個關聯技能包 |
| v1.1.0 | 2026-06-08 | feat | 新增 agent-reach 全域技能，修復 Hatchling 打包 Bug，本地安裝並同步監控網站 |
| v1.0.0 | 2026-06-07 | feat | 執行全域技能清理（保留遊戲開發引擎相關技能，刪除 74 個無用技能），並初始化 PROJECT_STATUS.md 與 README.md |

---

## 🎯 目前專案進度進展狀態

### 主要任務

- [x] 重構同步腳本、技能引導與還原指南中的硬編碼路徑，改用動態環境變數以支援異機還原無縫運作 (v1.6.4)
- [x] 透過 `#喜好` 自動擷取並更新 `PREFERENCES.md` 的功能完整度偏好 (v1.6.1)
- [x] 建立並實現 `hoonsor-preferences` 的 `#喜好` 專屬指令 (v1.6.0)
- [x] 建立 `ANTIGRAVITY.md` 架構引導指南文件 (v1.5.1)
- [x] 建立 `hoonsor-preferences` 使用者個人偏好與創作風格全域技能 (v1.5.0)
- [x] 執行技能冷儲存清理作業，將非核心技能搬移至 `_Skill_Vault` 分類目錄
- [x] 執行全域技能清理，移除 74 個無用目錄
- [x] 初始化 `PROJECT_STATUS.md` 與 `README.md`
- [x] 推送變更至 GitHub 倉庫 `hoonsor/global-skills`
- [x] 安裝 AntiGravity 懶人包核心文件與 7 個關聯技能包 (v1.2.0)
- [x] 備份並雙向同步本地全域設定與 hoonsor-error-learning 錯誤學習庫 (v1.3.1)
- [x] 備份範圍擴展至整個 config 資料夾，實作金鑰安全過濾與 projects/ 排除機制 (v1.4.0)

### 次要任務

- [x] 切換 GitHub 帳號至 `hoonsor` 以取得權限

---

## 📝 歷次修訂紀錄

### 當前方向

- 清理冗餘全域技能，建立冷儲存區，目前核心目錄僅保留約 60 個高頻次專案技能。

### 歷史修訂

> [!NOTE]
> **已棄用方向 (2026-06-13)**
> ~~清理冗餘全域技能，保留 1329 個核心技能與遊戲引擎技能。~~
> **棄用原因：** 技能數量過多導致 Token 嚴重超載並被截斷，改為設立 `_Skill_Vault` 冷儲存機制。
