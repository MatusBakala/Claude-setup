"""Testy pre scripts/memory-map.py (spustenie: python3 -m unittest discover plugins/core/tests)."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "memory-map.py"
spec = importlib.util.spec_from_file_location("memory_map", SCRIPT)
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def instinct(id_, trigger, action, scope="global", source="approved", confidence="0.7", extra=""):
    return (
        f"---\nid: {id_}\ntrigger: {trigger}\nconfidence: {confidence}\ndomain: workflow\n"
        f"source: {source}\nscope: {scope}\n{extra}---\n\n# {id_}\n\n## Action\n{action}\n"
    )


class MemoryMapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        t = self.tmp
        self.plugin = t / "plugin"
        write(self.plugin / "context" / "preferencie.md", "# Preferencie\n\n- stručne\n")
        write(self.plugin / "instincts" / "verify-facts.md",
              instinct("verify-facts", "when answering facts", "Check the docs."))
        write(self.plugin / "agents" / "hladac.md",
              "---\nname: hladac\ndescription: Fast search.\nmodel: haiku\n---\n\nBody\n")
        write(self.plugin / "skills" / "tdd" / "SKILL.md",
              "---\nname: tdd\ndescription: Test-first.\n---\n\n# TDD\n")

        self.web = t / "code" / "web"
        write(self.web / "CLAUDE.md", "# Web\n\nPouži npm.\n")
        write(self.web / ".claude" / "instincts" / "locales.md",
              instinct("apply-locales", "when copy changes", "Edit all locales.", scope="project"))

        self.homunculus = t / "homunculus"
        write(self.homunculus / "projects.json", json.dumps({
            "abc123": {"id": "abc123", "name": "web", "root": str(self.web)},
            "gone99": {"id": "gone99", "name": "gone", "root": str(t / "missing")},
        }))
        write(self.homunculus / "projects" / "abc123" / "instincts" / "personal" / "sync-main.md",
              instinct("sync-main", "after merge", "Pull main.", scope="project",
                       source="session-observation", confidence="0.5",
                       extra="project_id: abc123\nproject_name: web\n"))

        self.claude_home = t / "claude"
        enc = mm.encode_project_path(str(self.web))
        write(self.claude_home / "projects" / enc / "memory" / "MEMORY.md", "- [Deploy](deploy.md)\n")
        write(self.claude_home / "projects" / enc / "memory" / "deploy.md",
              "---\nname: deploy\ndescription: Deploys go via CI.\nmetadata:\n  type: project\n---\n\nUse CI.\n")
        self.claude_json = t / "claude.json"
        write(self.claude_json, json.dumps({"projects": {str(self.web): {}}}))

        self.vault = t / "vault"
        self.vault.mkdir()

    def sources(self):
        return mm.Sources(
            plugin_root=self.plugin,
            homunculus=self.homunculus,
            claude_home=self.claude_home,
            claude_json=self.claude_json,
            scan_dirs=[self.tmp / "code"],
        )

    def run_map(self):
        return mm.build_map(self.sources(), self.vault, "Claude")

    def read(self, rel):
        return (self.vault / "Claude" / rel).read_text(encoding="utf-8")

    def test_writes_index_and_notes_for_every_source(self):
        self.run_map()
        index = self.read("Mapa.md")
        for link in ("[[Claude/Preferencie|", "[[Claude/Instinkty/verify-facts|", "[[Claude/Projekty/web|",
                     "[[Claude/Agenti/hladac|", "[[Claude/Skilly/tdd|", "[[Claude/Pamat/web - deploy|"):
            self.assertIn(link, index)
        self.assertIn("stručne", self.read("Preferencie.md"))
        self.assertTrue((self.vault / "Claude" / "Prehlad.base").exists())

    def test_instinct_note_has_properties_and_project_link(self):
        self.run_map()
        note = self.read("Instinkty/sync-main.md")
        self.assertIn("typ: instinkt", note)
        self.assertIn("stav: automaticky", note)
        self.assertIn("confidence: 0.5", note)
        self.assertIn('projekt: "[[Claude/Projekty/web]]"', note)
        self.assertIn("Pull main.", note)
        approved = self.read("Instinkty/verify-facts.md")
        self.assertIn("stav: schvaleny", approved)
        self.assertIn("rozsah: globalny", approved)

    def test_project_note_embeds_claude_md_and_lists_its_memory(self):
        self.run_map()
        note = self.read("Projekty/web.md")
        self.assertIn("Použi npm.", note)
        self.assertIn("[[Claude/Instinkty/apply-locales|", note)
        self.assertIn("[[Claude/Instinkty/sync-main|", note)
        self.assertIn("[[Claude/Pamat/web - deploy|", note)

    def test_missing_project_roots_are_skipped(self):
        self.run_map()
        self.assertFalse((self.vault / "Claude" / "Projekty" / "gone.md").exists())

    def test_discovers_project_with_only_approved_instincts(self):
        repo = self.tmp / "code" / "hermes"
        write(repo / ".claude" / "instincts" / "check-hooks.md",
              instinct("check-hooks", "after hook changes", "Check both profiles.", scope="project"))
        self.run_map()
        self.assertIn('projekt: "[[Claude/Projekty/hermes]]"', self.read("Instinkty/check-hooks.md"))
        self.assertIn("[[Claude/Instinkty/check-hooks|", self.read("Projekty/hermes.md"))

    def test_identical_project_instincts_share_a_note_but_different_versions_do_not(self):
        same = self.web / ".claude" / "instincts" / "locales.md"
        original = same.read_text(encoding="utf-8")
        copies = self.tmp / "code"
        write(copies / "web-copy" / "CLAUDE.md", "# Web copy\n")
        write(copies / "web-variant" / "CLAUDE.md", "# Web variant\n")
        write(copies / "web-copy" / ".claude" / "instincts" / "locales.md", original)
        write(copies / "web-variant" / ".claude" / "instincts" / "locales.md",
              original.replace("Edit all locales.", "Edit public locales."))
        self.run_map()
        paths = sorted((self.vault / "Claude" / "Instinkty").glob("apply-locales*.md"))
        self.assertEqual(len(paths), 2)
        shared = "[[Claude/Instinkty/apply-locales|"
        for owner in ("web", "web-copy"):
            self.assertIn(shared, self.read(f"Projekty/{owner}.md"))
        self.assertNotIn(shared, self.read("Projekty/web-variant.md"))
        self.assertIn("[[Claude/Projekty/web-copy]]", self.read("Instinkty/apply-locales.md"))
        self.assertIn("property: note.projekt", self.read("Prehlad.base"))

    def test_second_run_changes_nothing(self):
        self.run_map()
        stats = self.run_map()
        self.assertEqual(stats["written"], 0)
        self.assertEqual(stats["removed"], 0)

    def test_removed_source_removes_its_note_but_keeps_user_files(self):
        self.run_map()
        write(self.vault / "Claude" / "moja-poznamka.md", "moje")
        (self.plugin / "instincts" / "verify-facts.md").unlink()
        stats = self.run_map()
        self.assertEqual(stats["removed"], 1)
        self.assertFalse((self.vault / "Claude" / "Instinkty" / "verify-facts.md").exists())
        self.assertEqual(self.read("moja-poznamka.md"), "moje")

    def test_does_not_overwrite_user_file_it_did_not_create(self):
        write(self.vault / "Claude" / "Preferencie.md", "moje vlastne")
        self.run_map()
        self.assertEqual(self.read("Preferencie.md"), "moje vlastne")

    def test_worktree_and_duplicate_names_get_distinct_notes(self):
        other = self.tmp / "other" / "web"
        write(other / "CLAUDE.md", "# Iny web\n")
        worktree = self.web / ".claude" / "worktrees" / "x"
        write(worktree / "CLAUDE.md", "# worktree\n")
        write(self.claude_json, json.dumps({"projects": {str(self.web): {}, str(other): {}, str(worktree): {}}}))
        self.run_map()
        names = sorted(p.name for p in (self.vault / "Claude" / "Projekty").iterdir())
        self.assertEqual(names, ["web (code).md", "web (other).md"])

    def test_non_utf8_user_file_is_not_overwritten(self):
        target = self.vault / "Claude" / "Mapa.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"\xff\xfe moje")
        stats = self.run_map()
        self.assertEqual(target.read_bytes(), b"\xff\xfe moje")
        self.assertGreaterEqual(stats["skipped"], 1)

    def test_manifest_entries_outside_folder_are_never_deleted(self):
        outside = self.vault / "outside.md"
        write(outside, "moje")
        write(self.vault / "Claude" / ".memory-map.json",
              json.dumps({"files": ["../outside.md", str(outside)]}))
        self.run_map()
        self.assertTrue(outside.exists())

    def test_interrupted_run_still_owns_its_files(self):
        out = self.vault / "Claude"
        notes = mm.build_notes(mm.collect(self.sources()), "Claude")
        out.mkdir()
        # simulácia prerušenia: súbory zapísané, finálny manifest nie
        write(out / ".memory-map.json", json.dumps({"files": sorted(notes)}))
        write(out / "Mapa.md", "stara verzia")
        self.run_map()
        self.assertIn("Mapa pamäte Clauda", self.read("Mapa.md"))

    def test_case_only_and_triple_collisions_get_distinct_notes(self):
        for i, id_ in enumerate(("dup", "Dup", "dup")):
            write(self.plugin / "instincts" / f"dup{i}.md", instinct(id_, f"t{i}", f"Action {i}."))
        self.run_map()
        names = [p.name.lower() for p in (self.vault / "Claude" / "Instinkty").iterdir()
                 if p.name.lower().startswith("dup")]
        self.assertEqual(len(names), 3)
        self.assertEqual(len(set(names)), 3)

    def test_claude_md_with_long_fence_stays_embedded(self):
        write(self.web / "CLAUDE.md", "# Web\n\n````\nkod\n````\nkoniec\n")
        self.run_map()
        note = self.read("Projekty/web.md")
        self.assertIn("`````markdown", note)

    def test_hook_mode_never_fails_when_build_raises(self):
        env = dict(os.environ, CLAUDE_MEMORY_MAP_VAULT=str(self.vault), HOME=str(self.tmp / "emptyhome"))
        write(self.vault / "Claude", "toto je subor, nie priecinok")
        out = subprocess.run([sys.executable, str(SCRIPT), "--hook", "--neznamy"], input="{}",
                             capture_output=True, text=True, env=env, timeout=20)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout + out.stderr, "")

    def test_hook_mode_without_vault_is_a_silent_noop(self):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_MEMORY_MAP_VAULT"}
        env["HOME"] = str(self.tmp / "emptyhome")
        out = subprocess.run([sys.executable, str(SCRIPT), "--hook"], input="{}",
                             capture_output=True, text=True, env=env, timeout=20)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout, "")


    def sources_with_hermes(self):
        sources = self.sources()
        sources.hermes_notes = self.vault / "Hermes"
        return sources

    def run_map_with_hermes(self):
        return mm.build_map(self.sources_with_hermes(), self.vault, "Claude")

    def test_map_lists_hermes_notes_newest_first_and_skips_readme(self):
        hermes = self.vault / "Hermes"
        write(hermes / "README.md", "# Hermes notes\n\nPravidla.\n")
        write(hermes / "2026-11-20-macbook-seo.md",
              "---\ndatum: 2026-11-20\nprojekt: osobny web\n---\n\n# SEO audit\n\nPrepisane texty.\n")
        write(hermes / "2026-11-21-imac-worker.md", "# Worker deploy\n\nNasadene na Cloudflare.\n")
        self.run_map_with_hermes()
        index = self.read("Mapa.md")
        self.assertIn("## Z Hermesa (2)", index)
        self.assertNotIn("README", index)
        self.assertLess(index.index("Worker deploy"), index.index("SEO audit"))
        self.assertIn("[[Hermes/2026-11-21-imac-worker|Worker deploy]]", index)
        self.assertIn("_(2026-11-20, osobny web)_ Prepisane texty.", index)

    def test_map_has_no_hermes_section_when_the_folder_is_missing(self):
        self.run_map_with_hermes()
        self.assertNotIn("Z Hermesa", self.read("Mapa.md"))

    def test_map_never_writes_into_the_hermes_folder(self):
        hermes = self.vault / "Hermes"
        write(hermes / "2026-11-21-imac-worker.md", "# Worker deploy\n\nHotovo.\n")
        before = sorted((p.name, p.read_bytes()) for p in hermes.iterdir())
        self.run_map_with_hermes()
        self.run_map_with_hermes()
        self.assertEqual(sorted((p.name, p.read_bytes()) for p in hermes.iterdir()), before)

    def test_map_shows_only_the_newest_hermes_notes(self):
        hermes = self.vault / "Hermes"
        total = mm.HERMES_NOTES_SHOWN + 2
        for index in range(total):
            write(hermes / f"2026-11-{index + 1:02d}-imac-poznamka.md", f"# Poznamka {index}\n\nText.\n")
        self.run_map_with_hermes()
        index_text = self.read("Mapa.md")
        self.assertIn(f"## Z Hermesa ({total})", index_text)
        self.assertIn("a ďalších 2 starších", index_text)


if __name__ == "__main__":
    unittest.main()
