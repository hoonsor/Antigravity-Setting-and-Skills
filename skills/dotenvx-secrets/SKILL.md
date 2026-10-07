---
name: dotenvx-secrets
description: 倬的所有專案 .env 都已用 dotenvx 加密（全部共用同一組金鑰）。凡是新增或修改環境變數、API key、建立新專案、撰寫或修改讀取 .env 的程式碼、建立啟動腳本或排程，或程式讀到「encrypted:」開頭的值、出現 DECRYPTION_FAILED 時，都必須先使用此技能。使用者說「批次遷移 dotenvx」時，執行本技能的批次遷移流程。
---

# dotenvx 加密環境變數規範

## 現況

- 每個專案的 `.env` 都已加密：第一行是 `DOTENV_PUBLIC_KEY="..."`（所有專案相同），變數值是 `encrypted:...`。
- 解密密碼存在 Windows 使用者環境變數 `DOTENV_PRIVATE_KEY`。
- 共用公鑰（只能加密、不能解密，可以讀）：`%USERPROFILE%\.dotenvx\public.key`
- 私鑰檔（禁止讀取）：`%USERPROFILE%\.dotenvx\.env.keys`
- `.env` 檔本身只有密文，可以正常讀取來查看有哪些變數名稱。

## 安全規則（不可違反）

1. 不讀取、不顯示 `%USERPROFILE%\.dotenvx\.env.keys` 與 `DOTENV_PRIVATE_KEY` 的值，也不把它寫進任何檔案、log 或對話。
2. 不執行會輸出明文的指令：`dotenvx decrypt`、`dotenvx get`、`dotenvx run -- set`／`env`／`printenv`，或任何印出 `os.environ`、`process.env` 全部內容的程式碼。
3. 不建立明文 `.env`，不把 `.env` 還原成明文，不刪除或修改 `DOTENV_PUBLIC_KEY` 那一行。
4. 不對沒有 `DOTENV_PUBLIC_KEY` 行的 `.env` 執行 `dotenvx encrypt` 或 `dotenvx set`，否則會產生第二把金鑰。
5. 專案資料夾內不得出現 `.env.keys`。若發現有，立刻停下來告知使用者，不要刪除也不要使用。
6. 每個 Git 專案的 `.gitignore` 必須包含 `.env.keys`。

## 新增或修改變數

在專案資料夾（`.env` 所在位置）操作：

- **機密值**（API key、token、密碼）：不要讓值經過對話。請使用者自己在終端機執行：
  `dotenvx set 變數名 "值" --no-armor --no-native`
  使用者若已經把機密值貼在對話中，照樣執行，但提醒他之後改用自己執行的方式。
- **非機密值**（PORT、DEBUG、網址）：可以直接執行
  `dotenvx set 變數名 值 --plain --no-armor --no-native`
- **刪除變數**：直接編輯 `.env` 刪掉那一行即可。
- 同步更新 `.env.example`：只列變數名稱，值留空。

## 新專案建立 .env

1. 讀取 `%USERPROFILE%\.dotenvx\public.key` 的內容。
2. 建立 `.env`（UTF-8 無 BOM），第一行寫 `DOTENV_PUBLIC_KEY="<public.key 的內容>"`，接一個空行。
3. 依「新增或修改變數」的方式寫入變數。
4. `.gitignore` 加入 `.env.keys`。
5. 程式讀取方式依下一節設定。

## 程式讀取 .env 的方式

原則：優先在程式碼內解密，這樣 .bat、捷徑、工作排程器、VS Code 偵錯都不用改。

### Python

- 依賴：以 `python-dotenvx` 取代 `python-dotenv`（更新 requirements.txt 或 pyproject.toml，並安裝到專案自己的虛擬環境）。
- 程式進入點最上方：

```python
from pathlib import Path
from dotenvx import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
```

- **必須傳入明確路徑**：python-dotenvx 只從「目前工作目錄」往上找 `.env`，不像 python-dotenv 從程式檔位置找。工作排程器或捷徑啟動時，工作目錄常常不是專案資料夾。進入點不在專案根目錄時，調整 `.parent` 層數。
- **必須 `override=True`**：VS Code／Antigravity 的 Python 擴充套件預設會把 `.env` 的密文先塞進環境變數，不覆寫的話程式會拿到密文。
- `dotenv_values(...)` 改成 `from dotenvx import dotenv_values`，同樣傳明確路徑。
- 其餘地方一律用 `os.getenv()`／`os.environ` 讀取。

### Node.js（程式自己載入 .env）

- 依賴：以 `@dotenvx/dotenvx` 取代 `dotenv`。
- 進入點最上方：

```js
const path = require('path')
require('@dotenvx/dotenvx').config({ path: path.join(__dirname, '.env'), overload: true })
```

ESM 寫法：`import dotenvx from '@dotenvx/dotenvx'` 再呼叫 `dotenvx.config({ ... })`。

### 框架自己載入 .env（Next.js、Vite、Nuxt 等）

框架會直接讀到密文，改成在 package.json scripts 前面加上 dotenvx：

```json
"dev": "dotenvx run -- next dev",
"build": "dotenvx run -- next build",
"start": "dotenvx run -- next start"
```

### 無法修改程式碼的情況（其他語言、第三方工具）

- 啟動指令改成：`dotenvx run -f "<專案絕對路徑>\.env" -- <原本的命令>`
- .bat 檔：先 `cd /d "%~dp0"`，再 `dotenvx run -- <原本的命令>`
- 工作排程器：「程式」填 dotenvx.exe 完整路徑（用 `where.exe dotenvx` 查），「引數」填 `run -f "<專案路徑>\.env" -- "<python.exe 完整路徑>" main.py`，「起始位置」填專案資料夾。

### VS Code／Antigravity 偵錯設定

`.vscode/launch.json` 若有 `"envFile"` 指向 `.env`，刪除該設定（它只會讀到密文）。

## 驗證

- 不可用印出金鑰值的方式驗證。可以印 `bool(os.getenv("X"))`，或確認值不是以 `encrypted:` 開頭。
- 讀到 `encrypted:` 開頭的值：表示沒有解密。檢查是否仍使用舊的 python-dotenv／dotenv、少了 override、或框架直接讀檔。
- 出現 `DECRYPTION_FAILED`：表示 `DOTENV_PRIVATE_KEY` 沒生效。終端機與編輯器要在設定環境變數之後重新開啟；工作排程器的任務需要登出或重新開機一次才讀得到。

## 批次遷移流程

使用者要求批次遷移時（預設根目錄 `D:\01-Project`），依序執行。全程排除 `node_modules`、`.venv`、`venv`、`.git`、`dist`、`build`、`.next`。

1. **盤點**：對每個子專案找出
   - 載入 .env 的程式碼：搜尋 `load_dotenv`、`dotenv_values`、`find_dotenv`、`require('dotenv')`、`require("dotenv")`、`from 'dotenv'`、`dotenv/config`
   - 依賴檔：`requirements*.txt`、`pyproject.toml`、`package.json`
   - 使用的框架（Next.js、Vite、Nuxt 等）
   - 啟動點：`*.bat`、`*.cmd`、`*.ps1`、package.json scripts、`.vscode/launch.json`
   - 工作排程器：執行 `schtasks /query /fo csv /v`，找出「要執行的工作」或「開始位置」在根目錄底下的任務
   - 專案內是否有 `.env.keys`（有的話列為異常）
2. **先回報盤點表**給使用者確認，確認後才開始修改。
3. **修改**：依「程式讀取 .env 的方式」處理。優先改程式碼；改了程式碼的 Python／Node 專案，啟動點與排程不用動。只把依賴裝進專案自己的虛擬環境或 node_modules，不動全域環境。不 commit、不 push。
4. **工作排程器**：只有在無法改程式碼的專案才需要修改。列出建議的新設定，由使用者確認後再修改。
5. **驗證**：有測試就跑測試；沒有的話用 `python -m py_compile` 或 `node --check` 做語法檢查，並確認 `import dotenvx` 能成功。不要直接執行會產生實際動作的程式（發訊息、寄信、下單、寫入資料庫、操作外部服務），改由使用者自行測試。
6. **最後回報**一張表：專案、修改的檔案、啟動方式是否需要變更、需要使用者手動處理的事項。
