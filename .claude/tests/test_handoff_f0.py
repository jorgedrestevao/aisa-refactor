# -*- coding: utf-8 -*-
"""F0 do plano handoff-v1 (docs/handoff-v1/plan): T02 e integridade das fixtures.

T02 — a matriz `docs/handoff-v1/F0/consumer-matrix.json` lista, por autoridade (SU,
decisoes, blueprint, coverage, implementation-spec, estimate, _state.json), quem cria,
escreve, le, valida ou guarda. O varrimento usa o padrao declarado de cada autoridade e
falha quando um ficheiro que a referencia nao esta na matriz: um consumidor novo obriga a
actualizar o inventario antes de F1 o adaptar. Globs de mencao historica nao podem cobrir
caminhos de runtime.

Fixtures — `.claude/tests/fixtures/handoff-v1/` sao sinteticas; o registo
`docs/handoff-v1/F0/fixture-registry.json` nomeia-as e as ancoras citadas existem."""
import fnmatch
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
F0 = ROOT / "docs" / "handoff-v1" / "F0"
MATRIX_PATH = F0 / "consumer-matrix.json"
REGISTRY_PATH = F0 / "fixture-registry.json"
FIXTURES = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
VALIDACAO = ROOT / "docs" / "handoff-v1" / "plan" / "06_VALIDACAO.md"

REQUIRED = {"su", "decisions", "blueprint", "coverage", "implementation_spec", "estimate", "state"}
WRITER_ROLES = {"creator", "writer", "appender", "mirror"}
RUNTIME_PREFIXES = (".claude/skills/", ".claude/hooks/", ".claude/commands/", ".claude/agents/",
                    ".claude/rules/", ".claude/output-styles/", "library/", ".github/")
RUNTIME_FILES = ("CLAUDE.md", ".claude/settings.json")
ROUTES = {"solution-choice", "platform-constrained", "change-impact"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def is_glob(s):
    return any(c in s for c in "*?[")


def text_files(root, excludes):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        rel_dir = "" if rel_dir == "." else rel_dir + "/"
        dirnames[:] = sorted(d for d in dirnames if (rel_dir + d) not in excludes and d not in excludes)
        for name in sorted(filenames):
            rel = rel_dir + name
            try:
                text = (root / rel).read_bytes().decode("utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            yield rel, text


def covered(path, entry):
    if path in {c["file"] for c in entry["consumers"]}:
        return True
    for m in entry["mention_only"]:
        target = m["file"]
        if path == target or (is_glob(target) and fnmatch.fnmatchcase(path, target)):
            return True
    return False


def unlisted(matrix, root):
    files = list(text_files(root, set(matrix["scan"]["exclude"])))
    out = {}
    for key, entry in matrix["artifacts"].items():
        rx = re.compile(entry["pattern"])
        miss = [p for p, t in files if rx.search(t) and not covered(p, entry)]
        if miss:
            out[key] = miss
    return out


def scenario_ids():
    return set(re.findall(r"^\| (T\d{2}) \|", VALIDACAO.read_text(encoding="utf-8"), re.M))


class T02_InventarioCompleto(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.m = load(MATRIX_PATH)

    def test_matrix_names_its_baseline_and_schema(self):
        self.assertEqual(self.m["schema_version"], "handoff-f0-consumer-matrix/1")
        self.assertEqual(self.m["baseline_commit"], "85baf1018ca2b238c41745f7f13dbb539589867f")

    def test_every_required_authority_is_inventoried(self):
        self.assertEqual(REQUIRED - set(self.m["artifacts"]), set())

    def test_every_file_that_references_an_authority_is_inventoried(self):
        miss = unlisted(self.m, ROOT)
        self.assertEqual(miss, {}, "referencias a autoridades fora do inventario F0: {}".format(miss))

    def test_every_listed_file_exists(self):
        gone = []
        for key, entry in self.m["artifacts"].items():
            for c in entry["consumers"]:
                if not (ROOT / c["file"]).is_file():
                    gone.append((key, c["file"]))
            for mo in entry["mention_only"]:
                if not is_glob(mo["file"]) and not (ROOT / mo["file"]).is_file():
                    gone.append((key, mo["file"]))
        self.assertEqual(gone, [], "entradas do inventario sem ficheiro: {}".format(gone))

    def test_a_consumer_without_a_textual_reference_declares_how_it_reaches_the_authority(self):
        silent = []
        for key, entry in self.m["artifacts"].items():
            rx = re.compile(entry["pattern"])
            for c in entry["consumers"]:
                body = (ROOT / c["file"]).read_text(encoding="utf-8", errors="replace")
                if not rx.search(body) and not c.get("via"):
                    silent.append((key, c["file"]))
        self.assertEqual(silent, [], "consumidores sem referencia nem `via`: {}".format(silent))

    def test_every_writer_row_carries_verified_evidence(self):
        weak = [(key, c["file"]) for key, entry in self.m["artifacts"].items()
                for c in entry["consumers"]
                if c["role"] in WRITER_ROLES and (not c.get("evidence") or c.get("confidence") != "verified")]
        self.assertEqual(weak, [], "escritores sem evidencia verificada: {}".format(weak))

    def test_bulk_globs_never_hide_runtime_paths(self):
        excludes = set(self.m["scan"]["exclude"])
        runtime = [p for p, _ in text_files(ROOT, excludes)
                   if (p.startswith(RUNTIME_PREFIXES) or p in RUNTIME_FILES) and "/tests/" not in p]
        hidden = [(key, mo["file"], p) for key, entry in self.m["artifacts"].items()
                  for mo in entry["mention_only"] if is_glob(mo["file"])
                  for p in runtime if fnmatch.fnmatchcase(p, mo["file"])]
        self.assertEqual(hidden, [], "globs de mencao que cobrem runtime: {}".format(hidden))


class T02_DetectaOQueFalta(unittest.TestCase):
    """Caso negativo: o varrimento apanha um consumidor que ninguem inventariou."""

    def setUp(self):
        self.m = load(MATRIX_PATH)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_new_skill_writing_state_is_reported(self):
        rel = "/".join((".claude", "skills", "aisa-nova", "SKILL.md"))
        self.put(rel, "Grava `projects/<slug>/_state.json` (tmp -> rename).\n")
        self.assertIn(rel, unlisted(self.m, self.root).get("state", []))

    def test_new_hook_reading_su_is_reported(self):
        rel = "/".join((".claude", "hooks", "novo-guard.py"))
        self.put(rel, "SU = 'shared-understanding.md'\n")
        self.assertIn(rel, unlisted(self.m, self.root).get("su", []))

    def test_listed_consumer_is_not_reported(self):
        some = self.m["artifacts"]["state"]["consumers"][0]["file"]
        self.put(some, "_state.json\n")
        self.assertNotIn(some, unlisted(self.m, self.root).get("state", []))

    def test_excluded_directories_are_not_scanned(self):
        self.put("projects/demo/notes.md", "_state.json shared-understanding.md\n")
        miss = unlisted(self.m, self.root)
        self.assertFalse(any(p.startswith("projects/") for v in miss.values() for p in v), miss)


class F0_FixturesSinteticas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.reg = load(REGISTRY_PATH)
        cls.ids = scenario_ids()
        cls.dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir())

    def test_plan_declares_46_scenarios(self):
        self.assertEqual(self.ids, {"T%02d" % i for i in range(1, 47)})

    def test_every_new_fixture_is_registered_and_every_registered_path_exists(self):
        registered = {f["path"] for f in self.reg["new_fixtures"]}
        on_disk = {str(p.relative_to(ROOT)).replace(os.sep, "/") for p in self.dirs}
        self.assertEqual(on_disk, registered)
        for f in self.reg["reused_fixtures"]:
            self.assertTrue((ROOT / f["path"]).exists(), f["path"])

    def test_every_required_scenario_has_a_fixture(self):
        covered = {s for f in self.reg["new_fixtures"] for s in f["covers_required"]}
        self.assertEqual(set(self.reg["required_scenarios"]) - covered, set())

    def test_scenarios_are_synthetic_and_well_formed(self):
        names = {p.name for p in self.dirs}
        for d in self.dirs:
            s = load(d / "scenario.json")
            self.assertEqual(s["schema_version"], "handoff-f0-fixture/1", d.name)
            self.assertIs(s["synthetic"], True, d.name)
            self.assertEqual(s["id"], d.name)
            self.assertIn(s["route"], ROUTES, d.name)
            for dep in s.get("depends_on", []):
                self.assertIn(dep, names, d.name)
            for src in s["sources"]:
                self.assertTrue((d / src["path"]).is_file(), (d.name, src["path"]))

    def test_every_cited_anchor_exists_and_every_scenario_id_is_known(self):
        bad = []
        for d in self.dirs:
            s = load(d / "scenario.json")
            for item in s["expected"] + s.get("variants", []):
                for ref in item.get("source_refs", []):
                    path, _, anchor = ref.partition("#")
                    f = d / path
                    if not f.is_file() or "[%s]" % anchor not in f.read_text(encoding="utf-8"):
                        bad.append((d.name, item["id"], ref))
                bad += [(d.name, item["id"], t) for t in item.get("scenarios", []) if t not in self.ids]
        self.assertEqual(bad, [], "ancoras ou cenarios invalidos: {}".format(bad))

    def test_no_client_identifier_leaks_into_synthetic_fixtures(self):
        deny = [w.lower() for w in self.reg["forbidden_identifiers"]]
        self.assertTrue(deny)
        leaks = []
        for p in FIXTURES.rglob("*"):
            if p.is_file():
                body = p.read_text(encoding="utf-8").lower()
                leaks += [(str(p.relative_to(ROOT)), w) for w in deny if w in body]
        self.assertEqual(leaks, [], "identificadores de engagements reais em fixtures sinteticas: {}".format(leaks))


if __name__ == "__main__":
    unittest.main(verbosity=1)
