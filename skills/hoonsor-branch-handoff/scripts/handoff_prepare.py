#!/usr/bin/env python3
"""#分支接手 輔助腳本（僅用 Python 標準函式庫，Windows / macOS / Linux 通用）

子指令：
  plan    盤點專案：Git 狀態、未提交變更、被 .gitignore 忽略的檔案分類，輸出 JSON（不修改任何東西）
  create  建立交接分支與 worktree，複製未提交變更與指定的忽略檔，寫入 .handoff/ 骨架與指引檔
  finalize 在 worktree 內 git add + commit（交接快照），並把交接文件備份到主幹的 .handoffs/（不進版控）

範例：
  python handoff_prepare.py plan --project "D:\\01-Project\\MyApp" --target codex
  python handoff_prepare.py create --project "D:\\01-Project\\MyApp" --target codex --source-agent "Claude Opus 5.5" --include-suggested
  python handoff_prepare.py finalize --worktree "D:\\01-Project\\MyApp_worktrees\\handoff-codex-20261006-2145"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:  # Windows 主控台中文輸出
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = 1
HANDOFF_DIR = ".handoff"
MAIN_ARCHIVE_DIR = ".handoffs"
MARK_BEGIN = "<!-- HANDOFF:BEGIN"
MARK_END = "<!-- HANDOFF:END -->"
POINTER_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]

# ---- 排除規則：環境、套件、建置產物、快取 -------------------------------------------------
EXCLUDE_DIR_NAMES = {
    "node_modules", ".venv", "venv", "env", ".env.d", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".nox", "dist", "build", "out", ".next", ".nuxt", ".svelte-kit", ".turbo",
    ".cache", ".parcel-cache", ".vite", "coverage", "htmlcov", "target", ".gradle", ".idea", ".vs",
    "bin", "obj", ".expo", ".dart_tool", "Pods", "vendor", ".terraform", "site-packages",
    ".ipynb_checkpoints", "logs", ".vercel", ".firebase", ".wrangler", ".angular", "bower_components",
    ".yarn", ".pnpm-store", ".npm", "jspm_packages", ".eggs", "wheels", ".conda", ".history",
    MAIN_ARCHIVE_DIR,
}
EXCLUDE_DIR_GLOBS = ["*.egg-info", "*_worktrees"]
EXCLUDE_FILE_GLOBS = [
    "*.log", "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db", "desktop.ini", "*.tmp", "*.swp",
    "MIGRATION_*.zip", "*.tsbuildinfo", ".eslintcache", "npm-debug.log*", "yarn-error.log*",
]
SECRET_FILE_GLOBS = [
    ".env.keys", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "id_rsa*", "id_ed25519*",
    "credentials*.json", "service-account*.json", "*.keystore", ".npmrc", ".pypirc", ".netrc",
]
ENV_FILE_RE = re.compile(r"^\.env(\..+)?$", re.I)
BIG_FILE_BYTES = 50 * 1024 * 1024


def now_local() -> _dt.datetime:
    return _dt.datetime.now().astimezone()


def git(args, cwd, check=True):
    cmd = ["git", "-c", "core.quotepath=off"] + list(args)
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失敗（{p.returncode}）：{err.strip()}")
    return p.returncode, out, err


def zsplit(s: str):
    return [x for x in s.split("\0") if x]


def slugify(s: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", s.strip().lower(), flags=re.UNICODE)
    return re.sub(r"-+", "-", s).strip("-") or "agent"


def dir_size(p: Path, cap_files=20000) -> int:
    total = 0
    n = 0
    for root, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except OSError:
                pass
            n += 1
            if n > cap_files:
                return total
    return total


def is_dotenvx_encrypted(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "DOTENV_PUBLIC_KEY" in txt or "encrypted:" in txt


def classify_ignored(rel: str, root: Path) -> dict:
    """回傳 {path, kind: dir|file, category, reason, size}"""
    is_dir = rel.endswith("/")
    rel_clean = rel.rstrip("/")
    name = Path(rel_clean).name
    parts = Path(rel_clean).parts
    full = root / rel_clean
    item = {"path": rel_clean, "kind": "dir" if is_dir else "file", "size": 0}

    if any(p in EXCLUDE_DIR_NAMES for p in parts) or any(
        fnmatch.fnmatch(p, g) for p in parts for g in EXCLUDE_DIR_GLOBS
    ):
        item.update(category="exclude", reason="環境／套件／建置產物或快取")
        return item
    if not is_dir and any(fnmatch.fnmatch(name, g) for g in EXCLUDE_FILE_GLOBS):
        item.update(category="exclude", reason="日誌、暫存或系統檔")
        return item
    if not is_dir and any(fnmatch.fnmatch(name, g) for g in SECRET_FILE_GLOBS):
        item.update(category="secret", reason="金鑰／憑證／解密金鑰，一律不複製")
        return item

    try:
        item["size"] = dir_size(full) if is_dir else full.stat().st_size
    except OSError:
        pass

    if not is_dir and ENV_FILE_RE.match(name):
        if name.lower() in (".env.example", ".env.sample", ".env.template"):
            item.update(category="suggest", reason="環境變數範本")
        elif is_dotenvx_encrypted(full):
            item.update(category="suggest", reason="dotenvx 已加密的 .env（解密金鑰在使用者環境變數，不複製 .env.keys）")
        else:
            item.update(category="confirm", reason="明文 .env，含機密值，需使用者明確同意才複製")
        return item

    if item["size"] > BIG_FILE_BYTES:
        item.update(category="confirm", reason=f"大型項目（{item['size']/1024/1024:.1f} MB），確認是否需要")
        return item
    # 本機設定、資料檔、AI 工具設定等：讓使用者決定
    item.update(category="review", reason="被 .gitignore 忽略的本機檔案（設定、資料、筆記等），請確認是否需要")
    return item


def repo_info(project: Path) -> dict:
    info = {"project": str(project), "is_git": False}
    rc, out, _ = git(["rev-parse", "--show-toplevel"], project, check=False)
    if rc != 0:
        return info
    root = Path(out.strip())
    info.update(is_git=True, repo_root=str(root))
    rc, out, _ = git(["rev-parse", "--verify", "HEAD"], root, check=False)
    info["has_commits"] = rc == 0
    info["head"] = out.strip() if rc == 0 else None
    rc, out, _ = git(["symbolic-ref", "--short", "-q", "HEAD"], root, check=False)
    info["current_branch"] = out.strip() if rc == 0 else None
    info["detached"] = rc != 0
    _, out, _ = git(["remote", "-v"], root, check=False)
    info["remotes"] = sorted({l.split()[1] for l in out.splitlines() if l.strip()})
    _, out, _ = git(["worktree", "list", "--porcelain"], root, check=False)
    info["existing_worktrees"] = [l[9:] for l in out.splitlines() if l.startswith("worktree ")]
    _, out, _ = git(["--version"], root, check=False)
    info["git_version"] = out.strip()
    return info


def wip_changes(root: Path, has_commits: bool) -> dict:
    res = {"modified": [], "added": [], "deleted": [], "untracked": []}
    if has_commits:
        _, out, _ = git(["diff", "HEAD", "--name-status", "--no-renames", "-z"], root)
        toks = zsplit(out)
        for i in range(0, len(toks) - 1, 2):
            st, path = toks[i], toks[i + 1]
            if st.startswith("D"):
                res["deleted"].append(path)
            elif st.startswith("A"):
                res["added"].append(path)
            else:
                res["modified"].append(path)
    _, out, _ = git(["ls-files", "-o", "--exclude-standard", "-z"], root)
    res["untracked"] = [p for p in zsplit(out) if not p.startswith(MAIN_ARCHIVE_DIR + "/")]
    return res


def ignored_items(root: Path) -> list:
    _, out, _ = git(["ls-files", "-o", "-i", "--exclude-standard", "--directory", "-z"], root)
    return [classify_ignored(p, root) for p in zsplit(out)]


def default_paths(root: Path, target: str, stamp: str, name: str | None):
    slug = slugify(name) if name else f"{slugify(target)}-{stamp}"
    branch = f"handoff/{slug}"
    wt = root.parent / f"{root.name}_worktrees" / f"handoff-{slug}"
    return branch, wt


# ---- plan ---------------------------------------------------------------------------------
def cmd_plan(a):
    project = Path(a.project).resolve()
    info = repo_info(project)
    stamp = now_local().strftime("%Y%m%d-%H%M")
    result = {"schema": SCHEMA, "generated_at": now_local().isoformat(timespec="seconds"), **info}
    warnings = []
    if not info["is_git"]:
        warnings.append("不是 Git 倉庫：需先 git init 並建立第一個 commit（請先徵得使用者同意）。")
        print(json.dumps({**result, "warnings": warnings}, ensure_ascii=False, indent=2))
        return
    root = Path(info["repo_root"])
    if not info["has_commits"]:
        warnings.append("倉庫還沒有任何 commit：worktree 需要基準 commit，請先在主幹建立初始 commit（需使用者同意）。")
    if info["detached"]:
        warnings.append("目前是 detached HEAD：分支會從目前這個 commit 分出。")
    branch, wt = default_paths(root, a.target, stamp, a.name)
    if a.worktree_root:
        wt = Path(a.worktree_root).resolve() / wt.name
    if wt.exists():
        warnings.append(f"預定的 worktree 路徑已存在：{wt}")
    rc, _, _ = git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], root, check=False)
    if rc == 0:
        warnings.append(f"分支 {branch} 已存在，請改名（--name）。")
    wip = wip_changes(root, info["has_commits"])
    ign = ignored_items(root)
    groups = {k: [i for i in ign if i["category"] == k] for k in ("suggest", "confirm", "review", "secret", "exclude")}
    wip_bytes = 0
    for p in wip["modified"] + wip["added"] + wip["untracked"]:
        try:
            wip_bytes += (root / p).stat().st_size
        except OSError:
            pass
    big_untracked = [p for p in wip["untracked"] if (root / p).is_file() and (root / p).stat().st_size > BIG_FILE_BYTES]
    if big_untracked:
        warnings.append(f"有 {len(big_untracked)} 個超過 50MB 的未追蹤檔會被一起 commit：{big_untracked[:5]}")
    for s in groups["secret"]:
        warnings.append(f"偵測到機密檔，不會複製：{s['path']}")
    result.update(
        proposed_branch=branch,
        proposed_worktree=str(wt),
        wip={**wip, "total_files": sum(len(v) for v in wip.values()), "approx_bytes": wip_bytes},
        ignored=groups,
        warnings=warnings,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---- create -------------------------------------------------------------------------------
def copy_path(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        def _ign(d, names):
            out = []
            for n in names:
                if n in EXCLUDE_DIR_NAMES or any(fnmatch.fnmatch(n, g) for g in EXCLUDE_DIR_GLOBS + EXCLUDE_FILE_GLOBS + SECRET_FILE_GLOBS):
                    out.append(n)
            return out
        shutil.copytree(src, dst, ignore=_ign, dirs_exist_ok=True)
    elif src.exists():
        shutil.copy2(src, dst)


def pointer_block(ctx: dict) -> str:
    return f"""{MARK_BEGIN}（由 #分支接手 自動產生；合併回主幹前會移除）-->
## 🔀 交接分支說明（請先讀）

本資料夾是專案 **{ctx['project_name']}** 的交接分支 `{ctx['branch']}`，
由 {ctx['source_agent']} 於 {ctx['created_at']} 從 `{ctx['base_branch']}`（commit `{ctx['base_short']}`）分出，交給 **{ctx['target_agent']}** 接續開發。

**開始任何工作前，依序閱讀：**
1. `.handoff/HANDOFF.md` — 完整開發過程、架構、決策、目前進度、下一步
2. `.handoff/FEATURES.md` — 功能清單與狀態（你的進度以此為準）
3. `.handoff/PROGRESS_LOG.md` — 歷次工作紀錄
4. 依 HANDOFF.md「環境建置」一節安裝相依套件（本資料夾**未包含** node_modules / venv 等環境）

**接手規則：**
- 只在分支 `{ctx['branch']}` 上 commit；不要 merge 到主幹、不要 push 到 main/master、不要切換到其他分支。
- 每個 commit 訊息最後加一行 trailer：`Agent: <應用程式名稱> / <模型名稱>`（例：`Agent: Codex / gpt-5.2-codex`）。
- 每次工作階段結束前：更新 `.handoff/FEATURES.md` 的狀態欄，並在 `.handoff/PROGRESS_LOG.md` **最上方**新增一筆紀錄（格式見檔案內說明）。
- 新增功能時沿用下一個 F 編號並在備註標 `🆕`；不要重新編號或刪除既有列（放棄的功能標 ❌ 並寫原因）。
- 不要修改 `.handoff/BASELINE.json` 與 `.handoff/HANDOFF.md` 的原始內容（可在 HANDOFF.md 最後的「接手者補充」一節追加）。
- 不要把 `.env.keys`、明文金鑰或密碼寫進任何檔案或 commit。
- 回覆與文件一律使用繁體中文（台灣用語）。
{MARK_END}
"""


def write_pointer_files(wt: Path, ctx: dict) -> dict:
    created, appended = [], []
    block = pointer_block(ctx)
    for name in POINTER_FILES:
        p = wt / name
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="replace")
            if MARK_BEGIN in txt:
                continue
            p.write_text(block + "\n" + txt, encoding="utf-8")  # 放最上方，確保 AI 先讀到
            appended.append(name)
        else:
            header = {"AGENTS.md": "# AGENTS.md", "CLAUDE.md": "# CLAUDE.md", "GEMINI.md": "# GEMINI.md"}[name]
            p.write_text(f"{header}\n\n{block}", encoding="utf-8")
            created.append(name)
    return {"created": created, "appended": appended}


def cmd_create(a):
    project = Path(a.project).resolve()
    info = repo_info(project)
    if not info["is_git"] or not info["has_commits"]:
        sys.exit("錯誤：專案不是 Git 倉庫或尚無 commit，請先執行 plan 並依警告處理。")
    root = Path(info["repo_root"])
    created = now_local()
    stamp = created.strftime("%Y%m%d-%H%M")
    branch, wt = default_paths(root, a.target, stamp, a.name)
    if a.branch:
        branch = a.branch
    if a.worktree:
        wt = Path(a.worktree).resolve()
    elif a.worktree_root:
        wt = Path(a.worktree_root).resolve() / wt.name
    if wt.exists() and any(wt.iterdir()):
        sys.exit(f"錯誤：worktree 目標資料夾已存在且非空：{wt}")

    base_commit = info["head"]
    base_branch = info["current_branch"] or "(detached)"
    wip = wip_changes(root, True) if not a.no_wip else {"modified": [], "added": [], "deleted": [], "untracked": []}

    wt.parent.mkdir(parents=True, exist_ok=True)
    git(["worktree", "add", "-b", branch, str(wt), base_commit], root)

    # 1) 複製未提交變更（工作目錄的實際狀態）
    for p in wip["modified"] + wip["added"] + wip["untracked"]:
        copy_path(root / p, wt / p)
    for p in wip["deleted"]:
        try:
            (wt / p).unlink()
        except OSError:
            pass

    # 2) 複製被忽略但重要的檔案
    ign = ignored_items(root)
    chosen = set(a.include or [])
    if a.include_suggested:
        chosen |= {i["path"] for i in ign if i["category"] == "suggest"}
    secret_paths = {i["path"] for i in ign if i["category"] == "secret"}
    copied_ignored, refused = [], []
    for rel in sorted(chosen):
        rel = rel.replace("\\", "/").rstrip("/")
        if rel in secret_paths or any(fnmatch.fnmatch(Path(rel).name, g) for g in SECRET_FILE_GLOBS):
            refused.append(rel)
            continue
        src = root / rel
        if not src.exists():
            refused.append(rel)
            continue
        copy_path(src, wt / rel)
        copied_ignored.append(rel)

    # 3) .handoff 骨架
    hd = wt / HANDOFF_DIR
    hd.mkdir(exist_ok=True)
    ctx = {
        "project_name": root.name,
        "branch": branch,
        "base_branch": base_branch,
        "base_short": base_commit[:8],
        "source_agent": a.source_agent,
        "target_agent": a.target,
        "created_at": created.strftime("%Y-%m-%d %H:%M (UTC%z)"),
    }
    pointers = write_pointer_files(wt, ctx)
    baseline = {
        "schema": SCHEMA,
        "project_name": root.name,
        "source_repo": str(root),
        "base_branch": base_branch,
        "base_commit": base_commit,
        "handoff_branch": branch,
        "worktree_path": str(wt),
        "created_at": created.isoformat(timespec="seconds"),
        "source_agent": a.source_agent,
        "target_agent": a.target,
        "wip_copied": wip,
        "ignored_copied": copied_ignored,
        "ignored_refused": refused,
        "excluded_categories": "node_modules / venv / 建置產物 / 快取 / 日誌 / 金鑰（詳見腳本 EXCLUDE_* 規則）",
        "pointer_files": pointers,
        "commands": {"install": "", "run": "", "test": "", "build": "", "lint": ""},
        "ports": [],
        "notes": "",
    }
    (hd / "BASELINE.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    for fname in ("HANDOFF.md", "FEATURES.md", "PROGRESS_LOG.md", "NEXT_AGENT_PROMPT.md"):
        f = hd / fname
        if not f.exists():
            f.write_text(f"<!-- 待填寫：依 references/templates.md 的「{fname}」範本撰寫 -->\n", encoding="utf-8")

    print(json.dumps({
        "ok": True, "branch": branch, "worktree": str(wt), "base_commit": base_commit,
        "wip_copied_files": sum(len(v) for v in wip.values()), "ignored_copied": copied_ignored,
        "ignored_refused": refused, "pointer_files": pointers,
        "next": "撰寫 .handoff/ 內 4 份 Markdown、補齊 BASELINE.json 的 commands，然後執行 finalize",
    }, ensure_ascii=False, indent=2))


# ---- finalize -----------------------------------------------------------------------------
def cmd_finalize(a):
    wt = Path(a.worktree).resolve()
    hd = wt / HANDOFF_DIR
    bl_path = hd / "BASELINE.json"
    if not bl_path.exists():
        sys.exit("錯誤：找不到 .handoff/BASELINE.json，這不是 #分支接手 建立的 worktree。")
    bl = json.loads(bl_path.read_text(encoding="utf-8"))
    problems = []
    for fname in ("HANDOFF.md", "FEATURES.md", "PROGRESS_LOG.md", "NEXT_AGENT_PROMPT.md"):
        txt = (hd / fname).read_text(encoding="utf-8", errors="replace")
        if "待填寫" in txt[:200] or len(txt.strip()) < 80:
            problems.append(f"{fname} 尚未完成")
    if problems and not a.force:
        sys.exit("錯誤：" + "；".join(problems) + "（確認無誤可加 --force）")

    git(["add", "-A"], wt)
    msg = a.message or (
        f"chore(handoff): {bl['source_agent']} 交接快照 → {bl['target_agent']}\n\n"
        f"基準：{bl['base_branch']}@{bl['base_commit'][:8]}\n"
        f"包含未提交變更 {sum(len(v) for v in bl['wip_copied'].values())} 個檔案與 .handoff/ 交接文件。\n\n"
        f"Agent: {bl['source_agent']}"
    )
    rc, out, err = git(["commit", "-m", msg], wt, check=False)
    if rc != 0 and "nothing to commit" not in (out + err):
        sys.exit(f"commit 失敗：{err or out}")
    _, head, _ = git(["rev-parse", "HEAD"], wt)

    # 備份交接文件到主幹的 .handoffs/<slug>/，並用 .git/info/exclude 排除（不弄髒主幹）
    src_repo = Path(bl["source_repo"])
    slug = bl["handoff_branch"].replace("/", "__")
    arch = src_repo / MAIN_ARCHIVE_DIR / slug
    arch.mkdir(parents=True, exist_ok=True)
    for f in hd.iterdir():
        if f.is_file():
            shutil.copy2(f, arch / f.name)
    (arch / "SNAPSHOT_COMMIT.txt").write_text(head.strip() + "\n", encoding="utf-8")
    _, gitdir, _ = git(["rev-parse", "--git-common-dir"], src_repo)
    gd = Path(gitdir.strip())
    if not gd.is_absolute():
        gd = src_repo / gd
    excl = gd / "info" / "exclude"
    excl.parent.mkdir(parents=True, exist_ok=True)
    cur = excl.read_text(encoding="utf-8", errors="ignore") if excl.exists() else ""
    if f"/{MAIN_ARCHIVE_DIR}/" not in cur:
        with excl.open("a", encoding="utf-8") as fh:
            fh.write(f"\n# #分支接手：交接文件備份與比較報告（不進版控）\n/{MAIN_ARCHIVE_DIR}/\n")
    print(json.dumps({"ok": True, "snapshot_commit": head.strip(), "archive": str(arch),
                      "worktree": str(wt), "branch": bl["handoff_branch"]}, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="#分支接手 輔助腳本")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--project", default=".")
    p.add_argument("--target", default="next-agent", help="接手的 AI，例如 codex / antigravity / dsh / claude")
    p.add_argument("--name", help="自訂分支名稱尾段（預設 <target>-<時間>）")
    p.add_argument("--worktree-root", help="worktree 上層資料夾（預設 <專案>_worktrees）")
    p.set_defaults(func=cmd_plan)

    c = sub.add_parser("create")
    c.add_argument("--project", default=".")
    c.add_argument("--target", default="next-agent")
    c.add_argument("--name")
    c.add_argument("--branch", help="完整分支名稱（覆蓋預設 handoff/...）")
    c.add_argument("--worktree", help="完整 worktree 路徑")
    c.add_argument("--worktree-root")
    c.add_argument("--source-agent", default="Claude")
    c.add_argument("--include", action="append", help="要一併複製的被忽略檔案／資料夾（相對路徑，可重複）")
    c.add_argument("--include-suggested", action="store_true", help="複製 plan 中 category=suggest 的項目")
    c.add_argument("--no-wip", action="store_true", help="不複製未提交變更（只從最後一個 commit 分出）")
    c.set_defaults(func=cmd_create)

    f = sub.add_parser("finalize")
    f.add_argument("--worktree", required=True)
    f.add_argument("--message")
    f.add_argument("--force", action="store_true")
    f.set_defaults(func=cmd_finalize)

    a = ap.parse_args()
    try:
        a.func(a)
    except RuntimeError as e:
        sys.exit(f"錯誤：{e}")


if __name__ == "__main__":
    main()
