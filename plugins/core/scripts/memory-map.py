#!/usr/bin/env python3
"""Mapa pamäte Clauda do Obsidian vaultu.

Prečíta všetko, čo si Claude pamätá, a zapíše to ako prepojené poznámky do priečinka vo vaulte:
  - preferencie a schválené globálne inštinkty pluginu core, jeho agenti a skilly
  - projekty: CLAUDE.md, schválené projektové inštinkty (<projekt>/.claude/instincts)
  - automaticky naučené inštinkty observera (ecc-homunculus)
  - auto-memory Claude Code (~/.claude/projects/*/memory)

Mapa je len na čítanie – zdroj pravdy ostávajú pôvodné súbory, ďalší beh ju prepíše.
Skript mení iba súbory, ktoré sám vytvoril (zoznam v <priečinok>/.memory-map.json);
poznámky, ktoré si do priečinka pridáš ručne, nechá tak.

Použitie:
  memory-map.py --vault ~/MojVault [--folder Claude] [--scan-dir ~/Developer]
  memory-map.py --hook   # SessionEnd hook: vault z CLAUDE_MEMORY_MAP_VAULT alebo
                         # ~/.claude/memory-map.json {"vault": ..., "folder": ..., "scan_dirs": [...]};
                         # bez nastaveného vaultu nerobí nič a nikdy nezlyhá.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST = ".memory-map.json"
YAML_RESERVED = {"true", "false", "yes", "no", "on", "off", "null", "y", "n", "~"}
SKIP_DIRS = {"node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
SCAN_DEPTH = 3


@dataclass
class Sources:
    plugin_root: Path
    homunculus: Path
    claude_home: Path
    claude_json: Path
    scan_dirs: list = field(default_factory=list)


@dataclass
class Project:
    root: Path
    name: str = ""
    claude_md: Path = None
    instincts: list = field(default_factory=list)
    memories: list = field(default_factory=list)
    aliases: set = field(default_factory=set)


# --- čítanie zdrojov -------------------------------------------------------------------------

def encode_project_path(path):
    """Názov priečinka, pod ktorým Claude Code ukladá projekt v ~/.claude/projects."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return None


def split_frontmatter(text):
    """Vráti (meta, telo). Podporuje `kľúč: hodnota` a viacriadkové `>`/`|` hodnoty."""
    lines = (text or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text or ""
    meta, key, i = {}, None, 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if line[:1] in (" ", "\t") and key:
            meta[key] = (meta[key] + " " + line.strip()).strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            meta[key] = "" if value in (">", "|", ">-", "|-") else value.strip('"').strip("'")
        i += 1
    return meta, "\n".join(lines[i + 1:]).lstrip("\n")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def is_ignored_root(path, home):
    s = str(path)
    return "/.claude/worktrees/" in s or "scratch-workspaces" in s or path == home


def scan_claude_md(base, depth=SCAN_DEPTH):
    roots = []
    base = Path(base).expanduser()
    if not base.is_dir():
        return roots
    for dirpath, dirnames, filenames in os.walk(base):
        rel_depth = len(Path(dirpath).relative_to(base).parts)
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        if rel_depth >= depth:
            dirnames[:] = []
        if "CLAUDE.md" in filenames:
            roots.append(Path(dirpath))
    return roots


def instinct_files(directory):
    d = Path(directory)
    if not d.is_dir():
        return []
    return sorted(p for p in d.rglob("*") if p.suffix in (".md", ".yaml", ".yml") and p.is_file())


def parse_instinct(path, stav, rozsah):
    meta, body = split_frontmatter(read_text(path))
    if not meta:
        return None
    return {
        "id": meta.get("id") or path.stem,
        "trigger": meta.get("trigger", ""),
        "confidence": meta.get("confidence", ""),
        "domain": meta.get("domain", ""),
        "stav": stav,
        "rozsah": rozsah,
        "body": body.strip(),
        "path": path,
        "project": None,
        "project_label": meta.get("project_name", ""),
    }


def collect(sources):
    home = Path.home()
    projects = {}

    def project(root):
        root = Path(root)
        key = str(root.resolve()) if root.exists() else str(root)
        if key not in projects:
            projects[key] = Project(root=Path(key))
        projects[key].aliases.update({str(root), key})
        return projects[key]

    candidate_roots = list(load_json(sources.claude_json).get("projects", {}).keys())
    homunculus_projects = load_json(sources.homunculus / "projects.json")
    candidate_roots += [p.get("root", "") for p in homunculus_projects.values()]
    for base in sources.scan_dirs:
        candidate_roots += [str(r) for r in scan_claude_md(base)]

    for raw in candidate_roots:
        root = Path(raw) if raw else None
        if not root or not root.is_dir() or is_ignored_root(root, home):
            continue
        p = project(root)
        for md in (p.root / "CLAUDE.md", p.root / ".claude" / "CLAUDE.md"):
            if md.is_file():
                p.claude_md = md
                break
        if not p.instincts:
            for f in instinct_files(p.root / ".claude" / "instincts"):
                inst = parse_instinct(f, "schvaleny", "projektovy")
                if inst:
                    inst["project"] = p
                    p.instincts.append(inst)

    instincts = []
    for f in instinct_files(sources.plugin_root / "instincts"):
        inst = parse_instinct(f, "schvaleny", "globalny")
        if inst:
            instincts.append(inst)
    for sub in ("personal", "inherited"):
        for f in instinct_files(sources.homunculus / "instincts" / sub):
            inst = parse_instinct(f, "automaticky", "globalny")
            if inst:
                instincts.append(inst)
    for pid, info in sorted(homunculus_projects.items()):
        root = Path(info.get("root", "") or "/nonexistent")
        owner = None
        if root.is_dir() and not is_ignored_root(root, home):
            owner = project(root)
        for f in instinct_files(sources.homunculus / "projects" / pid / "instincts"):
            inst = parse_instinct(f, "automaticky", "projektovy")
            if not inst:
                continue
            inst["project_label"] = inst["project_label"] or info.get("name", pid)
            if owner:
                inst["project"] = owner
                owner.instincts.append(inst)
            else:
                instincts.append(inst)
    for p in projects.values():
        instincts.extend(p.instincts)

    by_encoding = {encode_project_path(a): p for p in projects.values() for a in p.aliases}
    memories = []
    mem_base = sources.claude_home / "projects"
    if mem_base.is_dir():
        for d in sorted(mem_base.iterdir()):
            for f in sorted((d / "memory").glob("*.md")) if (d / "memory").is_dir() else []:
                if f.name == "MEMORY.md":
                    continue
                meta, body = split_frontmatter(read_text(f))
                owner = by_encoding.get(d.name)
                if owner is None:
                    owner = project(Path(d.name))  # projekt mimo disku: meno z priečinka
                mem = {"name": meta.get("name") or f.stem, "description": meta.get("description", ""),
                       "type": meta.get("type", ""), "body": body.strip(), "path": f, "project": owner}
                owner.memories.append(mem)
                memories.append(mem)

    kept = [p for p in projects.values() if p.claude_md or p.instincts or p.memories]
    name_projects(kept)

    def plugin_items(kind):
        items = []
        files = (sorted((sources.plugin_root / "agents").glob("*.md")) if kind == "agent"
                 else sorted((sources.plugin_root / "skills").glob("*/SKILL.md")))
        for f in files:
            meta, _ = split_frontmatter(read_text(f))
            items.append({"name": meta.get("name") or (f.stem if kind == "agent" else f.parent.name),
                          "description": meta.get("description", ""), "model": meta.get("model", ""),
                          "effort": meta.get("effort", ""), "path": f})
        return items

    return {
        "preferencie": sources.plugin_root / "context" / "preferencie.md",
        "global_claude_md": sources.claude_home / "CLAUDE.md",
        "instincts": instincts,
        "projects": sorted(kept, key=lambda p: p.name.lower()),
        "memories": memories,
        "agents": plugin_items("agent"),
        "skills": plugin_items("skill"),
    }


def name_projects(projects):
    """Meno projektu = názov priečinka; pri zhode pridá rodičovský priečinok."""
    def label(p, level):
        parts = p.root.parts
        name = parts[-1] if parts else str(p.root)
        if level and len(parts) > level:
            name = f"{name} ({parts[-1 - level]})"
        return safe_name(name)

    level_of = {id(p): 0 for p in projects}
    for _ in range(6):
        names = {}
        for p in projects:
            names.setdefault(label(p, level_of[id(p)]), []).append(p)
        clashes = [group for group in names.values() if len(group) > 1]
        if not clashes:
            break
        for group in clashes:
            for p in group:
                level_of[id(p)] += 1
    for p in projects:
        p.name = label(p, level_of[id(p)])


def safe_name(name):
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "-", str(name)).strip() or "bez-nazvu"


# --- zápis poznámok --------------------------------------------------------------------------

def yaml_value(value):
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return s
    if re.fullmatch(r"[A-Za-z0-9_.-]+", s) and s.lower() not in YAML_RESERVED:
        return s
    return json.dumps(s, ensure_ascii=False)


def note(props, body):
    lines = ["---"]
    for k, v in props.items():
        if v in (None, ""):
            continue
        lines.append(f"{k}: {yaml_value(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.rstrip() + "\n"


def one_line(text, limit=160):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_notes(data, folder):
    notes = {}
    f = folder.strip("/")

    def link(rel, label=None):
        target = f"{f}/{rel}" if f else rel
        return f"[[{target}|{label}]]" if label else f"[[{target}]]"

    back = f"↑ {link('Mapa', 'Mapa pamäte')}"
    generated = "> Vygenerované skriptom `memory-map.py` z pluginu core. Neupravuj – ďalší beh to prepíše."

    used = {"mapa", "preferencie", "globalny claude", "prehlad"}

    def unique(folder_name, *candidates):
        """Prvý voľný názov poznámky (bez ohľadu na veľkosť písmen – APFS ju nerozlišuje)."""
        names = [safe_name(c) for c in candidates if c]
        n = 2
        while True:
            for name in names:
                rel = f"{folder_name}/{name}"
                if rel.lower() not in used:
                    used.add(rel.lower())
                    return rel
            names = [f"{safe_name(candidates[0])} {n}"]
            n += 1

    for inst in data["instincts"]:
        inst["note"] = unique("Instinkty", inst["id"],
                              f"{inst['id']} ({inst['project_label'] or inst['stav']})")

    for mem in data["memories"]:
        mem["note"] = unique("Pamat", f"{mem['project'].name} - {mem['name']}")

    def instinct_line(inst):
        return f"- {link(inst['note'], inst['id'])} — {one_line(inst['trigger'])}"

    # inštinkty
    for inst in data["instincts"]:
        proj = inst["project"]
        props = {
            "typ": "instinkt", "rozsah": inst["rozsah"], "stav": inst["stav"],
            "confidence": inst["confidence"], "domena": inst["domain"],
            "projekt": link(f"Projekty/{proj.name}") if proj and proj.name else inst["project_label"],
            "zdroj": str(inst["path"]),
        }
        body = f"{back}\n\n**Kedy:** {inst['trigger']}\n\n{inst['body']}\n\n---\nZdroj: `{inst['path']}`"
        notes[inst["note"] + ".md"] = note(props, body)

    # projekty
    for p in data["projects"]:
        parts = [back, "", f"Priečinok: `{p.root}`"]
        if p.instincts:
            parts += ["", f"## Inštinkty ({len(p.instincts)})"]
            parts += [instinct_line(i) + f" _({i['stav']})_" for i in sorted(p.instincts, key=lambda i: i["id"])]
        if p.memories:
            parts += ["", f"## Auto-memory ({len(p.memories)})"]
            parts += [f"- {link(m['note'], m['name'])} — {one_line(m['description'])}" for m in p.memories]
        if p.claude_md:
            text = (read_text(p.claude_md) or "").rstrip()
            fence = "`" * max(4, max((len(r) for r in re.findall(r"`+", text)), default=0) + 1)
            parts += ["", "## CLAUDE.md", f"Zdroj: `{p.claude_md}`", "", fence + "markdown", text, fence]
        props = {"typ": "projekt", "priecinok": str(p.root), "instinkty": len(p.instincts),
                 "pamat": len(p.memories), "claude_md": "ano" if p.claude_md else "nie"}
        notes[f"Projekty/{p.name}.md"] = note(props, "\n".join(parts))

    # auto-memory
    for m in data["memories"]:
        props = {"typ": "pamat", "druh": m["type"], "projekt": link(f"Projekty/{m['project'].name}"),
                 "zdroj": str(m["path"])}
        body = f"{back}\n\n**{m['description']}**\n\n{m['body']}\n\n---\nZdroj: `{m['path']}`"
        notes[m["note"] + ".md"] = note(props, body)

    # agenti a skilly
    for kind, folder_name, typ in (("agents", "Agenti", "agent"), ("skills", "Skilly", "skill")):
        for item in data[kind]:
            item["note"] = unique(folder_name, item["name"])
            props = {"typ": typ, "model": item["model"], "effort": item["effort"], "zdroj": str(item["path"])}
            body = f"{back}\n\n{item['description']}\n\n---\nZdroj: `{item['path']}`"
            notes[item["note"] + ".md"] = note(props, body)

    # preferencie a globálny CLAUDE.md
    globals_ = []
    for path, title in ((data["preferencie"], "Preferencie"), (data["global_claude_md"], "Globalny CLAUDE")):
        text = read_text(path)
        if text is None:
            continue
        globals_.append(f"- {link(title, title)} — `{path}`")
        notes[f"{title}.md"] = note({"typ": "preferencie", "zdroj": str(path)},
                                    f"{back}\n\n{text.rstrip()}\n\n---\nZdroj: `{path}`")

    # prehľad (.base)
    inf = lambda sub: f'file.inFolder("{f}/{sub}")' if f else f'file.inFolder("{sub}")'
    notes["Prehlad.base"] = "\n".join([
        "views:",
        "  - type: table",
        "    name: Inštinkty",
        "    filters:",
        "      and:",
        f"        - '{inf('Instinkty')}'",
        "    order:", "      - file.name", "      - rozsah", "      - stav", "      - confidence",
        "      - domena", "      - projekt",
        "  - type: table",
        "    name: Projekty",
        "    filters:",
        "      and:",
        f"        - '{inf('Projekty')}'",
        "    order:", "      - file.name", "      - instinkty", "      - pamat", "      - claude_md",
        "      - priecinok",
        "",
    ])

    # mapa
    approved_global = [i for i in data["instincts"] if i["rozsah"] == "globalny" and i["stav"] == "schvaleny"]
    auto = [i for i in data["instincts"] if i["stav"] == "automaticky"]
    sections = ["# Mapa pamäte Clauda", "", generated, ""]
    sections += ["## Globálne nastavenia"] + (globals_ or ["- (nič)"])
    sections += ["", f"## Schválené globálne inštinkty ({len(approved_global)})"]
    sections += [instinct_line(i) for i in sorted(approved_global, key=lambda i: i["id"])] or ["- (žiadne)"]
    sections += ["", f"## Projekty ({len(data['projects'])})"]
    for p in data["projects"]:
        bits = [f"{len(p.instincts)} inštinktov"] + (["CLAUDE.md"] if p.claude_md else [])
        bits += [f"{len(p.memories)} v auto-memory"] if p.memories else []
        sections.append(f"- {link('Projekty/' + p.name, p.name)} — {', '.join(bits)}")
    if not data["projects"]:
        sections.append("- (žiadne)")
    sections += ["", f"## Automaticky naučené inštinkty ({len(auto)})",
                 "_Navrhol ich observer, zatiaľ neschválené – schváliš ich cez `/poucenia`._"]
    sections += [instinct_line(i) + (f" _({i['project_label']})_" if i["project_label"] else "")
                 for i in sorted(auto, key=lambda i: i["id"])] or ["- (žiadne)"]
    sections += ["", f"## Auto-memory ({len(data['memories'])})"]
    sections += [f"- {link(m['note'], m['project'].name + ' – ' + m['name'])} — {one_line(m['description'])}"
                 for m in data["memories"]] or ["- (prázdne)"]
    sections += ["", f"## Agenti ({len(data['agents'])})"]
    sections += [f"- {link(a['note'], a['name'])} — {a['model'] or '?'} · {one_line(a['description'], 120)}"
                 for a in data["agents"]] or ["- (žiadni)"]
    sections += ["", f"## Skilly ({len(data['skills'])})"]
    sections += [f"- {link(s['note'], s['name'])} — {one_line(s['description'], 120)}"
                 for s in data["skills"]] or ["- (žiadne)"]
    sections += ["", "## Tabuľka", f"![[{f + '/' if f else ''}Prehlad.base]]"]
    notes["Mapa.md"] = note({"typ": "mapa"}, "\n".join(sections))
    return notes


def inside(out_dir, rel):
    """Cesta rel vnútri out_dir, alebo None, ak by z neho utiekla (absolútna cesta, `..`)."""
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return None
    target = (out_dir / rel).resolve()
    return target if target.is_relative_to(out_dir.resolve()) else None


def save_manifest(path, files):
    text = json.dumps({"files": sorted(files)}, ensure_ascii=False, indent=1) + "\n"
    if read_text(path) != text:
        path.write_text(text, encoding="utf-8")


def write_notes(out_dir, notes):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / MANIFEST
    previous = {r for r in load_json(manifest_path).get("files", []) if isinstance(r, str)}
    stats = {"written": 0, "removed": 0, "skipped": 0}

    # 1. rozhodni, čo je moje: nový súbor, súbor z manifestu, alebo bajtovo zhodný súbor
    plan = {}
    for rel, content in sorted(notes.items()):
        target = inside(out_dir, rel)
        data = content.encode("utf-8")
        if target is None:
            continue
        if target.exists() or target.is_symlink():
            if not target.is_file() or target.is_symlink():
                stats["skipped"] += 1
                continue
            try:
                current = target.read_bytes()
            except Exception:
                stats["skipped"] += 1
                continue
            if rel not in previous and current != data:
                stats["skipped"] += 1  # súbor, ktorý som nevytvoril – nechám ho tak
                continue
            if current == data:
                plan[rel] = None
                continue
        plan[rel] = (target, data)

    # 2. manifest pred zápisom, aby prerušený beh nenechal moje súbory „cudzie“
    save_manifest(manifest_path, previous | set(plan))

    for rel, item in plan.items():
        if item is None:
            continue
        target, data = item
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp-memory-map")
        tmp.write_bytes(data)
        os.replace(tmp, target)
        stats["written"] += 1

    # 3. zmaž len moje staré súbory, ktoré už nemajú zdroj
    for rel in sorted(previous - set(notes)):
        target = inside(out_dir, rel)
        if target is not None and target.is_file() and not target.is_symlink():
            target.unlink()
            stats["removed"] += 1
            parent = target.parent
            if parent != out_dir.resolve() and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()

    save_manifest(manifest_path, set(plan))
    return stats


def build_map(sources, vault, folder="Claude"):
    notes = build_notes(collect(sources), folder)
    return write_notes(Path(vault) / folder, notes)


# --- spustenie -------------------------------------------------------------------------------

def homunculus_dir():
    for env, suffix in (("CLV2_HOMUNCULUS_DIR", ""), ("XDG_DATA_HOME", "ecc-homunculus")):
        value = os.environ.get(env, "")
        if value.startswith("/"):
            return Path(value) / suffix if suffix else Path(value)
    return Path.home() / ".local" / "share" / "ecc-homunculus"


def default_sources(scan_dirs):
    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    return Sources(plugin_root=plugin_root, homunculus=homunculus_dir(), claude_home=claude_home,
                   claude_json=Path.home() / ".claude.json",
                   scan_dirs=[Path(d).expanduser() for d in scan_dirs])


def load_config():
    config = load_json(Path.home() / ".claude" / "memory-map.json")
    if os.environ.get("CLAUDE_MEMORY_MAP_VAULT"):
        config["vault"] = os.environ["CLAUDE_MEMORY_MAP_VAULT"]
    return config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mapa pamäte Clauda do Obsidian vaultu.")
    parser.add_argument("--vault")
    parser.add_argument("--folder")
    parser.add_argument("--scan-dir", action="append", dest="scan_dirs")
    parser.add_argument("--hook", action="store_true", help="režim SessionEnd hooku: ticho, nikdy nezlyhá")
    args, _unknown = parser.parse_known_args(argv)

    try:
        config = load_config()
        vault = Path(args.vault or config.get("vault") or "").expanduser() if (args.vault or config.get("vault")) else None
        if vault is None or not vault.is_dir():
            if not args.hook:
                print("Chýba vault: zadaj --vault alebo nastav CLAUDE_MEMORY_MAP_VAULT / ~/.claude/memory-map.json",
                      file=sys.stderr)
                return 2
            return 0
        folder = str(args.folder or config.get("folder") or "Claude").strip("/")
        if not folder or Path(folder).is_absolute() or ".." in Path(folder).parts:
            raise ValueError(f"Priečinok mapy musí byť vnútri vaultu: {folder!r}")
        scan_dirs = args.scan_dirs or config.get("scan_dirs") or ["~/Developer"]
        stats = build_map(default_sources(scan_dirs), vault, folder)
        if not args.hook:
            print(f"Mapa: {vault / folder} – zapísané {stats['written']}, odstránené {stats['removed']}, "
                  f"preskočené (tvoje súbory) {stats['skipped']}")
        return 0
    except Exception as exc:
        if args.hook:
            return 0
        raise exc


if __name__ == "__main__":
    sys.exit(main())
