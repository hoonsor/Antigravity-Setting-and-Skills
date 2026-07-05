# ⚡ 常見錯誤速查表

> **用途**: 遇到錯誤時的第一手速查。按錯誤訊息關鍵字索引。
> **使用方式**: 用 `Ctrl+F` 搜尋錯誤訊息中的關鍵字。

---

## Windows 環境

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| `UnicodeEncodeError` / `cp950` | `$env:PYTHONIOENCODING="utf-8"` | #1 |
| `無法辨識` / `is not recognized` | 用完整絕對路徑執行指令 | #4 |
| `PermissionError` / `AccessDenied` | 以管理員權限執行，或檢查檔案鎖定 | — |
| `cp65001` / `chcp` | 終端設定 `chcp 65001` 或用 `$env:PYTHONIOENCODING` | #1 |
| `&&` 語法無效 | 使用 `;` 取代 `&&` 串接 PowerShell 命令 | #5 |
| `grep` / `executable file not found` | 改用 `grep_search` API 工具 | #5 |

## Python 依賴

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| `ModuleNotFoundError` | 直接用 `.venv\Scripts\pip.exe install <pkg>` | #3 |
| `No module named 'patchright'` | `pip install patchright` (在正確的 venv 中) | #3 |
| `pip` / `版本衝突` | `pip install --force-reinstall <pkg>==<version>` | #3 |
| `Export ... doesn't exist` | 檢查套件版本匯出名稱，或改用其他通用元件/圖示 | #7 |

## 瀏覽器自動化

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| `query_selector` 返回 `None` | 改用 `page.inner_text('body')` 文字解析 | #2 |
| `TimeoutError` / `wait_for_selector` | SPA 頁面不要等 selector，等 `networkidle` 後用文字解析 | #2 |
| `Navigation timeout` | 增加 `timeout` 參數，加 `time.sleep()` | #2 |
| `ERR_CONNECTION_REFUSED` | 確認 Chrome profile 路徑正確，無其他 Chrome 實例佔用 | — |

## MCP 伺服器

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| MCP 指令找不到 | 不用 CLI，直接用 Python 腳本或完整路徑 | #4 |
| MCP 啟動後無回應 | 檢查 `mcp_config.json` 中的 command 是否匹配實際入口 | #4 |
| MCP 連接超時 | 重啟 MCP 伺服器，確認 port 未被佔用 | — |

## Git / 部署 / 專案同步

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| `PrismaClient` / 連線耗盡 | 使用 singleton 模式（參考 ai-pro-hub 專案） | — |
| `Internal Server Error` (Vercel) | 檢查 API route 是否有未處理的 async 錯誤 | — |
| `DEPLOYMENT_FAILED` | 查看 Vercel Function logs 而非 Build logs | — |
| `冷凍技能數量顯示 0 / 掃描跳過` | 檢查目錄深度是否為多層級（如 `_Skill_Vault`），改用兩層深度遍歷 | #8 |
| `同步資料後網頁無頁籤或無新欄位` | 檢查前端 React 組件與 Hook 是否已同步編寫對應的渲染與資料讀取邏輯 | #9 |
| `dotenv/config` / `worktree` | 全新 worktree 目錄下需先執行 `npm install` (或使用鏡像源) 以還原依賴套件 | #10 |

## React / 前端

| 錯誤關鍵字 | 正確解法 | 教訓 # |
|-----------|---------|:-----:|
| `duplicate key` | 將 React 迴圈中的 key 屬性改為唯一的欄位值（如 `kw.trigger`） | #11 |
| `hydration mismatch` / `bis_register` | 同步在 `<html>` 與 `<body>` 上加上 `suppressHydrationWarning` 屬性 | #12 |

---

## 🔑 黃金法則

1. **Windows + Python = 先設 `PYTHONIOENCODING=utf-8`**
2. **SPA 頁面 = 先用 `inner_text()`，不用 selector**
3. **ModuleNotFoundError = 直接 pip install，不依賴 wrapper**
4. **MCP 不通 = 用完整路徑，不依賴 PATH**
5. **嘗試 2 次失敗 = 換方向，不要盲目重試**
