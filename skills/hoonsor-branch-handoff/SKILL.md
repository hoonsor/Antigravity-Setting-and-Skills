---
name: hoonsor-branch-handoff
description: 使用者輸入「#分支接手」，或說要把進行到一半的專案交給另一個 AI（Codex、Antigravity、DeepSeek Harness、Claude 等）接續時使用。建立 Git 交接分支與獨立 worktree 資料夾，複製未提交變更與重要的被忽略檔（不含套件環境），並寫出詳盡的交接文件與功能矩陣，供其他 AI 直接開新專案接手，之後可用「#分支比較」評比。
---

# #分支接手：建立交接分支與交接文件

目的：把目前專案「原封不動」地分出一份到獨立資料夾，附上讓陌生 AI 也能無縫接手的交接文件。主幹（原資料夾與原分支）**完全不被修改**，唯一例外是在原專案 `.handoffs/` 留一份交接文件備份（已用 `.git/info/exclude` 排除，不會進版控）。

全程繁體中文。本技能可在 Claude、Codex、Antigravity、DeepSeek Harness 等任何能執行 shell 的 AI 工具使用。

## 0. 找到輔助腳本

`handoff_prepare.py`（僅用 Python 標準函式庫）依序找：
1. 本 SKILL.md 同層的 `scripts/handoff_prepare.py`
2. `~/.agents/skills/hoonsor-branch-handoff/scripts/handoff_prepare.py`
3. `~/.claude/skills/hoonsor-branch-handoff/scripts/handoff_prepare.py`

Windows 用 `python` 或 `py -3` 執行。腳本都找不到時，改用本文件「附錄：無腳本手動流程」的 git 指令，結果相同。

若你在雲端環境、專案在使用者電腦上：用可以在使用者電腦執行指令的工具（例如 device_bash）跑腳本；沒有這種工具就告訴使用者此環境無法操作他的 Git，請在本機的 AI 工具執行本技能。

## 1. 收集必要資訊（一次問完，有預設就不要多問）

| 項目 | 預設 | 何時一定要問 |
|------|------|-------------|
| 專案路徑 | 目前工作資料夾 | 找不到 Git 根目錄或有多個候選 |
| 接手的 AI（target） | 無 | **一定要問**：codex / antigravity / dsh / claude / 其他；用於分支命名與文件 |
| 交出者（source-agent） | 你自己的「應用程式 / 模型」，例如 `Claude / Opus 5.5` | 不確定自己模型名稱時照實寫應用程式名 |
| 是否複製未提交變更 | 是 | — |
| 分支名 / worktree 位置 | `handoff/<target>-<YYYYMMDD-HHmm>`，`<專案上層>\<專案名>_worktrees\handoff-<...>` | 使用者有指定時 |

**多模型比賽模式**：使用者要讓多個 AI 各自接手做比較時，建議每個 AI 各開一條交接分支（包含 Claude 自己若要繼續做），主幹保持凍結，這樣 #分支比較 才公平。逐一對每個 target 執行步驟 2–6。

## 2. 盤點（不改任何東西）

```bash
python handoff_prepare.py plan --project "<專案路徑>" --target <target>
```

讀 JSON 結果並處理：
- `is_git: false` → 問使用者是否 `git init` 並建立初始 commit（`.gitignore` 先確認有排除 node_modules、.venv、.env.keys 等）。同意才做。
- `has_commits: false` → 問使用者是否在主幹做初始 commit。
- `warnings` 全部轉述給使用者。
- `ignored` 分類：
  - `suggest`（dotenvx 加密的 .env、.env.example）→ 預設帶入
  - `confirm`（明文 .env、>50MB 項目）→ 必須逐項取得同意
  - `review`（本機設定、資料檔、筆記、AI 工具設定如 `.claude/settings.local.json`）→ 列給使用者勾選；判斷原則：**接手者若沒有它就無法執行或會失去上下文**才建議帶
  - `secret`（.env.keys、*.pem、credentials*.json…）→ 永不複製，只告知
  - `exclude`（node_modules、venv、dist、快取、log）→ 不複製，只回報數量

把「將建立的分支、worktree 路徑、要複製的未提交檔案數、要帶的被忽略項目」整理成一張表給使用者確認。**得到確認後**才進入下一步。

## 3. 建立 worktree 與骨架

```bash
python handoff_prepare.py create --project "<專案路徑>" --target <target> \
  --source-agent "<應用程式 / 模型>" --include-suggested [--include "<相對路徑>" ...]
```

腳本會：
- `git worktree add -b <分支> <路徑> HEAD`（從目前 commit 分出）
- 把主幹工作目錄中「已修改／新增／未追蹤」檔案複製過去、刪除的檔案同步刪除 → 分支內容 = 交接當下的真實狀態
- 複製你指定的被忽略檔（拒絕金鑰類）
- 建立 `.handoff/BASELINE.json`（機器可讀的基準資料）與 4 份待填文件
- 在 `AGENTS.md`（Codex、DeepSeek Harness 等讀取）、`CLAUDE.md`（Claude）、`GEMINI.md`（Antigravity／Gemini）最上方插入「交接分支說明」區塊（以 `<!-- HANDOFF:BEGIN -->` 標記，合併前可自動移除）

## 4. 撰寫交接文件（本技能最重要的一步）

依 `references/templates.md` 撰寫 worktree 內的：
1. `.handoff/HANDOFF.md` — 完整開發過程與進度（16 節，越詳細越好）
2. `.handoff/FEATURES.md` — 功能矩陣，**格式要保持可解析**（#分支比較 會直接讀）
3. `.handoff/PROGRESS_LOG.md` — 第一筆紀錄由你寫
4. `.handoff/NEXT_AGENT_PROMPT.md` — 給使用者貼到新 AI 的開場指令（填入實際分支名與 target）

資訊來源與查證：
- 對話上下文：使用者需求、限制、偏好、決策過程（摘要但保留原意，重要的話保留原話）
- 實際執行取得，不要憑印象：`git log --oneline -30`、`git status`、`git diff --stat`、執行環境版本（`python --version`、`node -v` 等）、套件清單、測試指令與**目前測試結果**
- 讀專案既有文件：README、PROJECT_STATUS.md、ANTIGRAVITY.md、PRD、TODO
- 程式碼：進入點、主要模組；「進行中」的部分要讀實際程式碼寫出精確位置

同時補齊 `.handoff/BASELINE.json` 的 `commands`（install/run/test/build/lint，用實際可執行的指令）與 `ports`。不要改其他欄位。

自我檢查（全部通過才繼續）：
- 一個從沒看過對話的 AI 只讀 HANDOFF.md 能否說出：目標、做到哪、下一步做什麼、怎麼跑起來、怎麼驗收？
- FEATURES.md 每一列都有客觀驗收標準？狀態與實際測試結果一致？
- 文件中沒有任何金鑰、密碼、token 的值？

## 5. 快照 commit

把要執行的指令列給使用者看並取得同意（使用者規範：commit 前一定先問），然後：

```bash
python handoff_prepare.py finalize --worktree "<worktree 路徑>"
```

腳本會在交接分支上 `git add -A && git commit`（訊息含 `Agent:` trailer），並把 `.handoff/` 備份到原專案 `.handoffs/<分支名>/`（供 #分支比較 省 token 使用）。**不 push**；使用者要求才 push 交接分支（絕不 push 到 main）。

## 6. 回報

用簡短表格回報：
- 分支名稱、worktree 完整路徑（使用者要拿去給其他 AI 開新專案的資料夾）
- 基準 commit、複製的未提交檔案數、帶入／刻意排除的被忽略檔
- 接手者需要自行準備的事（安裝套件、登入 CLI、dotenvx 金鑰環境變數）
- 把 `NEXT_AGENT_PROMPT.md` 的開場指令貼在回覆中，方便使用者直接複製
- 提醒：各 AI 做完後，在原專案輸入「#分支比較」即可評比

各工具開啟方式提示：Codex → 在該資料夾開新 session（`codex` 或 IDE 開資料夾）；Antigravity → Open Folder 選該資料夾；DeepSeek Harness → 在該資料夾啟動 dsh；Claude → 以該資料夾開新專案或新工作。

## 注意事項

- 不修改主幹的任何追蹤檔案，不切換主幹分支，不 stash。
- 同一專案已存在 handoff 分支時，用新的時間戳或 `--name` 避免撞名。
- 若專案使用 Git LFS、submodule：worktree 建立後提醒接手者在新資料夾執行 `git lfs pull` / `git submodule update --init --recursive`，並寫入 HANDOFF.md 第 9 節。
- 若專案路徑含空白或中文，所有路徑都加雙引號。
- 使用者若要放棄某條交接分支：`git worktree remove "<路徑>"` 再 `git branch -D <分支>`（先確認）。

## 附錄：無腳本手動流程

```bash
cd "<專案>"
git status --porcelain                        # 記錄未提交變更
git worktree add -b handoff/<target>-<時間> "<專案>_worktrees/handoff-<target>-<時間>" HEAD
# 把 git status 中的 M/A/?? 檔案逐一複製到新資料夾相同路徑；D 的檔案在新資料夾刪除
# 依需要複製被忽略的重要檔（加密 .env 等），絕不複製 .env.keys / 金鑰
# 在新資料夾建立 .handoff/ 四份文件 + BASELINE.json（欄位同腳本：base_commit、handoff_branch、source_agent、target_agent、commands…）
# 在 AGENTS.md / CLAUDE.md / GEMINI.md 最上方加入 <!-- HANDOFF:BEGIN --> ... <!-- HANDOFF:END --> 區塊
cd "<新資料夾>" && git add -A && git commit -m "chore(handoff): 交接快照" -m "Agent: <你>"
# 把 .handoff/ 複製到 "<專案>/.handoffs/handoff__<target>-<時間>/"，並在 .git/info/exclude 加入 /.handoffs/
```
