# 🧠 錯誤教訓知識庫

> **用途**: Agent 遇到錯誤時，先查閱此索引，命中已知教訓則直接使用正確解法。
> **規則**: 只追加不刪除。每次呼叫 `hoonsor-error-learning` 技能後更新。

---

## 📑 教訓索引

| # | 標題 | 分類 | 等級 | 浪費模式 | 預估浪費 | 日期 |
|---|------|------|------|---------|---------|------|
| 1 | Windows CP950 編碼崩潰 | 環境 | 🔴 | TW-04 | ~6,000 | 2026-04-22 |
| 2 | Angular SPA Selector 地獄 | 前端 | 🔴 | TW-07, TW-02 | ~30,000 | 2026-04-22 |
| 3 | Python venv 依賴不完整 | 依賴 | 🟡 | TW-06 | ~4,000 | 2026-04-22 |
| 4 | MCP 伺服器指令衝突 | 配置 | 🟡 | TW-06 | ~5,000 | 2026-04-22 |
| 5 | PowerShell 語法不相容 | 環境 | 🟡 | TW-04 | ~6,000 | 2026-06-13 |
| 6 | ArtifactMetadata 參數誤用 | API | 🟢 | — | ~3,000 | 2026-06-13 |
| 7 | lucide-react 圖示匯出遺失 | 依賴 | 🟡 | — | ~5,000 | 2026-06-13 |
| 8 | 技能掃描器忽視多層目錄 | 邏輯 | 🟡 | TW-04 | ~4,000 | 2026-06-14 |
| 9 | Web 專案僅同步數據未更新 React UI | 前端 | 🟡 | TW-02 | ~6,000 | 2026-06-14 |

---

## 📌 教訓 #1: Windows CP950 編碼崩潰

**錯誤分類**: 環境
**嚴重等級**: 🔴 高頻
**Token 浪費模式**: TW-04（環境假設錯誤）
**預估浪費 Tokens**: ~6,000

### 症狀
```
UnicodeEncodeError: 'cp950' codec can't encode character '\U0001f4da' in position 0: illegal multibyte sequence
```

### 根因分析
Windows 終端預設使用 CP950（Big5）編碼，無法輸出 Emoji 或部分 Unicode 字元。
Python 的 `print()` 會嘗試用 `sys.stdout.encoding`（即 CP950）編碼所有輸出。
任何包含 Emoji、特殊符號的輸出都會觸發此錯誤。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 嘗試修改程式碼移除 Emoji → 治標不治本，新的 Unicode 字元仍會出錯
2. 直接在腳本內設定 `encoding='utf-8'` 但沒有包裝 `sys.stdout` → 無效

### ✅ 正確解法
**方法 A（推薦）**: 執行前設定環境變意
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**方法 B**: 在 Python 腳本最開頭加入
```python
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### 🛡️ 預防措施
- **每次在 Windows 上執行 Python 腳本前，必須設定 `PYTHONIOENCODING=utf-8`**
- 所有新建的 Python 腳本都應在開頭包含方法 B 的防護碼
- 特別注意：`run_command` 工具執行 Python 時，也需要在 CommandLine 前加 `$env:PYTHONIOENCODING="utf-8"; `

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`

---

## 📌 教訓 #2: Angular SPA Selector 地獄

**錯誤分類**: 前端
**嚴重等級**: 🔴 高頻
**Token 浪費模式**: TW-07（Selector 地獄）, TW-02（方向錯誤）
**預估浪費 Tokens**: ~30,000（最大單筆浪費！）

### 症狀
```python
page.query_selector('a[href*="/notebook/"]')  # → None
page.query_selector('[data-notebook-id]')     # → None
page.query_selector('.notebook-card')         # → None
page.query_selector('mat-card')              # → None
# 所有 CSS selector 均返回 None
```

### 根因分析
NotebookLM 使用 Angular 框架，採用深度動態渲染：
- 筆記本 UUID 不出現在 DOM 的 `href` 或 `data-*` 屬性中
- Angular 組件使用影子 DOM 或虛擬 DOM，標準 selector 無法穿透
- 頁面載入後 Angular 還需要額外渲染時間，DOM 結構持續變化
- `_ngcontent-*` 等隨機屬性讓 selector 不可靠

### ❌ 無效嘗試（避免重蹈覆轍）
1. `a[href*="/notebook/"]` → UUID 不在 href 中
2. `[data-notebook-id]` → 不存在此屬性
3. `.notebook-card`, `mat-card` → 類名不存在或動態生成
4. `querySelectorAll('a')` 然後過濾 → href 中沒有 notebook 路徑
5. 等待特定 selector 出現（`wait_for_selector`）→ 永遠不會出現
6. JavaScript 反射 (`__zone_symbol__`)  → 部分成功但不穩定
7. 修改 `client.py` 的 `_list_notebooks_sync` 反覆嘗試不同 selector → 10+ 輪全部失敗
8. 嘗試用 `evaluate()` 注入 JS 讀取 Angular 內部狀態 → 太脆弱

### ✅ 正確解法
**方法 A（最穩定）**: 使用 `page.inner_text('body')` 獲取純文字，然後解析
```python
body_text = page.inner_text('body')
# 從文字中用正則解析筆記本名稱、來源數、日期
```

**方法 B（需要 UUID 時）**: 模擬點擊遍歷
```python
# 1. 取得列表中所有可點擊元素
# 2. 逐一點擊 → 等待導航 → 從 URL 提取 UUID → 返回上一頁
# 3. 重複直到遍歷完成
```

### 🛡️ 預防措施
- **遇到 Angular/React/Vue 等 SPA 框架 of 頁面，第一時間使用 `inner_text('body')` 而非 CSS selector**
- 如果 `inner_text` 不夠，改用 `page.content()` 獲取完整 HTML 後用正則解析
- 絕對不要花超過 2 輪嘗試 CSS selector，如果前兩次失敗就立即切換策略
- 記住：**SPA 框架的 DOM 是動態生成的，selector 策略本質上不可靠**

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`, `a8a8d866-7ee5-4772-9ee5-af7f42e502d9`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`

---

## 📌 教訓 #3: Python venv 依賴不完整

**錯誤分類**: 依賴
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-06（依賴混淆）
**預估浪費 Tokens**: ~4,000

### 症狀
```
ModuleNotFoundError: No module named 'patchright'
```
即使 `.venv` 目錄存在且 `requirements.txt` 列出了 `patchright`。

### 根因分析
`run.py` wrapper 的 `ensure_venv()` 函數只在 venv 目錄不存在時才建立並安裝依賴。
如果 venv 已存在但依賴不完整（例如手動刪除了某個套件，或 requirements.txt 新增了條目），
wrapper 不會自動重新安裝。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 反覆用 `python scripts/run.py ...` 執行 → 不會自動修復依賴
2. 刪除 venv 重建 → 可以慢

### ✅ 正確解法
```powershell
# 直接用 venv 內的 pip 安裝缺失依賴
& "C:\Users\hoonsor\.gemini\antigravity\skills\notebooklm\.venv\Scripts\pip.exe" install patchright
# 或安裝所有依賴
& "C:\Users\hoonsor\.gemini\antigravity\skills\notebooklm\.venv\Scripts\pip.exe" install -r requirements.txt
```

### 🛡️ 預防措施
- 遇到 `ModuleNotFoundError` 時，先用 `pip list` 檢查套件是否在 venv 中
- 不要依賴 wrapper 的自動安裝邏輯
- 安裝後用 `pip show <package>` 確認版本

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22

---

## 📌 教訓 #4: MCP 伺服器指令衝突

**錯誤分類**: 配置
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-06（依賴混淆）
**預估浪費 Tokens**: ~5,000

### 症狀
```
notebooklm-mcp : 無法辨識 'notebooklm-mcp' 這個名稱
```
或 MCP 伺服器啟動後無回應/當機。

### 根因分析
`notebooklm-mcp` pip 套件被卸載後重裝為 `notebooklm-mcp-server`，
但 `mcp_config.json` 中的指令仍指向舊的入口點。
同時，PATH 未包含 Python Scripts 目錄，導致命令列找不到入口。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 反覆卸載重裝 pip 套件 → 入口點名稱不同
2. 修改 `opencode.json` 指向錯誤的指令 → 啟動失敗
3. 嘗試用 `python -m notebooklm_mcp` → 模組結構不支援

### ✅ 正確解法
- 不依賴 MCP CLI，改用 `notebooklm` skill 的 Python 腳本直接執行
- 如果需要 MCP，在配置文件中使用**完整絕對路徑**
- 確認 `mcp_config.json` 中的 `command` 對應實際安裝 of 入口點名稱

### 🛡️ 預防措施
- pip 安裝後立即用 `where <command>` 確認入口點名稱和位置
- MCP 配置一律使用完整路徑，不依賴 PATH
- 維護 `hoonsor-mcp-manager` skill 來集中管理 MCP 伺服器配置

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`

---

## 📌 教訓 #5: PowerShell 語法不相容

**錯誤分類**: 環境
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-04（環境假設錯誤）
**預估浪費 Tokens**: ~6,000

### 症狀
執行含有 `&&` 或是 `grep` 的指令時，PowerShell 拋出語法錯誤：
`無法辨識 '&&' 語法` 或 `exec: "grep": executable file not found in %PATH%`。

### 根因分析
Windows 的 PowerShell 不支援 Linux/Bash 的 `&&` 命令串接語法（除非升級到 PS 7+），且 Windows 預設沒有 `grep` 命令。

### ❌ 無效嘗試
1. 直接在 PowerShell 內執行 `&&` 或 `grep` 串接命令。

### ✅ 正確解法
- **命令串接**: 使用 `;` 取代 `&&`。
- **搜尋文本**: 使用系統專屬的 `grep_search` API 工具，而不是在 command line 手動執行 grep。

### 🛡️ 預防措施
- 在 Windows 終端執行命令時，一律使用 `;` 代替 `&&`。
- 搜尋程式碼時一律使用 `grep_search` 工具，不手動下 grep 命令。

### 📎 關聯
- 對話 ID: `ba1bef9c-2609-4075-b167-e5d8cc7b7c50`
- 日期: 2026-06-13

---

## 📌 教訓 #6: ArtifactMetadata 參數誤用

**錯誤分類**: API
**嚴重等級**: 🟢 輕微
**Token 浪費模式**: 無
**預估浪費 Tokens**: ~3,000

### 症狀
`invalid tool call error (invalid_args) ... is not a valid artifact path; artifacts must be in C:\Users\...`

### 根因分析
呼叫 `write_to_file` 或 `multi_replace_file_content` 時，如果修改的不是位於 `<appDataDir>\brain\<conversation-id>\` 下的 Markdown 報告檔，但帶有 `ArtifactMetadata` 參數，系統會檢驗並拋出無效路徑錯誤。

### ❌ 無效嘗試
1. 建立或修改普通專案代碼檔（如 `src/components/views/SystemView.tsx`）時填寫了 `ArtifactMetadata`。

### ✅ 正確解法
- 建立或修改一般專案代碼檔案時，**不要** 填寫 `ArtifactMetadata` 參數。

### 🛡️ 預防措施
- 編輯一般專案原始碼檔案（如 `.ts`、`.tsx`、`.py`）時，務必將 `ArtifactMetadata` 留空。

### 📎 關聯
- 對話 ID: `ba1bef9c-2609-4075-b167-e5d8cc7b7c50`
- 日期: 2026-06-13

---

## 📌 教訓 #7: lucide-react 圖示匯出遺失

**錯誤分類**: 依賴
**嚴重等級**: 🟡 中等
**Token 浪費模式**: 無
**預估浪費 Tokens**: ~5,000

### 症狀
Next.js / Vercel Build 失敗：
`Export Github doesn't exist in target module`

### 根因分析
在新版本的 `lucide-react` 中，部分 Icon 命名可能不同，或是未包含在預設匯出中。在開發時若未檢查，直接導入不存的圖示，會在 Vercel 構建時觸發嚴重錯誤。

### ❌ 無效嘗試
1. 假設 Vercel 線上環境與本地完全一致，不執行本地 build 測試就推送。

### ✅ 正確解法
- 改用更通用的 Icon，或者改用 SVG 自訂渲染。
- 程式碼推送前，於本地先執行 `npm run build` 或 `tsc --noEmit` 做編譯檢查。

### 🛡️ 預防措施
- 使用第三方圖示庫時，不使用不確定的導出名稱。
- 每次推送 UI 程式碼前，必定在本地執行 build 以檢測依賴與導出完整度。

### 📎 關聯
- 對話 ID: `ba1bef9c-2609-4075-b167-e5d8cc7b7c50`
- 日期: 2026-06-13

---

## 📌 教訓 #8: 技能掃描器忽視多層目錄

**錯誤分類**: 邏輯 / 專案管理
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-04（環境假設錯誤）
**預估浪費 Tokens**: ~4,000

### 症狀
資料同步後，Vercel 監控網站上顯示的「冷凍技能數量」為 0。

### 根因分析
`_Skill_Vault` 資料夾是一個分類容器目錄，其底下的第二層子目錄（例如 `_Skill_Vault/01-Non_Core_Languages/c-pro`）才是真正包含 `SKILL.md` 的技能檔案。原先的 `scan_skills.py` 腳本只掃描了一層技能目錄（即 `skills_dir` 的直接子目錄），因此把這些大類目錄當作普通技能，因無 `SKILL.md` 而直接跳過。

### ❌ 無效嘗試
1. 嘗試不修改程式碼，直接重複執行 `sync_to_website.py` 期待快取生效。

### ✅ 正確解法
- 重構 `scan_skills.py` 的 `scan_all` 函數，在掃描 `_Skill_Vault` 時增加一圈分類目錄的遍歷，實現兩層深度的掃描，並在 `skills_slim.json` 中將它們輸出到獨立的 `frozen_skills` 屬性中。

### 🛡️ 預防措施
- 設計目錄掃描器時，要確認是否含有分類文件夾。
- 掃描後的關鍵輸出（例如項目數）必須做防呆，若結果為 0，應拋出警示或日誌。

### 📎 關聯
- 對話 ID: `9f2855d0-3025-4ba5-930f-90da6b57ff72`
- 日期: 2026-06-14

---

## 📌 教訓 #9: Web 專案僅同步數據未更新 React UI

**錯誤分類**: 前端 / 邏輯
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-02（方向錯誤）
**預估浪費 Tokens**: ~6,000

### 症狀
數據已成功寫入 json 資料源並部署至網站，但網頁重新整理後依然沒有顯示冷凍技能與切換頁籤。

### 根因分析
僅透過後端腳本更新並推送了 `skills_slim.json`，但是前端 React 元件（如 `SkillsView.tsx`）並未設計並編寫讀取、呈現此新欄位的 UI 代碼，導致數據庫有資料但畫面沒有對應元件渲染。

### ❌ 無效嘗試
1. 盲目等待 Vercel 重複部署，或重整瀏覽器快取。

### ✅ 正確解法
- 同步修改 React 前端元件：
  1. 在 `useDashboardData.ts` 中加入對 `frozen_skills` 陣列的 Hook 讀取。
  2. 在 `SkillsView.tsx` 中新增 Tabs 切換按鈕（啟用技能 vs 冷凍技能），在卡片中標示冷凍類別，並串接搜尋與標籤篩選。
  3. 本地執行 `npm run build` 確認構建成功後再 Push。

### 🛡️ 預防措施
- 新增/調整資料庫或 JSON 資料欄位時，必須同時審查前端 UI 呈現是否需對齊。
- 嚴格落實「代碼推送前本地 build」的規範，確保前後端無縫整合。

### 📎 關聯
- 對話 ID: `9f2855d0-3025-4ba5-930f-90da6b57ff72`
- 日期: 2026-06-14
