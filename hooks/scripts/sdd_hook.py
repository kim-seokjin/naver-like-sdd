#!/usr/bin/env python3
"""SDD 훅. 규칙 주입(SessionStart, SubagentStart)과 스펙 없는 코드 수정 경고(PreToolUse, Stop).

PreToolUse는 Write/Edit를 고치기 전에, Stop은 셸로 고친 것까지 파일 변화를 비교해 고친 뒤에 경고한다.
경고 전용이므로 어떤 오류가 나도 도구 실행을 막지 않는다.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
CODE_EXT = set(
    ".py .ipynb .js .jsx .ts .tsx .mjs .cjs .svelte .vue .java .kt .kts .go .rs .c .h "
    ".cc .cpp .hpp .cs .rb .php .swift .scala .sql .sh .bash .ps1 .css .scss .html".split()
)
ACTIVE = re.compile(r"^- *(?:\*\*)?상태(?:\*\*)? *:(?:\*\*)? *진행 ?중 *(?:<!--.*)?$", re.M)


def find_root(start):
    """start부터 위로 올라가며 SDD 프로젝트 루트를 찾는다. git 루트에서 멈춘다."""
    for d in [start, *start.parents]:
        if any(d.glob("specs/*/decisions.md")):
            return d
        if (d / ".git").exists():
            return None
    return None


def active_specs(root):
    found = []
    for plan in sorted(root.glob("specs/*/plan.md")):
        try:
            text = plan.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        # 본문의 같은 문구와 섞이지 않도록 첫 "## " 앞의 머리말만 본다.
        header = re.split(r"^## ", unicodedata.normalize("NFC", text), maxsplit=1, flags=re.M)[0]
        if ACTIVE.search(header):
            found.append(plan.parent.relative_to(root).as_posix())
    return found


def state_file(kind, session_id):
    base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or Path(tempfile.gettempdir()) / "naver-like-sdd")
    name = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")
    return base / kind / name


def first_time(session_id):
    """세션마다 한 번만 True. 기록할 수 없으면 경고를 놓치지 않도록 True."""
    flag = state_file("warned", session_id)
    try:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.touch(exist_ok=False)
        return True
    except FileExistsError:
        return False
    except OSError:
        return True


def is_code(path, root):
    return (
        path.suffix.lower() in CODE_EXT
        and path.is_relative_to(root)
        and not path.is_relative_to(root / "specs")
    )


def file_sig(path):
    try:
        st = os.stat(path)
        return [st.st_mtime_ns, st.st_size]
    except OSError:
        return None


def snapshot(root):
    """git이 아는 코드 파일(무시되지 않은 새 파일 포함)의 수정 시각과 크기. git 저장소가 아니면 None.

    git status는 줄바꿈이 다른 체크아웃에서 모든 파일을 다시 읽어 느리므로 쓰지 않는다.
    """
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True, timeout=8,
    )
    if out.returncode != 0:
        return None
    names = {n for n in os.fsdecode(out.stdout).split("\0") if n and is_code(root / n, root)}
    paths = sorted(names)
    with ThreadPoolExecutor(16) as pool:
        return dict(zip(paths, pool.map(lambda n: file_sig(root / n), paths)))


def save_baseline(session_id, root, active):
    """비교 기준을 저장한다. 진행 중인 스펙이 있으면 비교하지 않으므로 파일을 조회하지 않는다."""
    state = {"root": str(root), "active": active}
    if not active:
        state["files"] = snapshot(root)
        if state["files"] is None:
            return
    path = state_file("baseline", session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


def load_baseline(session_id, root):
    try:
        state = json.loads(state_file("baseline", session_id).read_text(encoding="utf-8"))
        return state if state["root"] == str(root) else None
    except (OSError, ValueError, KeyError):
        return None


def changed_code(state, root):
    before, now = state["files"], snapshot(root)
    if now is None:
        return []
    return sorted(n for n in before.keys() | now.keys() if before.get(n) != now.get(n))


def cleanup():
    """30일 지난 세션 상태를 지운다."""
    limit = time.time() - 30 * 86400
    for kind in ("warned", "baseline"):
        for f in state_file(kind, "x").parent.glob("*"):
            if f.is_file() and f.stat().st_mtime < limit:
                f.unlink()


def project_root(data):
    return find_root(Path(os.environ.get("CLAUDE_PROJECT_DIR") or data["cwd"]).resolve())


def session_start(data):
    root = project_root(data)
    if not root:
        return None
    rules = (PLUGIN_ROOT / "shared" / "core-rules.md").read_text(encoding="utf-8")
    specs = active_specs(root)
    try:
        sid = data.get("session_id")
        # 압축은 같은 세션이 이어지는 것이므로 기준을 유지한다.
        if data.get("source") != "compact" or not load_baseline(sid, root):
            save_baseline(sid, root, bool(specs))
        cleanup()
    except (OSError, subprocess.SubprocessError):
        pass  # 비교 기준이 없어도 규칙은 주입한다.
    current = "\n".join("- " + s for s in specs) if specs else "- 없음"
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{rules}\n## 진행 중인 스펙\n{current}\n",
        }
    }


def subagent_start(data):
    root = project_root(data)
    specs = active_specs(root) if root else []
    if not specs:
        return None
    rules = (PLUGIN_ROOT / "shared" / "core-rules.md").read_text(encoding="utf-8")
    current = "\n".join("- " + s for s in specs)
    return {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": (
                f"{rules}\n## 진행 중인 스펙\n{current}\n\n## 서브에이전트\n"
                "맡은 일이 위 스펙과 관련될 때 적용한다. 스펙 문서의 작성을 맡지 않았다면 `plan.md`와 `decisions.md`를 "
                "직접 고치지 않고, 새로 내린 결정, 사람의 선택이 필요한 결정, 스펙과의 불일치를 결과와 함께 메인 세션에 보고한다.\n"
            ),
        }
    }


def pre_tool_use(data):
    ti = data.get("tool_input") or {}
    raw = ti.get("file_path") or ti.get("notebook_path")
    if not raw:
        return None
    path = (Path(data.get("cwd") or ".") / raw).resolve()
    root = find_root(path.parent)
    if not root or not is_code(path, root) or active_specs(root):
        return None
    if not first_time(data.get("session_id")):
        return None
    return {
        "systemMessage": f"[SDD] 진행 중인 스펙 없이 코드를 수정합니다: {path.relative_to(root).as_posix()}",
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "[SDD] 진행 중인 스펙 없이 코드를 수정하고 있다. 작업은 계속하되, 사소한 수정이 아니라면 "
                "/naver-like-sdd:spec 으로 의도와 결정을 남기도록 사용자에게 제안한다."
            ),
        },
    }


def stop(data):
    root = project_root(data)
    if not root:
        return None
    sid = data.get("session_id")
    state = load_baseline(sid, root)
    active = bool(active_specs(root))
    # 스펙이 진행 중이거나 이번 응답에서 막 끝났다면 변경은 그 스펙에 속한 것으로 본다.
    if active or state is None or state["active"]:
        if state is None or not (active and state["active"]):
            save_baseline(sid, root, active)
        return None
    if state_file("warned", sid).exists():
        return None
    names = changed_code(state, root)
    if not names or not first_time(sid):
        return None
    more = f" 외 {len(names) - 3}개" if len(names) > 3 else ""
    return {
        "systemMessage": (
            f"[SDD] 진행 중인 스펙 없이 코드가 바뀌었습니다: {', '.join(names[:3])}{more}. "
            "남길 의도나 결정이 있으면 /naver-like-sdd:spec 을 사용하세요."
        )
    }


def main():
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    handler = {"SessionStart": session_start, "SubagentStart": subagent_start, "PreToolUse": pre_tool_use, "Stop": stop}.get(data.get("hook_event_name"))
    out = handler(data) if handler else None
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"naver-like-sdd hook skipped: {e}", file=sys.stderr)
    sys.exit(0)
