#!/usr/bin/env python3
"""
score_promotion.py — Phase 2 MVP

Updates ~/dev/personal-skills/data/promotion_state.json for the rubric lines that
can be scored from the shell:

  - engineering.code_review  via `gh search prs reviewed-by:VashisthaCT`
  - org.mentoring            via line-count heuristic on data/mentees.yaml
  - ai.competency            via line-count heuristic on data/ai_tooling.yaml

For Drive/Slack-only lines (engineering.lld, org.communication) it leaves
`status` unchanged and writes a `current.note` telling the user to run
`/v-promo-tracker` from a Claude session (which delegates to the
promo-evidence-scorer subagent).

Stdlib only (Python 3.9 ships on macOS by default). No PyYAML.

Run:
    python3 ~/dev/personal-skills/scripts/score_promotion.py --dry-run
    python3 ~/dev/personal-skills/scripts/score_promotion.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = REPO_ROOT / "data" / "promotion_state.json"
MENTEES_PATH = REPO_ROOT / "data" / "mentees.yaml"
AI_TOOLING_PATH = REPO_ROOT / "data" / "ai_tooling.yaml"

# Lines this script handles end-to-end. Everything else is left for the
# Claude-session subagent (Drive/Slack searches require MCP, not subprocess).
SCRIPTABLE_IDS = {
    "engineering.code_review",
    "org.mentoring",
    "ai.competency",
}
AGENT_REQUIRED_IDS = {
    "engineering.lld",
    "org.communication",
}


# ---------- helpers ----------------------------------------------------------

def now_iso_ist() -> str:
    """ISO-8601 timestamp with +05:30 offset, matching existing schema examples."""
    return datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(timespec="seconds")


def status_emoji(current: int, threshold: int) -> str:
    """Map (current, threshold) → emoji status the rest of the OS reads.

    🔴 < 30%   not started / very thin
    🟡 30-99%  on track but below threshold
    🟢 ≥ 100%  meets or exceeds threshold
    """
    if threshold <= 0:
        return "🟡 below threshold"
    ratio = current / threshold
    if ratio >= 1.0:
        return f"🟢 meets threshold ({current}/{threshold})"
    if ratio < 0.3:
        return f"🔴 not started ({current}/{threshold})"
    return f"🟡 below threshold ({current}/{threshold})"


# ---------- score: engineering.code_review ----------------------------------

def score_code_review(cycle_start: str) -> Tuple[Dict[str, Any], str]:
    """Use `gh search prs` to count substantive reviews authored by user.

    Substantive = ≥5 review comments (per data_source.filter in the schema).
    `gh` can't filter by comment count directly, so we fetch candidates then
    fetch comment counts per PR. Best-effort; rate-limited to 50 PRs.
    """
    cycle_start_iso = cycle_start  # YYYY-MM-DD already
    query = (
        f"is:pr -author:VashisthaCT reviewed-by:VashisthaCT created:>={cycle_start_iso}"
    )
    cmd = [
        "gh", "search", "prs",
        "--reviewed-by", "VashisthaCT",
        "--created", f">={cycle_start_iso}",
        "--limit", "50",
        "--json", "url,repository,author,number,title",
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=60,
        )
    except subprocess.CalledProcessError as e:
        return (
            {"substantive_reviews": 0, "distinct_authors": [], "repos": [],
             "evidence": [],
             "error": f"gh search failed: {e.stderr.strip()[:200]}"},
            "🟡 below threshold (gh error)",
        )
    except FileNotFoundError:
        return (
            {"substantive_reviews": 0, "distinct_authors": [], "repos": [],
             "evidence": [], "error": "gh CLI not found in PATH"},
            "🟡 below threshold (gh missing)",
        )

    try:
        prs = json.loads(out.stdout) if out.stdout.strip() else []
    except json.JSONDecodeError:
        prs = []

    substantive = 0
    authors: List[str] = []
    repos: List[str] = []
    evidence: List[Dict[str, Any]] = []

    for pr in prs:
        url = pr.get("url") or ""
        author = (pr.get("author") or {}).get("login")
        repo = (pr.get("repository") or {}).get("nameWithOwner")
        if not url or not author or not repo:
            continue

        # Fetch user-authored review comments on this PR. Conservative: count
        # review-comments authored by VashisthaCT; ≥5 = substantive.
        view_cmd = [
            "gh", "pr", "view", url,
            "--json", "reviews,comments",
        ]
        try:
            v = subprocess.run(
                view_cmd, capture_output=True, text=True, check=True, timeout=30,
            )
            data = json.loads(v.stdout) if v.stdout.strip() else {}
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                json.JSONDecodeError):
            continue

        my_comments = 0
        for r in data.get("reviews", []) or []:
            a = (r.get("author") or {}).get("login")
            if a == "VashisthaCT" and (r.get("body") or "").strip():
                my_comments += 1
        for c in data.get("comments", []) or []:
            a = (c.get("author") or {}).get("login")
            if a == "VashisthaCT":
                my_comments += 1

        if my_comments >= 5:
            substantive += 1
            if author not in authors:
                authors.append(author)
            if repo not in repos:
                repos.append(repo)
            evidence.append({
                "url": url,
                "author": author,
                "repo": repo,
                "user_comment_count": my_comments,
            })

    threshold_count = 10
    current = {
        "substantive_reviews": substantive,
        "distinct_authors": authors,
        "repos": repos,
        "evidence": evidence[:10],  # cap to keep file small
    }

    # Composite gate: ≥10 reviews AND ≥3 authors AND ≥2 repos.
    meets = substantive >= 10 and len(authors) >= 3 and len(repos) >= 2
    if meets:
        status = f"🟢 meets threshold ({substantive}/10, {len(authors)} authors, {len(repos)} repos)"
    else:
        status = status_emoji(substantive, threshold_count)
    return current, status


# ---------- score: org.mentoring --------------------------------------------

def _yaml_count_list_items(path: Path, list_key: str) -> Tuple[int, List[Dict[str, Any]]]:
    """Cheap structural read of `<list_key>: [...]` shaped YAML.

    Returns (count, [{"id": ..., "touchpoint_count": N}]). Counts list-of-mapping
    entries by matching `^  - id:` (two-space indent, mentees.yaml schema). For
    each entry, counts touchpoints by matching subsequent `^      - date:` lines
    (six-space indent for nested list-of-mappings) until the next `^  - id:` or
    EOF.
    """
    if not path.exists():
        return 0, []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Skip lines that are inside a comment region (start with `#` after stripping
    # leading whitespace) — covers the example block in mentees.yaml.
    code_lines: List[str] = []
    for ln in lines:
        stripped = ln.lstrip()
        if stripped.startswith("#"):
            continue
        code_lines.append(ln)

    # Find `<list_key>:` then walk children at deeper indent.
    in_section = False
    section_indent = -1
    entries: List[List[str]] = []
    current: Optional[List[str]] = None

    for ln in code_lines:
        if not in_section:
            if re.match(rf"^{re.escape(list_key)}\s*:\s*\[\s*\]\s*$", ln):
                return 0, []
            if re.match(rf"^{re.escape(list_key)}\s*:\s*$", ln):
                in_section = True
                section_indent = 0
            continue

        # In section. Find list items.
        m = re.match(r"^(\s*)- id:\s*(.+?)\s*$", ln)
        if m and len(m.group(1)) > section_indent:
            if current is not None:
                entries.append(current)
            current = [ln]
            continue
        # Continuation of current entry.
        if current is not None:
            # Bail out of section if a non-indented line appears.
            if ln and not ln.startswith(" "):
                entries.append(current)
                current = None
                in_section = False
                continue
            current.append(ln)

    if current is not None:
        entries.append(current)

    summaries: List[Dict[str, Any]] = []
    for e in entries:
        # First line is `  - id: <value>`
        m = re.match(r"^\s*- id:\s*(.+?)\s*$", e[0])
        ident = m.group(1) if m else "?"
        touchpoints = sum(1 for l in e[1:] if re.match(r"^\s+- date:", l))
        summaries.append({"id": ident, "touchpoint_count": touchpoints})

    return len(summaries), summaries


def score_mentoring() -> Tuple[Dict[str, Any], str]:
    count, summaries = _yaml_count_list_items(MENTEES_PATH, "mentees")
    qualifying = [s for s in summaries if s["touchpoint_count"] >= 10]
    current = {
        "mentees": count,
        "touchpoints_per_mentee": [s["touchpoint_count"] for s in summaries],
        "evidence": summaries,
    }
    # Threshold: ≥2 named mentees, each with ≥10 touchpoints.
    if len(qualifying) >= 2:
        status = f"🟢 meets threshold ({len(qualifying)} qualifying mentees)"
    elif count == 0:
        status = "🔴 not started (0 mentees logged)"
    else:
        status = (
            f"🟡 below threshold ({count} mentees, "
            f"{len(qualifying)} with ≥10 touchpoints)"
        )
    return current, status


# ---------- score: ai.competency --------------------------------------------

def score_ai_competency() -> Tuple[Dict[str, Any], str]:
    """Counts `tools:` entries + signals from ai_tooling.yaml.

    Threshold (L4): ≥3 timed features + ≥1 workflow doc + ≥1 multi-step agent
    workflow live. Only the agent-workflows count is measurable from the file;
    timed-features + workflow-docs require the user logging via /v-timed-feature
    (Phase 6) — flag as manual until then.
    """
    tools_count, _ = _yaml_count_list_items(AI_TOOLING_PATH, "tools")
    # personal-skills repo itself counts as 1 live agent workflow.
    agent_workflows_live = 1 if tools_count >= 1 else 0

    current = {
        "timed_features_logged": 0,
        "workflow_docs": 0,
        "agent_workflows_live": agent_workflows_live,
        "evidence": ["personal-skills repo itself"] if agent_workflows_live else [],
        "note": (
            "timed_features_logged + workflow_docs require /v-timed-feature "
            "(Phase 6). Manual override: edit promotion_state.json directly."
        ),
    }
    # L4 threshold = ≥3 timed features + ≥1 workflow doc + ≥1 live agent workflow.
    # We only know live-agent count from the file; the other two are 0 until
    # /v-timed-feature lands. So: never auto-promote past L3-trending-L4 from
    # the script. User must manually flip when they have evidence.
    timed_features_logged = current["timed_features_logged"]
    workflow_docs = current["workflow_docs"]
    if (timed_features_logged >= 3 and workflow_docs >= 1
            and agent_workflows_live >= 1):
        status = "🟢 L4 mastering"
    else:
        status = "🟡 L3 trending L4"
    return current, status


# ---------- main loop -------------------------------------------------------

def update_line(line: Dict[str, Any], cycle_start: str) -> Tuple[bool, str]:
    """Mutates `line` in place. Returns (changed, status_before)."""
    rid = line.get("id")
    status_before = line.get("status", "")

    if rid == "engineering.code_review":
        current, new_status = score_code_review(cycle_start)
    elif rid == "org.mentoring":
        current, new_status = score_mentoring()
    elif rid == "ai.competency":
        current, new_status = score_ai_competency()
    elif rid in AGENT_REQUIRED_IDS:
        # Don't change status. Just leave a breadcrumb.
        prev = line.get("current") or {}
        prev["note"] = (
            "requires Claude session — run /v-promo-tracker (delegates to "
            "promo-evidence-scorer subagent for Drive/Slack searches)"
        )
        line["current"] = prev
        return False, status_before
    else:
        # Out of MVP scope. Leave untouched.
        return False, status_before

    line["current"] = current
    line["status"] = new_status
    return new_status != status_before, status_before


def main() -> int:
    p = argparse.ArgumentParser(description="Score promotion rubric lines.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would change; don't write the file.")
    p.add_argument("--state", default=str(STATE_PATH),
                   help="Path to promotion_state.json")
    args = p.parse_args()

    state_path = Path(args.state)
    if not state_path.exists():
        print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
        return 2

    state = json.loads(state_path.read_text(encoding="utf-8"))
    cycle_start = state.get("cycle_start", "2026-04-01")

    changes: List[str] = []
    skipped: List[str] = []
    deferred: List[str] = []

    for line in state.get("rubric_lines", []):
        rid = line.get("id")
        if rid in SCRIPTABLE_IDS:
            changed, before = update_line(line, cycle_start)
            after = line.get("status", "")
            arrow = f"{before} → {after}" if changed else f"{after} (unchanged)"
            changes.append(f"  [{rid}] {arrow}")
            ts = now_iso_ist()
            if changed:
                line.setdefault("history", []).append({
                    "evaluated_at": ts,
                    "from_status": before,
                    "to_status": after,
                })
            line["last_evaluated"] = ts
        elif rid in AGENT_REQUIRED_IDS:
            update_line(line, cycle_start)
            deferred.append(f"  [{rid}] left for Claude-session subagent")
            # Don't touch last_evaluated for agent-required lines — the agent does it.
        else:
            skipped.append(f"  [{rid}] out of MVP scope")

    state["last_evaluated"] = now_iso_ist()

    print("Scriptable lines:")
    for c in changes:
        print(c)
    print()
    print("Agent-required (run /v-promo-tracker in a Claude session):")
    for d in deferred:
        print(d)
    print()
    print("Skipped (out of MVP scope, will wire in later phases):")
    for s in skipped:
        print(s)
    print()

    if args.dry_run:
        print("--dry-run: NOT writing state file.")
        return 0

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    print(f"Wrote: {state_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
