#!/usr/bin/env python3
"""ux.py - deterministic helper shared by the user-types and tool-for-users skills.

Run from the repository root (or pass --root PATH). Python 3.8+, standard library only.

Commands
  status                  What exists under UX/: user-types, next free ID, tool docs, git state.
  scan                    Collect evidence about user-types from the repository.
  init [--force]          Create UX/User_Types.md from the template.
  init-tool SLUG NAME     Create UX/tools/SLUG.md from the template.
  refs UT-ID [UT-ID ...]  Show which tool docs, features, journeys and coverage rows use a user-type.
  sync                    Regenerate the generated blocks (index, mapped features, journey flowcharts, ID trackers).
  check [SLUG]            Validate User_Types.md and the tool docs (or one). Exit code 1 on errors.

The exact file format is described in references/file-format.md next to this script's skill.
"""
import argparse
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

UX_DIR = "UX"
TYPES_NAME = "User_Types.md"
TOOLS_DIR = "tools"

PRIORITY = {"M": "Must", "S": "Should", "C": "Could", "W": "Won't"}
ACCESS_LEVELS = ["Anonymous", "Signed-in", "Elevated", "Admin", "System"]
OUTCOMES = ["Success", "Partial", "Abandoned", "Error", "Blocked"]
DECISIONS = ["Served elsewhere", "Out of scope", "Open"]
MAP_VALUES = {"P", "S", "", "-", "–", "—"}

UT_HEAD_RE = re.compile(r"^##\s+(UT-\d{2,})\s*[·:|\-–—]\s*(.+?)\s*$")
UT_ID_RE = re.compile(r"\bUT-\d{2,}\b")
REQ_ID_RE = re.compile(r"\b(?:UT-\d{2,}|BL)-[MSCW]\d+\b")
UT_REQ_FULL_RE = re.compile(r"^(UT-\d{2,})-([MSCW])(\d+)$")
BL_REQ_FULL_RE = re.compile(r"^BL-([MSCW])(\d+)$")
F_ID_RE = re.compile(r"\bF-\d{2,}\b")
J_ID_RE = re.compile(r"\bJ-\d{2,}\b")
H2_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$")
FIELD_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")
SEP_CELL_RE = re.compile(r"^:?-{2,}:?$")
LAST_UT_RE = re.compile(r"<!--\s*ux:last-ut:\s*(\d+)\s*-->")
LAST_IDS_RE = re.compile(r"<!--\s*ux:last-ids:\s*F=(\d+)\s+J=(\d+)\s*-->")
DETAIL_RE = re.compile(r"^####\s+(J-\d{2,})\b")


# --------------------------------------------------------------------------- markdown helpers

def split_row(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def tables(lines, offset=0):
    """Return [(header_cells, [(line_no, cells), ...], header_line_no)] for every table in lines."""
    out, i = [], 0
    while i < len(lines):
        head = split_row(lines[i])
        if head is not None and i + 1 < len(lines):
            sep = split_row(lines[i + 1])
            if sep and all(SEP_CELL_RE.match(c) for c in sep if c) and any(sep):
                rows, j = [], i + 2
                while j < len(lines):
                    r = split_row(lines[j])
                    if r is None:
                        break
                    rows.append((offset + j, r))
                    j += 1
                out.append((head, rows, offset + i))
                i = j
                continue
        i += 1
    return out


def h2_sections(lines):
    """[(title_lower, start, end)] for every '## ' heading outside code fences."""
    idx, fence = [], False
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            fence = not fence
        elif not fence and l.startswith("## "):
            idx.append(i)
    res = []
    for k, i in enumerate(idx):
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        m = H2_RE.match(lines[i])
        res.append(((m.group(1) if m else lines[i][3:]).strip().lower(), i, end))
    return res


def cell(row, i):
    return row[i].strip() if i is not None and i < len(row) else ""


def col_index(header, *names):
    low = [h.strip().lower() for h in header]
    for n in names:
        for i, h in enumerate(low):
            if h == n:
                return i
    for n in names:
        for i, h in enumerate(low):
            if h.startswith(n):
                return i
    return None


def set_block(text, key, content):
    start, end = f"<!-- ux:{key}:start -->", f"<!-- ux:{key}:end -->"
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    new = f"{start}\n{content}\n{end}"
    if pat.search(text):
        return pat.sub(lambda m: new, text, count=1), True
    return text, False


def num(id_):
    return int(id_.split("-")[-1]) if id_ else 0


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


# --------------------------------------------------------------------------- loading

def types_path(root):
    return root / UX_DIR / TYPES_NAME


def find_alternative_types_file(root):
    ux = root / UX_DIR
    if not ux.is_dir():
        return None
    for p in sorted(ux.iterdir()):
        if p.is_file() and p.name != TYPES_NAME and re.match(r"^user[_\- ]?types?\.md$", p.name, re.I):
            return p
    return None


def load_types(root):
    p = types_path(root)
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    types, baseline = [], []
    for title, s, e in h2_sections(lines):
        block = lines[s + 1:e]
        m = UT_HEAD_RE.match(lines[s])
        if not m:
            if title.startswith("baseline"):
                for _, rows, _ in tables(block, s + 1):
                    for ln, r in rows:
                        if r and BL_REQ_FULL_RE.match(r[0]):
                            baseline.append({"id": r[0], "priority": cell(r, 1), "text": cell(r, 2), "line": ln + 1})
            continue
        reqs, fields = [], {}
        for _, rows, _ in tables(block, s + 1):
            for ln, r in rows:
                if r and re.match(r"^UT-\d{2,}-[MSCW]\d+$", r[0]):
                    reqs.append({"id": r[0], "priority": cell(r, 1), "text": cell(r, 2), "line": ln + 1})
        for l in block:
            fm = FIELD_RE.match(l.strip())
            if fm:
                fields[fm.group(1).strip().lower()] = fm.group(2).strip()
        types.append({"id": m.group(1), "name": m.group(2), "line": s + 1, "start": s, "end": e,
                      "reqs": reqs, "fields": fields})
    lm = LAST_UT_RE.search(text)
    return {"path": p, "text": text, "lines": lines, "types": types, "baseline": baseline,
            "last_ut": int(lm.group(1)) if lm else 0, "has_last": bool(lm)}


def tool_paths(root):
    d = root / UX_DIR / TOOLS_DIR
    return sorted(d.glob("*.md")) if d.is_dir() else []


def load_tool(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = None
    for l in lines:
        if l.startswith("# "):
            title = re.sub(r"^#\s+(?:Tool:\s*)?", "", l).strip()
            break
    secs = h2_sections(lines)

    def sec(prefix):
        for t, s, e in secs:
            if t.startswith(prefix):
                return s, e
        return None

    tool = {"path": path, "slug": path.stem, "title": title or path.stem, "text": text, "lines": lines,
            "sections": {}, "features": OrderedDict(), "map": OrderedDict(), "map_cols": [],
            "coverage": [], "journeys": [], "details": set(), "warnings_parse": []}
    for key, prefix in [("summary", "summary"), ("features", "features"), ("map", "feature map"),
                        ("coverage", "coverage"), ("journeys", "journeys")]:
        tool["sections"][key] = sec(prefix)

    s = tool["sections"]["features"]
    if s:
        for head, rows, _ in tables(lines[s[0] + 1:s[1]], s[0] + 1):
            ci_serves = col_index(head, "serves")
            ci_name = col_index(head, "feature", "name")
            ci_what = col_index(head, "what it does", "description")
            for ln, r in rows:
                if r and re.match(r"^F-\d{2,}$", r[0]):
                    tool["features"].setdefault(r[0], {
                        "id": r[0], "name": cell(r, ci_name if ci_name is not None else 1),
                        "what": cell(r, ci_what), "serves": REQ_ID_RE.findall(cell(r, ci_serves)),
                        "line": ln + 1, "dupe": False})
                    if tool["features"][r[0]]["line"] != ln + 1:
                        tool["features"][r[0]]["dupe"] = True
            break

    s = tool["sections"]["map"]
    if s:
        for head, rows, _ in tables(lines[s[0] + 1:s[1]], s[0] + 1):
            cols = [(i, UT_ID_RE.search(h).group(0)) for i, h in enumerate(head) if UT_ID_RE.search(h)]
            if not cols:
                continue
            tool["map_cols"] = [u for _, u in cols]
            for ln, r in rows:
                fm = F_ID_RE.search(r[0]) if r else None
                if not fm:
                    continue
                tool["map"][fm.group(0)] = {"line": ln + 1,
                                            "cells": {u: cell(r, i).upper() for i, u in cols}}
            break

    s = tool["sections"]["coverage"]
    if s:
        for head, rows, _ in tables(lines[s[0] + 1:s[1]], s[0] + 1):
            ci_dec = col_index(head, "decision")
            for ln, r in rows:
                rm = REQ_ID_RE.search(r[0]) if r else None
                if rm:
                    tool["coverage"].append({"req": rm.group(0), "decision": cell(r, ci_dec if ci_dec is not None else 1),
                                             "line": ln + 1})
            break

    s = tool["sections"]["journeys"]
    if s:
        block = lines[s[0] + 1:s[1]]
        for head, rows, _ in tables(block, s[0] + 1):
            ci = {k: col_index(head, *names) for k, names in {
                "id": ("id",), "type": ("user type", "type"), "intent": ("intent",), "entry": ("entry", "arrival"),
                "path": ("path", "use"), "outcome": ("outcome",), "after": ("after",),
                "variant": ("variant of", "variant"), "context": ("context",)}.items()}
            if ci["id"] is None or ci["path"] is None:
                continue
            for ln, r in rows:
                if not r or not re.match(r"^J-\d{2,}$", cell(r, ci["id"])):
                    continue
                j = {k: cell(r, i) for k, i in ci.items()}
                um = UT_ID_RE.search(j["type"])
                j["ut"] = um.group(0) if um else None
                j["path_ids"] = F_ID_RE.findall(j["path"])
                vm = J_ID_RE.search(j["variant"])
                j["variant_id"] = vm.group(0) if vm else None
                j["line"] = ln + 1
                tool["journeys"].append(j)
            break
        for l in block:
            dm = DETAIL_RE.match(l)
            if dm:
                tool["details"].add(dm.group(1))

    lm = LAST_IDS_RE.search(text)
    tool["last_f"] = int(lm.group(1)) if lm else 0
    tool["last_j"] = int(lm.group(2)) if lm else 0
    return tool


def load_tools(root, slug=None):
    out = []
    for p in tool_paths(root):
        if slug and p.stem != slug:
            continue
        out.append(load_tool(p))
    return out


def mapped_types(tool):
    used = OrderedDict()
    for fid, m in tool["map"].items():
        for u, v in m["cells"].items():
            if v in ("P", "S"):
                used.setdefault(u, []).append((fid, v))
    return used


# --------------------------------------------------------------------------- git

def git_state(root, rel):
    try:
        r = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", rel],
                           capture_output=True, text=True, timeout=15)
    except Exception:
        return "not a git repository (or git unavailable)"
    if r.returncode != 0:
        return "not a git repository"
    out = r.stdout.strip()
    if not out:
        return "committed, no local changes"
    if out.startswith("??"):
        return "UNCOMMITTED: file is not tracked by git yet"
    return "UNCOMMITTED: file has local changes git has no copy of"


# --------------------------------------------------------------------------- templates

TYPES_TEMPLATE = """# User Types

<!-- Maintained with the user-types skill. Edit freely, but keep the IDs, headings and ux: markers.
     Everything between ux: start/end markers is regenerated by `ux.py sync`. -->
<!-- ux:last-ut: 0 -->

## Index

<!-- ux:index:start -->
_No user-types yet._
<!-- ux:index:end -->

## Baseline requirements

Every human user-type inherits these. They are not repeated in the profiles and are not part of the coverage check.

| ID | Priority | Requirement |
|---|---|---|
| BL-M1 | Must | Usable with keyboard and screen reader; meets WCAG 2.2 AA. |
| BL-M2 | Must | Works on a phone-sized screen as well as on desktop. |
| BL-M3 | Must | Errors say what went wrong and how to fix it, without losing what the user entered. |
| BL-M4 | Must | Personal data is collected only when needed and handled per applicable privacy law (e.g. GDPR consent for non-essential tracking). |
| BL-S1 | Should | Usable on a slow connection: main content appears within about 3 seconds on 4G. |
| BL-S2 | Should | Plain language that non-native speakers can follow. |
"""

TOOL_TEMPLATE = """# Tool: {name}

<!-- Maintained with the tool-for-users skill. Everything between ux: start/end markers is regenerated by `ux.py sync`. -->
<!-- ux:last-ids: F=0 J=0 -->

## 1. Summary

| Field | Value |
|---|---|
| Purpose | |
| Problem it solves | |
| Target users (as requested) | |
| Platform & context | |
| Constraints & out of scope | |
| Status | Draft: features and mapping awaiting review |

## 2. Features

| ID | Feature | What it does | Serves |
|---|---|---|---|

## 3. Feature map

P = primary user of the feature, S = secondary or occasional user, blank = does not use it.

| Feature |
|---|

## 4. Coverage

Must-requirements of the mapped user-types that no feature serves, and what was decided about each.

| Requirement | Decision | Note |
|---|---|---|

## 5. Journeys

### Journey index

| ID | User type | Intent | Entry | Path | Outcome | After | Variant of | Context |
|---|---|---|---|---|---|---|---|---|

### Journey flows

<!-- ux:flows:start -->
_Generated by `ux.py sync` from the journey index._
<!-- ux:flows:end -->

### Journey details
"""


# --------------------------------------------------------------------------- commands

def cmd_status(root, args):
    ux = root / UX_DIR
    print(f"Repository root: {root}")
    print(f"UX folder: {'present' if ux.is_dir() else 'missing'}")
    t = load_types(root)
    alt = find_alternative_types_file(root)
    if t is None:
        if alt:
            print(f"User types file: MISSING ({UX_DIR}/{TYPES_NAME}); found alternative name: {alt.relative_to(root)}")
        else:
            print(f"User types file: MISSING ({UX_DIR}/{TYPES_NAME})")
    else:
        print(f"User types file: {UX_DIR}/{TYPES_NAME} ({len(t['types'])} user-types)")
        if alt:
            print(f"  Note: another user-types file also exists: {alt.relative_to(root)}")
        for ty in t["types"]:
            musts = sum(1 for r in ty["reqs"] if UT_REQ_FULL_RE.match(r["id"]) and UT_REQ_FULL_RE.match(r["id"]).group(2) == "M")
            print(f"  {ty['id']} · {ty['name']} | access: {ty['fields'].get('access level', '?')} | "
                  f"based on: {ty['fields'].get('based on', '?')} | requirements: {len(ty['reqs'])} ({musts} Must)")
        top = max([t["last_ut"]] + [num(x["id"]) for x in t["types"]])
        print(f"Next user-type ID: UT-{top + 1:02d}")
        print(f"Git state of {UX_DIR}/{TYPES_NAME}: {git_state(root, f'{UX_DIR}/{TYPES_NAME}')}")
    tools = load_tools(root)
    print(f"Tool docs ({len(tools)}):" if tools else "Tool docs: none")
    for tool in tools:
        nf = max([tool["last_f"]] + [num(f) for f in tool["features"]])
        nj = max([tool["last_j"]] + [num(j["id"]) for j in tool["journeys"]])
        main = sum(1 for j in tool["journeys"] if not j["variant_id"])
        print(f"  {tool['slug']}: \"{tool['title']}\" | features {len(tool['features'])} | "
              f"user-types {', '.join(mapped_types(tool)) or '-'} | journeys {len(tool['journeys'])} "
              f"({main} main) | next IDs F-{nf + 1:02d}, J-{nj + 1:02d}")
    return 0


SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "vendor", ".venv", "venv",
             "__pycache__", "coverage", ".turbo", ".vercel", ".svelte-kit", "target", ".cache", ".idea",
             ".vscode", "bin", "obj", ".output", ".pnpm-store", "UX"}
CODE_EXT = {".sql", ".prisma", ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".rb", ".php", ".go", ".cs",
            ".java", ".kt", ".toml", ".yaml", ".yml", ".json", ".graphql", ".gql", ".vue", ".svelte", ".astro"}
SKIP_FILES_RE = re.compile(r"(lock|\.min\.)", re.I)
ROLE_LINE_RE = re.compile(
    r"(?i)(role[s]?\b|\benum\b|\buser_?types?\b|\bpermissions?\b|\bis_?admin\b|\bis_?staff\b|\bsuperuser\b|"
    r"\bcreate\s+policy\b|\bgrant\s+\w+\s+on\b|\bauth\.(uid|role|jwt)\b|\bhas_?role\b|\bcan_?\w+\b\s*[:=(])")
ROLE_WORD_RE = re.compile(r"['\"`]([a-z][a-z0-9_\-]{2,24})['\"`]")
ROLE_STOP = {"text", "string", "boolean", "number", "true", "false", "null", "default", "public", "select", "insert",
             "update", "delete", "authenticated", "anon", "service_role", "uuid", "json", "jsonb", "role", "roles",
             "type", "name", "id", "user_id", "created_at", "updated_at", "all", "none", "read", "write", "use client",
             "use server", "permission", "permissions", "utf-8", "utf8", "get", "post", "put", "patch"}
DOC_NAMES = ["README.md", "README", "readme.md", "CLAUDE.md", "AGENTS.md", "AGENT.md", "CONTRIBUTING.md"]
PERSONA_RE = re.compile(r"(persona|user[-_ ]?types?|roles?|audience|stakeholders?|target[-_ ]?users?)", re.I)
ROUTE_DIRS = ["app", "src/app", "pages", "src/pages", "src/routes", "routes", "app/routes", "src/views", "views"]


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in (".github",))
        for f in sorted(filenames):
            yield Path(dirpath) / f


def cmd_scan(root, args):
    rel = lambda p: str(p.relative_to(root))
    print("== Docs at the root")
    found = [n for n in DOC_NAMES if (root / n).exists()]
    print("  " + ("; ".join(found) if found else "none"))
    docs, personas, evidence, words = [], [], [], Counter()
    per_file = Counter()
    for p in walk(root):
        r = rel(p)
        if r.startswith("docs/") and p.suffix.lower() in (".md", ".mdx"):
            docs.append(r)
        if PERSONA_RE.search(p.stem) and p.suffix.lower() in (".md", ".mdx", ".txt", ".yaml", ".yml", ".json"):
            personas.append(r)
        if p.suffix.lower() not in CODE_EXT or SKIP_FILES_RE.search(p.name):
            continue
        try:
            if p.stat().st_size > 1_000_000:
                continue
            content = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(content):
            if ROLE_LINE_RE.search(line):
                for w in ROLE_WORD_RE.findall(line):
                    w = w.strip().lower()
                    if w not in ROLE_STOP:
                        words[w] += 1
                if per_file[r] < 6 and len(evidence) < 160:
                    evidence.append(f"  {r}:{i + 1}: {line.strip()[:150]}")
                    per_file[r] += 1
    print(f"== docs/ markdown files ({len(docs)})")
    for d in docs[:40]:
        print("  " + d)
    if len(docs) > 40:
        print(f"  ... {len(docs) - 40} more")
    print(f"== Persona / role / audience files ({len(personas)})")
    for d in personas[:30]:
        print("  " + d)
    print(f"== Role and permission evidence ({len(evidence)} lines, max 6 per file)")
    print("\n".join(evidence) if evidence else "  none found")
    print("== Candidate role names (quoted words on role/permission lines, by frequency)")
    common = [f"{w} ({c})" for w, c in words.most_common(25)]
    print("  " + ("; ".join(common) if common else "none"))
    print("== Route folders")
    any_route = False
    for d in ROUTE_DIRS:
        rd = root / d
        if rd.is_dir():
            names = sorted(x.name for x in rd.iterdir() if not x.name.startswith((".", "_")))
            print(f"  {d}/: " + ", ".join(names[:50]))
            any_route = True
    if not any_route:
        print("  none of: " + ", ".join(ROUTE_DIRS))
    pkg = root / "package.json"
    if pkg.exists():
        m = re.search(r'"description"\s*:\s*"([^"]*)"', pkg.read_text(encoding="utf-8", errors="ignore"))
        if m and m.group(1):
            print(f"== package.json description: {m.group(1)}")
    return 0


def cmd_init(root, args):
    p = types_path(root)
    if p.exists() and not args.force:
        print(f"{UX_DIR}/{TYPES_NAME} already exists; use --force to overwrite it.")
        return 1
    p.parent.mkdir(parents=True, exist_ok=True)
    last = 0
    if p.exists():
        old = load_types(root)
        last = max([old["last_ut"]] + [num(t["id"]) for t in old["types"]])
    p.write_text(TYPES_TEMPLATE.replace("ux:last-ut: 0", f"ux:last-ut: {last}"), encoding="utf-8")
    print(f"Created {UX_DIR}/{TYPES_NAME} (ID tracker at UT-{last:02d}; next new type is UT-{last + 1:02d}).")
    return 0


def cmd_init_tool(root, args):
    slug = args.slug
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        print(f"Slug must be kebab-case (lowercase letters, digits, hyphens): {slug}")
        return 1
    p = root / UX_DIR / TOOLS_DIR / f"{slug}.md"
    if p.exists() and not args.force:
        print(f"{p.relative_to(root)} already exists; use --force to overwrite it.")
        return 1
    p.parent.mkdir(parents=True, exist_ok=True)
    t = load_types(root)
    text = TOOL_TEMPLATE.replace("{name}", args.name)
    p.write_text(text, encoding="utf-8")
    print(f"Created {p.relative_to(root)}.")
    if t and t["types"]:
        print("Add a Feature map column per mapped user-type, e.g. | Feature | UT-01 Visitor | UT-02 Member |")
    return 0


def cmd_refs(root, args):
    t = load_types(root)
    names = {x["id"]: x["name"] for x in (t["types"] if t else [])}
    rc = 0
    for ut in args.ids:
        if not re.match(r"^UT-\d{2,}$", ut):
            print(f"Not a user-type ID: {ut}")
            rc = 1
            continue
        print(f"== {ut} · {names.get(ut, '(not in User_Types.md)')}")
        any_ref = False
        for tool in load_tools(root):
            feats = [(f, m["cells"].get(ut)) for f, m in tool["map"].items() if m["cells"].get(ut) in ("P", "S")]
            js = [j["id"] for j in tool["journeys"] if j["ut"] == ut]
            reqs_served = sorted({r for f in tool["features"].values() for r in f["serves"] if r.startswith(ut + "-")})
            cov = [c["req"] for c in tool["coverage"] if c["req"].startswith(ut + "-")]
            col = ut in tool["map_cols"]
            if not (feats or js or reqs_served or cov or col):
                continue
            any_ref = True
            print(f"  {UX_DIR}/{TOOLS_DIR}/{tool['slug']}.md (\"{tool['title']}\")")
            print("    features: " + (", ".join(f"{f} {tool['features'].get(f, {}).get('name', '?')} ({v})" for f, v in feats) or "column present, no P/S"))
            if js:
                print("    journeys: " + ", ".join(js))
            if reqs_served:
                print("    requirements cited in Serves: " + ", ".join(reqs_served))
            if cov:
                print("    coverage rows: " + ", ".join(cov))
        if not any_ref:
            print("  not referenced by any tool doc")
    return rc


def esc(label, limit=48):
    s = re.sub(r"\s+", " ", label).strip().replace('"', "'")
    return s if len(s) <= limit else s[:limit - 1] + "…"


def flows_markdown(tool, type_names):
    by_ut = OrderedDict()
    for j in tool["journeys"]:
        if j["ut"]:
            by_ut.setdefault(j["ut"], []).append(j)
    if not by_ut:
        return "_No journeys yet._"
    out = []
    for ut in sorted(by_ut, key=num):
        nodes, edges = OrderedDict(), OrderedDict()

        def node(key, label, shape):
            if key not in nodes:
                nodes[key] = (f"n{len(nodes) + 1}", label, shape)
            return nodes[key][0]

        def edge(a, b, label=None):
            edges.setdefault((a, b), [])
            if label and label not in edges[(a, b)]:
                edges[(a, b)].append(label)

        for j in by_ut[ut]:
            i_n = node(("i", norm(j["intent"])), j["intent"] or "(intent?)", "intent")
            outcome = j["outcome"] or "?"
            o_n = node(("o", outcome.lower()), outcome, "ok" if outcome.lower() == "success" else "bad")
            f_ns = [node(("f", f), f"{f} {tool['features'].get(f, {}).get('name', '?')}", "feature") for f in j["path_ids"]]
            entries = [e.strip() for e in j["entry"].split(";") if e.strip()] or ["(entry?)"]
            tag = j["id"] + (f" · {j['context']}" if j["context"] else "")
            for e in entries:
                e_n = node(("e", norm(e)), e, "entry")
                edge(i_n, e_n)
                edge(e_n, f_ns[0] if f_ns else o_n, None if f_ns else tag)
            for a, b in zip(f_ns, f_ns[1:]):
                edge(a, b)
            if f_ns:
                edge(f_ns[-1], o_n, tag)
        out += [f"#### {ut} · {type_names.get(ut, '(unknown user-type)')}", "", "```mermaid", "flowchart LR"]
        shapes = {"intent": '(["{}"])', "entry": '[/"{}"/]', "feature": '["{}"]', "ok": '{{{{"{}"}}}}',
                  "bad": '{{{{"{}"}}}}'}
        for (nid, label, shape) in nodes.values():
            out.append(f"    {nid}{shapes[shape].format(esc(label))}")
        for (a, b), labels in edges.items():
            out.append(f'    {a} -->|"{esc(", ".join(labels), 60)}"| {b}' if labels else f"    {a} --> {b}")
        out.append("    classDef intent fill:#eef2ff,stroke:#4f46e5")
        out.append("    classDef ok fill:#e8f5e9,stroke:#2e7d32")
        out.append("    classDef bad fill:#fdecea,stroke:#c62828")
        for kind in ("intent", "ok", "bad"):
            ids = [nid for (nid, _, shape) in nodes.values() if shape == kind]
            if ids:
                out.append(f"    class {','.join(ids)} {kind}")
        out += ["```", ""]
    return "\n".join(out).rstrip()


def cmd_sync(root, args):
    t = load_types(root)
    tools = load_tools(root)
    type_names = {x["id"]: x["name"] for x in (t["types"] if t else [])}
    changed = []

    # ---- tool docs: flows block + ID tracker
    for tool in tools:
        text = tool["text"]
        flows = flows_markdown(tool, type_names)
        text, ok = set_block(text, "flows", flows)
        if not ok:
            lines = text.splitlines()
            block = ["<!-- ux:flows:start -->", flows, "<!-- ux:flows:end -->", ""]
            at = next((i for i, l in enumerate(lines) if l.strip().lower() == "### journey flows"), None)
            if at is not None:
                lines[at + 1:at + 1] = [""] + block
            else:
                at = next((i for i, l in enumerate(lines) if l.strip().lower() == "### journey details"), None)
                if at is not None:
                    lines[at:at] = ["### Journey flows", ""] + block
                else:
                    lines += ["", "### Journey flows", ""] + block
            text = "\n".join(lines) + "\n"
        lf = max([tool["last_f"]] + [num(f) for f in tool["features"]])
        lj = max([tool["last_j"]] + [num(j["id"]) for j in tool["journeys"]])
        marker = f"<!-- ux:last-ids: F={lf} J={lj} -->"
        if LAST_IDS_RE.search(text):
            text = LAST_IDS_RE.sub(marker, text, count=1)
        else:
            lines = text.splitlines()
            at = next((i for i, l in enumerate(lines) if l.startswith("# ")), -1)
            lines.insert(at + 1, marker)
            text = "\n".join(lines) + "\n"
        if text != tool["text"]:
            tool["path"].write_text(text, encoding="utf-8")
            changed.append(str(tool["path"].relative_to(root)))

    # ---- User_Types.md: index, mapped blocks, ID tracker
    if t is None:
        print(f"{UX_DIR}/{TYPES_NAME} missing; only tool docs were synced.")
    else:
        usage = OrderedDict((x["id"], []) for x in t["types"])
        for tool in tools:
            for u, feats in mapped_types(tool).items():
                njs = sum(1 for j in tool["journeys"] if j["ut"] == u)
                usage.setdefault(u, []).append((tool, feats, njs))
        text = t["text"]
        for ty in t["types"]:
            uses = usage.get(ty["id"], [])
            if uses:
                body = "\n".join(
                    f"- **{tool['title']}** (`{UX_DIR}/{TOOLS_DIR}/{tool['slug']}.md`): " +
                    ", ".join(f"{f} {tool['features'].get(f, {}).get('name', '?')} ({v})" for f, v in feats) +
                    f" · {njs} journeys" for tool, feats, njs in uses)
            else:
                body = "_Not mapped to any tool yet._"
            text, ok = set_block(text, f"mapped:{ty['id']}", body)
        # insert missing mapped blocks (reverse order keeps line numbers valid)
        lines = text.splitlines()
        cur = load_types_from_text(text)
        for ty in reversed(cur):
            if f"<!-- ux:mapped:{ty['id']}:start -->" in text:
                continue
            uses = usage.get(ty["id"], [])
            body = "\n".join(
                f"- **{tool['title']}** (`{UX_DIR}/{TOOLS_DIR}/{tool['slug']}.md`): " +
                ", ".join(f"{f} {tool['features'].get(f, {}).get('name', '?')} ({v})" for f, v in feats) +
                f" · {njs} journeys" for tool, feats, njs in uses) or "_Not mapped to any tool yet._"
            end = ty["end"]
            while end > ty["start"] and not lines[end - 1].strip():
                end -= 1
            lines[end:end] = ["", "### Mapped features", "", f"<!-- ux:mapped:{ty['id']}:start -->", body,
                              f"<!-- ux:mapped:{ty['id']}:end -->", ""]
        text = "\n".join(lines) + "\n"
        rows = ["| ID | Name | Access | Must | Used in tools |", "|---|---|---|---|---|"]
        for ty in t["types"]:
            musts = sum(1 for r in ty["reqs"] if UT_REQ_FULL_RE.match(r["id"]) and UT_REQ_FULL_RE.match(r["id"]).group(2) == "M")
            used = ", ".join(tool["slug"] for tool, _, _ in usage.get(ty["id"], [])) or "-"
            rows.append(f"| {ty['id']} | {ty['name']} | {ty['fields'].get('access level', '?')} | {musts} | {used} |")
        index = "\n".join(rows) if t["types"] else "_No user-types yet._"
        text, ok = set_block(text, "index", index)
        if not ok:
            lines = text.splitlines()
            at = next((i for i, l in enumerate(lines) if LAST_UT_RE.search(l)), None)
            if at is None:
                at = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
            lines[at + 1:at + 1] = ["", "## Index", "", "<!-- ux:index:start -->", index, "<!-- ux:index:end -->"]
            text = "\n".join(lines) + "\n"
        last = max([t["last_ut"]] + [num(x["id"]) for x in t["types"]])
        if LAST_UT_RE.search(text):
            text = LAST_UT_RE.sub(f"<!-- ux:last-ut: {last} -->", text, count=1)
        else:
            lines = text.splitlines()
            at = next((i for i, l in enumerate(lines) if l.startswith("# ")), -1)
            lines.insert(at + 1, f"<!-- ux:last-ut: {last} -->")
            text = "\n".join(lines) + "\n"
        if text != t["text"]:
            t["path"].write_text(text, encoding="utf-8")
            changed.append(f"{UX_DIR}/{TYPES_NAME}")
    print("Synced: " + (", ".join(changed) if changed else "nothing changed"))
    return 0


def load_types_from_text(text):
    lines = text.splitlines()
    res = []
    for _, s, e in h2_sections(lines):
        m = UT_HEAD_RE.match(lines[s])
        if m:
            res.append({"id": m.group(1), "start": s, "end": e})
    return res


def cmd_check(root, args):
    errors, warnings = [], []
    E = lambda where, msg: errors.append(f"{where}: {msg}")
    W = lambda where, msg: warnings.append(f"{where}: {msg}")
    t = load_types(root)
    tf = f"{UX_DIR}/{TYPES_NAME}"
    alt = find_alternative_types_file(root)
    if alt:
        W(str(alt.relative_to(root)), f"non-standard user-types file name; the skills use {tf}")
    types, reqs = {}, {}
    if t is None:
        E(tf, "missing (run the user-types skill)")
    else:
        for ty in t["types"]:
            where = f"{tf}:{ty['line']}"
            if ty["id"] in types:
                E(where, f"duplicate user-type ID {ty['id']}")
            types[ty["id"]] = ty
            if not ty["fields"].get("description"):
                E(where, f"{ty['id']} has no **Description:**")
            if "goals" not in ty["fields"]:
                W(where, f"{ty['id']} has no **Goals:**")
            acc = ty["fields"].get("access level", "")
            if acc not in ACCESS_LEVELS:
                E(where, f"{ty['id']} access level '{acc}' is not one of {', '.join(ACCESS_LEVELS)}")
            if not ty["fields"].get("based on"):
                W(where, f"{ty['id']} has no **Based on:**")
            counts = Counter()
            for r in ty["reqs"]:
                m = UT_REQ_FULL_RE.match(r["id"])
                rw = f"{tf}:{r['line']}"
                if m.group(1) != ty["id"]:
                    E(rw, f"requirement {r['id']} sits under {ty['id']}")
                if r["priority"] != PRIORITY[m.group(2)]:
                    E(rw, f"requirement {r['id']} has priority '{r['priority']}', expected '{PRIORITY[m.group(2)]}'")
                if r["id"] in reqs:
                    E(rw, f"duplicate requirement ID {r['id']}")
                if not r["text"]:
                    E(rw, f"requirement {r['id']} has no text")
                reqs[r["id"]] = r
                counts[m.group(2)] += 1
            if counts["M"] == 0:
                E(where, f"{ty['id']} has no Must requirement")
            if f"<!-- ux:mapped:{ty['id']}:start -->" not in t["text"]:
                W(where, f"{ty['id']} has no generated 'Mapped features' block (run sync)")
        for b in t["baseline"]:
            reqs[b["id"]] = b
        if "<!-- ux:index:start -->" not in t["text"]:
            W(tf, "no generated index block (run sync)")
        if t["last_ut"] < max([0] + [num(x) for x in types]):
            W(tf, "ID tracker is behind the highest user-type ID (run sync)")

    for tool in load_tools(root, args.slug):
        tp = f"{UX_DIR}/{TOOLS_DIR}/{tool['slug']}.md"
        for key, label in [("summary", "Summary"), ("features", "Features"), ("map", "Feature map"),
                           ("coverage", "Coverage"), ("journeys", "Journeys")]:
            if not tool["sections"][key]:
                E(tp, f"missing section '## {label}'")
        feats = tool["features"]
        if not feats:
            E(tp, "no features")
        for f in feats.values():
            fw = f"{tp}:{f['line']}"
            if f["dupe"]:
                E(fw, f"duplicate feature ID {f['id']}")
            if not f["name"]:
                E(fw, f"{f['id']} has no name")
            for r in f["serves"]:
                if t is not None and r not in reqs:
                    E(fw, f"{f['id']} serves unknown requirement {r}")
        for u in tool["map_cols"]:
            if t is not None and u not in types:
                E(tp, f"feature map column {u} is not a user-type in {tf}")
        for fid, m in tool["map"].items():
            mw = f"{tp}:{m['line']}"
            if fid not in feats:
                E(mw, f"feature map row {fid} is not in the Features table")
            bad = [f"{u}='{v}'" for u, v in m["cells"].items() if v not in MAP_VALUES]
            if bad:
                E(mw, f"{fid} has invalid map values {', '.join(bad)} (use P, S or blank)")
            if not any(v in ("P", "S") for v in m["cells"].values()):
                E(mw, f"{fid} is not mapped to any user-type")
        for fid in feats:
            if fid not in tool["map"]:
                E(tp, f"feature {fid} is missing from the feature map")
        used = mapped_types(tool)

        # coverage
        served = {r for f in feats.values() for r in f["serves"]}
        decided = {}
        for c in tool["coverage"]:
            cw = f"{tp}:{c['line']}"
            if c["decision"] not in DECISIONS:
                E(cw, f"coverage decision '{c['decision']}' for {c['req']} is not one of {', '.join(DECISIONS)}")
            if t is not None and c["req"] not in reqs:
                E(cw, f"coverage row for unknown requirement {c['req']}")
            decided[c["req"]] = c["decision"]
        gaps = []
        for u in used:
            ty = types.get(u)
            if not ty:
                continue
            for r in ty["reqs"]:
                if not r["id"].split("-")[2].startswith("M") or r["id"] in served:
                    continue
                d = decided.get(r["id"])
                if d in ("Served elsewhere", "Out of scope"):
                    continue
                gaps.append((r, d))
        for r, d in gaps:
            W(tp, f"coverage gap {'(Open) ' if d == 'Open' else ''}{r['id']} '{r['text']}' is served by no feature")

        # journeys
        js = tool["journeys"]
        if not js:
            W(tp, "no journeys yet")
        else:
            ids, keys = set(), {}
            main_ids = {j["id"] for j in js if not j["variant_id"]}
            for j in js:
                jw = f"{tp}:{j['line']}"
                if j["id"] in ids:
                    E(jw, f"duplicate journey ID {j['id']}")
                ids.add(j["id"])
                if not j["ut"]:
                    E(jw, f"{j['id']} has no user-type ID")
                elif t is not None and j["ut"] not in types:
                    E(jw, f"{j['id']} uses unknown user-type {j['ut']}")
                elif j["ut"] not in used:
                    W(jw, f"{j['id']} is for {j['ut']}, who is not mapped to any feature of this tool")
                for f in j["path_ids"]:
                    if f not in feats:
                        E(jw, f"{j['id']} path uses unknown feature {f}")
                    elif j["ut"] and tool["map"].get(f, {}).get("cells", {}).get(j["ut"]) not in ("P", "S"):
                        W(jw, f"{j['id']}: {j['ut']} uses {f} but is not mapped to it (P/S)")
                if j["outcome"] not in OUTCOMES:
                    E(jw, f"{j['id']} outcome '{j['outcome']}' is not one of {', '.join(OUTCOMES)}")
                if not j["path_ids"] and j["outcome"] != "Blocked":
                    E(jw, f"{j['id']} has an empty path; only Blocked journeys may")
                for k in ("intent", "entry", "after"):
                    if not j[k]:
                        E(jw, f"{j['id']} has no {k}")
                if j["variant_id"]:
                    if j["variant_id"] not in main_ids:
                        E(jw, f"{j['id']} is a variant of {j['variant_id']}, which is not a main journey")
                elif j["outcome"] != "Success":
                    W(jw, f"{j['id']} is a main journey but its outcome is {j['outcome']} (main journeys are Success)")
                if not j["variant_id"] and j["id"] not in tool["details"]:
                    W(jw, f"main journey {j['id']} has no '#### {j['id']} ·' details section")
                key = (j["ut"], norm(j["intent"]), tuple(j["path_ids"]), j["outcome"].lower(), norm(j["context"]))
                if key in keys:
                    E(jw, f"{j['id']} duplicates {keys[key]} (same user-type, intent, path, outcome, context): merge them")
                else:
                    keys[key] = j["id"]
            for u in used:
                if not any(j["ut"] == u and not j["variant_id"] for j in js):
                    E(tp, f"mapped user-type {u} has no main journey")
            in_paths = {f for j in js for f in j["path_ids"]}
            for f in feats:
                if f not in in_paths:
                    W(tp, f"feature {f} {feats[f]['name']} appears in no journey")
            for u, fl in used.items():
                for f, v in fl:
                    if v == "P" and not any(j["ut"] == u and f in j["path_ids"] for j in js):
                        W(tp, f"{u} is primary (P) on {f} but none of its journeys use it")
            generated = flows_markdown(tool, {k: v["name"] for k, v in types.items()})
            m = re.search(r"<!-- ux:flows:start -->\n(.*?)\n<!-- ux:flows:end -->", tool["text"], re.S)
            if not m or m.group(1).strip() != generated.strip():
                W(tp, "journey flowcharts are out of date (run sync)")

    if t is not None:
        tools_all = load_tools(root)
        for ty in t["types"]:
            m = re.search(re.escape(f"<!-- ux:mapped:{ty['id']}:start -->") + r"\n(.*?)\n", t["text"], re.S)
            uses = [tool["slug"] for tool in tools_all if ty["id"] in mapped_types(tool)]
            if m and uses and any(f"/{s}.md" not in m.group(1) for s in uses):
                W(tf, f"{ty['id']} mapped-features block is out of date (run sync)")
                break

    for e in errors:
        print("ERROR   " + e)
    for w in warnings:
        print("WARNING " + w)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("scan")
    p = sub.add_parser("init")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("init-tool")
    p.add_argument("slug")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("refs")
    p.add_argument("ids", nargs="+")
    sub.add_parser("sync")
    p = sub.add_parser("check")
    p.add_argument("slug", nargs="?")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    return {"status": cmd_status, "scan": cmd_scan, "init": cmd_init, "init-tool": cmd_init_tool,
            "refs": cmd_refs, "sync": cmd_sync, "check": cmd_check}[args.cmd](root, args)


if __name__ == "__main__":
    sys.exit(main())
