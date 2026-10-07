---
name: hoonsor-branch-compare
description: 使用者輸入「#分支比較」，或要比較交接分支（由 Codex、Antigravity、DeepSeek Harness、Claude 等不同 AI 接手的 worktree）與主幹的進度、功能差異與品質，決定要 merge 哪個版本或改為主版時使用。先用腳本收集客觀數據與交接文件以節省 token，再抽查程式碼，產出評分報告與合併建議。
---

# #分支比較：評比各 AI 接手的分支

目的：讓使用者知道「哪個 AI 在這個專案做得比較好」，並決定要 merge 哪個分支、改用哪個為主版，或從多個分支挑功能組合。全程繁體中文。

**省 token 原則**：先讀結構化資料（腳本輸出、`.handoff/FEATURES.md`、`PROGRESS_LOG.md`），只對「狀態不同的功能」與「多分支都改的檔案」抽查 diff；不要整份讀程式碼、不要讀完整 `git diff`。

## 0. 找到輔助腳本

`compare_branches.py` 依序找：本 SKILL.md 同層 `scripts/`、`~/.agents/skills/hoonsor-branch-compare/scripts/`、`~/.claude/skills/hoonsor-branch-compare/scripts/`。範本 `references/report-template.md` 也依同樣順序尋找。Windows 用 `python` 或 `py -3`。找不到時改用文末「附錄：無腳本流程」。

專案在使用者電腦、而你在雲端：用能在使用者電腦執行指令的工具跑腳本；沒有就請使用者改在本機 AI 工具執行。

## 1. 取得要比較的對象

先問使用者（若訊息中已提供就不要問）：
- **主幹資料夾路徑**（原專案）
- **要比較的分支資料夾路徑**（一個或多個；也接受分支名稱）

使用者不確定時，執行：
```bash
python compare_branches.py list --main "<主幹路徑>"
```
列出所有 `handoff/*` 分支、對應 worktree 路徑與最後 commit，讓使用者勾選（預設全選 handoff 分支）。

## 2. 收集客觀數據（腳本，不改任何 Git 狀態）

```bash
python compare_branches.py collect --main "<主幹>" --branch "<分支1路徑>" --branch "<分支2路徑>"
```
產出（預設在 `<主幹>/.handoffs/reports/`）：
- `compare_data_*.json`：每個分支的基準、交接後 commit（含 `Agent:` trailer）、diffstat（已排除交接鷹架）、交接時 vs 現在的功能矩陣、工作紀錄、worktree 未提交變更、與主幹的衝突預測（`git merge-tree`，不動工作目錄）
- `COMPARE_DRAFT_*.md`：上述數據的表格草稿

**跑測試（建議）**：問使用者是否在各 worktree 執行測試（需各自已安裝環境，可能耗時）。同意則加 `--run-tests`（使用 BASELINE.json 的 test 指令）。

讀結果時特別注意：
- `error`：路徑不是本專案的 worktree（例如使用者手動複製資料夾）→ 告知，並改用附錄的檔案層級比較
- `uncommitted_in_worktree` 有內容 → 該 AI 還有沒 commit 的成果，提醒使用者（比較以 commit 為準，必要時請使用者先讓該 AI commit）
- `main.commits_since_base` > 0 → 主幹在交接後也有進展（例如 Claude 在主幹繼續做），把主幹也當成一位參賽者評估（讀主幹自基準後的 commit 與 diffstat）
- 沒有 `.handoff/`（不是 #分支接手 建立的分支）→ 改以 commit 訊息與 diffstat 推估功能，並在報告標註信心較低

## 3. 抽查驗證（有限度地讀程式碼）

依序、適可而止：
1. 讀 `COMPARE_DRAFT_*.md` 與各分支最新 `PROGRESS_LOG` 紀錄。
2. 讀主幹 `.handoffs/<分支>/HANDOFF.md` 的第 0、2、12 節（需求、禁止事項、原定下一步）——作為評分基準，不必整份讀。
3. 對**狀態有差異或標 ✅ 的關鍵功能**：用 `git diff <base>..<分支> -- <相關檔案>` 只看相關檔案，驗證是否真的實作（自稱完成 ≠ 完成）。
4. 對 `overlap_files`（多分支都改的檔案）：比較做法差異。
5. 測試結果有失敗時，看失敗訊息判斷嚴重度。

每個分支的抽查以約 5 個檔案為上限；超過時優先看與使用者核心需求相關者。

## 4. 撰寫報告

依 `references/report-template.md` 寫 `<主幹>/.handoffs/reports/BRANCH_COMPARE_<時間>.md`：
- 先給結論與建議，再給評分總表（六個面向，加權總分）與證據
- 每個分數都要能對應到證據；無證據標「未評」
- 指出「自稱 vs 實際」不符之處
- 歸納各 AI 的優缺點與適合的任務類型（這是使用者最想知道的）

回覆使用者時：用 5–10 行摘要結論、評分總表與報告檔路徑；不要把整份報告貼進對話。

## 5. 後續動作（每一步都先列指令、取得使用者同意才執行）

依使用者決定：

**A. 合併某分支回主幹**
```bash
python compare_branches.py strip --worktree "<勝出分支 worktree>"   # 移除 .handoff/ 與 AGENTS/CLAUDE/GEMINI.md 的交接區塊
cd "<勝出分支 worktree>" && git add -A && git commit -m "chore(handoff): 移除交接鷹架"
cd "<主幹>" && git tag backup/<主幹分支>-<YYYYMMDD-HHmm>          # 先備份
git merge --no-ff <分支> -m "merge: 採用 <AI> 的實作（#分支比較）"
```
有衝突時停下，列出衝突檔案與建議解法，讓使用者決定。

**B. 把某分支直接變成主版**（主幹交接後沒有要保留的進展時）
```bash
python compare_branches.py strip --worktree "<分支 worktree>" && (commit 同上)
cd "<主幹>" && git tag backup/<主幹分支>-<YYYYMMDD-HHmm>
git merge --ff-only <分支>        # 主幹沒有新 commit 時可快轉
# 不能快轉時才考慮：git reset --hard <分支>（破壞性，必須再次明確確認，且已有 backup tag）
```

**C. 從多個分支挑功能**：先合併主要分支，再 `git cherry-pick <commit>` 或 `git checkout <分支> -- <檔案>` 帶入其他分支的特定功能，最後跑測試。

**D. 清理**（合併後）：`git worktree remove "<路徑>"`、`git branch -d <分支>`；未採用的分支先問要保留還是刪除（`-D`）。是否 push 主幹另外詢問。

`.handoffs/` 的交接文件與報告保留在主幹本機（不進版控），作為 AI 表現的歷史紀錄。

## 附錄：無腳本流程

```bash
git -C "<主幹>" worktree list
git -C "<主幹>" log --oneline <base>..<分支>                 # base 取自 .handoff/BASELINE.json 的 base_commit，或 git merge-base
git -C "<主幹>" diff --stat <base>..<分支> -- . ":(exclude).handoff"
git -C "<主幹>" merge-tree --write-tree --name-only <主幹分支> <分支>   # exit 1 表示有衝突
# 讀各分支 .handoff/FEATURES.md 自行製作功能矩陣
```
非 worktree 的獨立資料夾（手動複製）：`git diff --no-index --stat "<主幹>" "<資料夾>"`，並排除 node_modules、.venv、.git 等目錄後比較。
