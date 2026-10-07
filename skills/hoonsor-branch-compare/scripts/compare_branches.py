#!/usr/bin/env python3
"""#分支比較 輔助腳本（僅用 Python 標準函式庫）

子指令：
  list     列出主幹倉庫的所有 worktree 與 handoff/* 分支
  collect  收集主幹與各分支的客觀數據 → compare_data.json + COMPARE_DRAFT.md（不修改任何 Git 狀態）
  strip    在交接分支上移除交接鷹架（.handoff/ 與 HANDOFF 標記區塊），為合併做準備（不自動 commit）

範例：
  python compare_branches.py list --main "D:\\01-Project\\MyApp"
  python compare_branches.py collect --main "D:\\01-Project\\MyApp" --branch "D:\\01-Project\\MyApp_worktrees\\handoff-codex-20261006-2145" --branch handoff/dsh-20261006-2150
  python compare_branches.py collect --main ... --branch ... --run-tests
  python compare_branches.py strip --worktree "D:\\...\\handoff-codex-..."
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HANDOFF_DIR = ".handoff"
MAIN_ARCHIVE_DIR = ".handoffs"
MARK_BEGIN = "<!-- HANDOFF:BEGIN"
MARK_END = "<!-- HANDOFF:END -->"
POINTER_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
SCAFFOLD_PATHS = [HANDOFF_DIR] + POINTER_FILES
STATUS_MAP = {
    "✅": "done", "🟡": "partial", "⬜": "todo", "❌": "dropped",
    "done": "done", "完成": "done", "partial": "partial", "部分": "partial",
    "todo": "todo", "未開始": "todo", "dropped": "dropped", "放棄": "dropped",
}
FEATURE_ROW = re.compile(r"^\|\s*(F\d{2,3})\s*\|(.*)$")
LOG_HEAD = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}[^｜|]*)[｜|]\s*([^｜|]+?)\s*(?:[｜|]\s*(.*))?$")


def git(args, cwd, check=True, timeout=120):
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=str(cwd),
                       capture_output=True, timeout=timeout)
    out, err = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}（{cwd}）失敗：{err.strip()}")
    return p.returncode, out, err


def common_dir(path: Path) -> Path | None:
    rc, out, _ = git(["rev-parse", "--git-common-dir"], path, check=False)
    if rc != 0:
        return None
    d = Path(out.strip())
    return (path / d).resolve() if not d.is_absolute() else d.resolve()


def worktree_map(main: Path) -> dict:
    """branch -> worktree path"""
    _, out, _ = git(["worktree", "list", "--porcelain"], main)
    res, cur = {}, None
    for line in out.splitlines():
        if line.startswith("worktree "):
            cur = line[9:]
        elif line.startswith("branch ") and cur:
            res[line[7:].replace("refs/heads/", "")] = cur
    return res


def read_text_at(repo: Path, ref: str | None, wt: Path | None, rel: str) -> str | None:
    if wt and (wt / rel).exists():
        return (wt / rel).read_text(encoding="utf-8", errors="replace")
    if ref:
        rc, out, _ = git(["show", f"{ref}:{rel}"], repo, check=False)
        if rc == 0:
            return out
    return None


def parse_features(txt: str | None) -> dict:
    feats = {}
    if not txt:
        return feats
    for line in txt.splitlines():
        m = FEATURE_ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        name = cells[0] if cells else ""
        raw = cells[1] if len(cells) > 1 else ""
        status = "unknown"
        for k, v in STATUS_MAP.items():
            if k in raw or k in raw.lower():
                status = v
                break
        note = cells[4] if len(cells) > 4 else ""
        feats[m.group(1)] = {"name": name, "status": status, "raw": raw, "new": "🆕" in line, "note": note[:200]}
    return feats


def feature_summary(feats: dict) -> dict:
    c = {"done": 0, "partial": 0, "todo": 0, "dropped": 0, "unknown": 0}
    for f in feats.values():
        c[f["status"]] = c.get(f["status"], 0) + 1
    active = sum(c.values()) - c["dropped"]
    score = (c["done"] + 0.5 * c["partial"]) / active * 100 if active else 0
    return {**c, "total": len(feats), "completion_pct": round(score, 1)}


def parse_log(txt: str | None) -> dict:
    if not txt:
        return {"entries": 0, "agents": [], "latest": None}
    entries, agents = [], []
    lines = txt.splitlines()
    for i, line in enumerate(lines):
        m = LOG_HEAD.match(line.strip())
        if m:
            entries.append(i)
            agents.append(m.group(2).strip())
    latest = None
    if entries:
        start = entries[0]
        end = entries[1] if len(entries) > 1 else len(lines)
        latest = "\n".join(lines[start:end]).strip()[:1500]
    return {"entries": len(entries), "agents": sorted(set(agents)), "latest": latest}


def numstat(repo: Path, a: str, b: str) -> dict:
    _, out, _ = git(["diff", "--numstat", "--no-renames", f"{a}..{b}", "--", ".",
                     *[f":(exclude){p}" for p in SCAFFOLD_PATHS]], repo)
    files, add, dele = [], 0, 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        x, y, path = parts
        x = int(x) if x.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        add += x
        dele += y
        files.append({"path": path, "add": x, "del": y})
    files.sort(key=lambda f: f["add"] + f["del"], reverse=True)
    return {"files_changed": len(files), "insertions": add, "deletions": dele, "files": files}


def commits(repo: Path, a: str, b: str) -> list:
    fmt = "%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:key=Agent,valueonly,separator=;)%x1f%(trailers:key=Co-Authored-By,valueonly,separator=;)%x1e"
    _, out, _ = git(["log", f"--format={fmt}", f"{a}..{b}"], repo)
    res = []
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        f = rec.split("\x1f")
        while len(f) < 6:
            f.append("")
        res.append({"sha": f[0][:10], "author": f[1], "date": f[2], "subject": f[3],
                    "agent": f[4].strip(), "coauthor": f[5].strip()})
    return res


def conflicts(repo: Path, ours: str, theirs: str) -> dict:
    rc, out, err = git(["merge-tree", "--write-tree", "--name-only", "--no-messages", ours, theirs], repo, check=False)
    if rc not in (0, 1):
        return {"checked": False, "reason": (err or out).strip()[:300] or "git 版本過舊（需 2.38+）"}
    lines = [l for l in out.splitlines()[1:] if l.strip()]
    return {"checked": True, "has_conflicts": rc == 1, "files": lines[:200]}


def run_tests(wt: Path, cmd: str, timeout: int) -> dict:
    if not cmd:
        return {"ran": False, "reason": "BASELINE.json 沒有 test 指令"}
    try:
        p = subprocess.run(cmd, cwd=str(wt), shell=True, capture_output=True, timeout=timeout)
        out = (p.stdout + p.stderr).decode("utf-8", "replace")
        return {"ran": True, "command": cmd, "exit_code": p.returncode, "tail": out[-2500:]}
    except subprocess.TimeoutExpired:
        return {"ran": True, "command": cmd, "exit_code": None, "tail": f"逾時（{timeout}s）"}


def resolve_branch(main: Path, spec: str, wts: dict, main_cd: Path) -> dict:
    p = Path(spec)
    if p.exists():
        p = p.resolve()
        cd = common_dir(p)
        if cd is None:
            return {"spec": spec, "error": "路徑不是 Git 倉庫（可能是直接複製的資料夾），無法以 Git 比較"}
        if cd != main_cd:
            return {"spec": spec, "error": "此資料夾屬於不同的 Git 倉庫（不是本專案的 worktree）"}
        _, out, _ = git(["rev-parse", "--abbrev-ref", "HEAD"], p)
        return {"spec": spec, "branch": out.strip(), "worktree": str(p)}
    rc, _, _ = git(["rev-parse", "--verify", "--quiet", f"refs/heads/{spec}"], main, check=False)
    if rc != 0:
        return {"spec": spec, "error": "找不到此路徑或分支"}
    return {"spec": spec, "branch": spec, "worktree": wts.get(spec)}


def cmd_list(a):
    main = Path(a.main).resolve()
    wts = worktree_map(main)
    _, out, _ = git(["for-each-ref", "--format=%(refname:short)%09%(committerdate:iso8601)%09%(subject)", "refs/heads/"], main)
    rows = []
    for line in out.splitlines():
        name, date, subj = (line.split("\t") + ["", ""])[:3]
        rows.append({"branch": name, "last_commit": date, "subject": subj, "worktree": wts.get(name),
                     "is_handoff": name.startswith("handoff/")})
    _, cur, _ = git(["rev-parse", "--abbrev-ref", "HEAD"], main)
    arch = main / MAIN_ARCHIVE_DIR
    print(json.dumps({"main": str(main), "current_branch": cur.strip(), "branches": rows,
                      "archives": sorted(p.name for p in arch.iterdir() if p.is_dir()) if arch.exists() else []},
                     ensure_ascii=False, indent=2))


def cmd_collect(a):
    main = Path(a.main).resolve()
    main_cd = common_dir(main)
    if main_cd is None:
        sys.exit("錯誤：--main 不是 Git 倉庫")
    _, main_branch, _ = git(["rev-parse", "--abbrev-ref", "HEAD"], main)
    main_branch = main_branch.strip()
    _, main_head, _ = git(["rev-parse", "HEAD"], main)
    wts = worktree_map(main)
    _, gv, _ = git(["--version"], main)
    now = _dt.datetime.now().astimezone()
    data = {"generated_at": now.isoformat(timespec="seconds"), "git_version": gv.strip(),
            "main": {"path": str(main), "branch": main_branch, "head": main_head.strip()},
            "branches": []}

    # 主幹未提交變更
    _, st, _ = git(["status", "--porcelain"], main)
    data["main"]["uncommitted"] = len([l for l in st.splitlines() if l.strip() and MAIN_ARCHIVE_DIR not in l])

    for spec in a.branch:
        r = resolve_branch(main, spec, wts, main_cd)
        if "error" in r:
            data["branches"].append(r)
            continue
        br, wt = r["branch"], Path(r["worktree"]) if r.get("worktree") else None
        bl_txt = read_text_at(main, br, wt, f"{HANDOFF_DIR}/BASELINE.json")
        baseline = json.loads(bl_txt) if bl_txt else None
        if baseline and baseline.get("base_commit"):
            base = baseline["base_commit"]
        else:
            _, mb, _ = git(["merge-base", main_branch, br], main)
            base = mb.strip()
        # 交接當下的功能矩陣：優先讀主幹 .handoffs 備份，其次讀分支第一個 commit 版本
        arch = main / MAIN_ARCHIVE_DIR / br.replace("/", "__")
        snap_feat = (arch / "FEATURES.md").read_text(encoding="utf-8", errors="replace") if (arch / "FEATURES.md").exists() else None
        snap_commit = (arch / "SNAPSHOT_COMMIT.txt").read_text().strip() if (arch / "SNAPSHOT_COMMIT.txt").exists() else None
        if snap_feat is None:
            _, first, _ = git(["rev-list", "--reverse", f"{base}..{br}"], main, check=False)
            first = first.split()[0] if first.split() else None
            if first:
                snap_commit = snap_commit or first
                snap_feat = read_text_at(main, first, None, f"{HANDOFF_DIR}/FEATURES.md")
        feats_now = parse_features(read_text_at(main, br, wt, f"{HANDOFF_DIR}/FEATURES.md"))
        feats_then = parse_features(snap_feat)
        log = parse_log(read_text_at(main, br, wt, f"{HANDOFF_DIR}/PROGRESS_LOG.md"))
        since = snap_commit or base
        all_commits = commits(main, base, br)
        work_commits = commits(main, since, br) if since != base else all_commits
        uncommitted = None
        if wt and wt.exists():
            _, st, _ = git(["status", "--porcelain"], wt)
            uncommitted = [l for l in st.splitlines() if l.strip()]
        entry = {
            "spec": spec, "branch": br, "worktree": str(wt) if wt else None,
            "baseline": {k: baseline.get(k) for k in ("source_agent", "target_agent", "created_at", "base_branch", "commands")} if baseline else None,
            "base_commit": base, "snapshot_commit": snap_commit,
            "commits_after_handoff": work_commits,
            "agents_seen": sorted(({c["agent"] for c in work_commits if c["agent"]} | set(log["agents"]))
                                  - {(baseline or {}).get("source_agent")}),
            "diff_vs_base": numstat(main, base, br),
            "diff_after_handoff": numstat(main, since, br),
            "features_at_handoff": feature_summary(feats_then),
            "features_now": feature_summary(feats_now),
            "features": feats_now,
            "features_baseline": feats_then,
            "progress_log": log,
            "uncommitted_in_worktree": uncommitted,
            "merge_conflicts_with_main": conflicts(main, main_branch, br),
        }
        if a.run_tests and wt:
            cmd = (baseline or {}).get("commands", {}).get("test", "")
            entry["tests"] = run_tests(wt, cmd, a.test_timeout)
        data["branches"].append(entry)

    # 主幹在交接後是否也有進展
    bases = {b["base_commit"] for b in data["branches"] if "base_commit" in b}
    data["main"]["commits_since_base"] = {b[:10]: len(commits(main, b, main_branch)) for b in bases}
    data["main"]["diff_since_base"] = {b[:10]: {k: v for k, v in numstat(main, b, main_branch).items() if k != "files"} for b in bases}

    # 分支間重疊修改的檔案
    touched = {}
    for b in data["branches"]:
        for f in b.get("diff_after_handoff", {}).get("files", []):
            touched.setdefault(f["path"], []).append(b["branch"])
    data["overlap_files"] = {p: v for p, v in touched.items() if len(v) > 1}

    out_dir = Path(a.out).resolve() if a.out else main / MAIN_ARCHIVE_DIR / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%d-%H%M")
    jpath = out_dir / f"compare_data_{stamp}.json"
    jpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    mpath = out_dir / f"COMPARE_DRAFT_{stamp}.md"
    mpath.write_text(render_draft(data), encoding="utf-8")
    print(json.dumps({"ok": True, "json": str(jpath), "draft": str(mpath),
                      "summary": [{"branch": b.get("branch", b.get("spec")), "error": b.get("error"),
                                   "agents": b.get("agents_seen"),
                                   "completion": b.get("features_now", {}).get("completion_pct"),
                                   "commits": len(b.get("commits_after_handoff", [])),
                                   "conflicts": b.get("merge_conflicts_with_main", {}).get("has_conflicts")}
                                  for b in data["branches"]]}, ensure_ascii=False, indent=2))


ICON = {"done": "✅", "partial": "🟡", "todo": "⬜", "dropped": "❌", "unknown": "？", None: "—"}


def render_draft(d: dict) -> str:
    ok = [b for b in d["branches"] if "error" not in b]
    L = [f"# 分支比較數據草稿（自動產生，{d['generated_at']}）", "",
         f"主幹：`{d['main']['branch']}` @ `{d['main']['head'][:8]}`（{d['main']['path']}），未提交變更 {d['main']['uncommitted']} 個", ""]
    for b in d["branches"]:
        if "error" in b:
            L.append(f"- ⚠️ `{b['spec']}`：{b['error']}")
    if d["main"].get("commits_since_base"):
        L.append("主幹自交接基準後的 commit 數：" + "、".join(f"`{k}` → {v}" for k, v in d["main"]["commits_since_base"].items()))
    L += ["", "## 1. 總覽", "",
          "| 分支 | 接手 AI（紀錄） | 交接時完成度 | 目前完成度 | 交接後 commit | 交接後變更 | 與主幹衝突 | 未提交 |",
          "|---|---|---|---|---|---|---|---|"]
    for b in ok:
        da = b["diff_after_handoff"]
        cf = b["merge_conflicts_with_main"]
        cft = ("有 %d 檔" % len(cf["files"])) if cf.get("has_conflicts") else ("無" if cf.get("checked") else "未檢查")
        L.append(f"| `{b['branch']}` | {', '.join(b['agents_seen']) or (b['baseline'] or {}).get('target_agent', '?')} | "
                 f"{b['features_at_handoff']['completion_pct']}% | **{b['features_now']['completion_pct']}%** | "
                 f"{len(b['commits_after_handoff'])} | {da['files_changed']} 檔 +{da['insertions']}/-{da['deletions']} | {cft} | "
                 f"{len(b['uncommitted_in_worktree']) if b['uncommitted_in_worktree'] is not None else '—'} |")
    ids = sorted({fid for b in ok for fid in list(b["features"]) + list(b["features_baseline"])}, key=lambda x: int(x[1:]))
    if ids:
        L += ["", "## 2. 功能矩陣（交接時 → 各分支目前）", "",
              "| ID | 功能 | 交接時 | " + " | ".join(f"`{b['branch']}`" for b in ok) + " |",
              "|---|---|---|" + "---|" * len(ok)]
        for fid in ids:
            name = next((b["features"].get(fid, b["features_baseline"].get(fid, {})).get("name") for b in ok if fid in b["features"] or fid in b["features_baseline"]), "")
            then = next((b["features_baseline"][fid]["status"] for b in ok if fid in b["features_baseline"]), None)
            cells = []
            for b in ok:
                f = b["features"].get(fid)
                cells.append((ICON[f["status"]] + (" 🆕" if f["new"] else "")) if f else "—")
            L.append(f"| {fid} | {name} | {ICON[then]} | " + " | ".join(cells) + " |")
    L += ["", "## 3. 各分支細節", ""]
    for b in ok:
        L += [f"### `{b['branch']}`", ""]
        if b["baseline"]:
            L.append(f"- 交出者：{b['baseline'].get('source_agent')}｜指定接手：{b['baseline'].get('target_agent')}｜建立：{b['baseline'].get('created_at')}")
        L.append(f"- worktree：{b['worktree'] or '（無，僅分支）'}")
        L.append(f"- 工作紀錄筆數：{b['progress_log']['entries']}")
        top = b["diff_after_handoff"]["files"][:12]
        if top:
            L.append("- 變更最多的檔案：" + "、".join(f"`{f['path']}`(+{f['add']}/-{f['del']})" for f in top))
        if b["commits_after_handoff"]:
            L.append("- 交接後 commit：")
            for c in b["commits_after_handoff"][:25]:
                L.append(f"  - `{c['sha'][:8]}` {c['date'][:16]} {c['subject']}" + (f"（{c['agent']}）" if c["agent"] else ""))
        cf = b["merge_conflicts_with_main"]
        if cf.get("has_conflicts"):
            L.append("- 與主幹衝突的檔案：" + "、".join(f"`{x}`" for x in cf["files"][:20]))
        if "tests" in b:
            t = b["tests"]
            L.append(f"- 測試：{t.get('command', '')} → exit {t.get('exit_code')}" if t.get("ran") else f"- 測試：未執行（{t.get('reason')}）")
        if b["progress_log"]["latest"]:
            L += ["", "最新工作紀錄：", "", "```", b["progress_log"]["latest"], "```"]
        L.append("")
    if d["overlap_files"]:
        L += ["## 4. 多個分支都修改的檔案（實作差異重點）", ""]
        for p, bs in list(d["overlap_files"].items())[:40]:
            L.append(f"- `{p}`：{', '.join(bs)}")
    return "\n".join(L) + "\n"


def cmd_strip(a):
    wt = Path(a.worktree).resolve()
    removed = []
    hd = wt / HANDOFF_DIR
    bl = {}
    if (hd / "BASELINE.json").exists():
        bl = json.loads((hd / "BASELINE.json").read_text(encoding="utf-8"))
    created = set((bl.get("pointer_files") or {}).get("created", []))
    for name in POINTER_FILES:
        p = wt / name
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if MARK_BEGIN not in txt:
            continue
        new = re.sub(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", "", txt, flags=re.S)
        if name in created and new.strip() in ("", f"# {name}"):
            p.unlink()
            removed.append(f"{name}（整檔刪除，原本由交接建立）")
        else:
            p.write_text(new.lstrip("\n"), encoding="utf-8")
            removed.append(f"{name}（移除交接區塊）")
    if hd.exists():
        shutil.rmtree(hd)
        removed.append(".handoff/（文件已備份於主幹 .handoffs/）")
    print(json.dumps({"ok": True, "worktree": str(wt), "removed": removed,
                      "next": "檢查 git status 後 commit：chore(handoff): 移除交接鷹架，再進行 merge"}, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="#分支比較 輔助腳本")
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list")
    l.add_argument("--main", default=".")
    l.set_defaults(func=cmd_list)
    c = sub.add_parser("collect")
    c.add_argument("--main", default=".")
    c.add_argument("--branch", action="append", required=True, help="分支資料夾路徑或分支名稱（可重複）")
    c.add_argument("--out", help="輸出資料夾（預設 <主幹>/.handoffs/reports）")
    c.add_argument("--run-tests", action="store_true", help="在各 worktree 執行 BASELINE.json 的 test 指令")
    c.add_argument("--test-timeout", type=int, default=600)
    c.set_defaults(func=cmd_collect)
    s = sub.add_parser("strip")
    s.add_argument("--worktree", required=True)
    s.set_defaults(func=cmd_strip)
    a = ap.parse_args()
    try:
        a.func(a)
    except RuntimeError as e:
        sys.exit(f"錯誤：{e}")


if __name__ == "__main__":
    main()
