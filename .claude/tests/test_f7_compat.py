# -*- coding: utf-8 -*-
"""handoff-v1 F7.3 — versões suportadas, restore sem força e rollback de código.

Desenho: `docs/handoff-v1/F7/DESENHO.md` §2 (Q4).

    tabela   `workflow.SUPPORTED` é a única resposta a «que versão esta versão lê»; as
             constantes dos motores não divergem dela
    T36      um artefacto de versão fora da tabela (futura, ou sem `schema_version`) é recusado
             por todos os leitores com `SCHEMA_UNSUPPORTED`, sem tocar em nenhum ficheiro
    D10      `migrate.restore` não tem força: com trabalho posterior à migração recusa sempre,
             e a decisão acrescentada depois fica
    rollback o código do fim da F5 (`56cb4e1`) escreve num engagement da F6 sem tocar nos
             artefactos que não conhece (âmbito, inventário, release)
"""
import inspect
import json
import runpy
import shutil
import subprocess
import sys
import tarfile
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
RT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_release.py"))
MT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
W = runpy.run_path(str(TOOLS / "workflow.py"))
F = RT["F"]
REL = RT["REL"]
INV = runpy.run_path(str(TOOLS / "inventory.py"))
RV = runpy.run_path(str(TOOLS / "review.py"))
TR = runpy.run_path(str(TOOLS / "trace.py"))
I = runpy.run_path(str(TOOLS / "impact.py"))
M = MT["M"]
O = MT["O"]
FIM_F5 = "56cb4e1"


def pegada(eng):
    return {p.relative_to(eng).as_posix(): p.read_bytes()
            for p in Path(eng).rglob("*") if p.is_file()}


def _futuro(eng, rel):
    p = eng / rel
    d = json.loads(p.read_text(encoding="utf-8"))
    d["schema_version"] = W["supported_schema"](rel).rsplit("/", 1)[0] + "/2"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class Tabela(unittest.TestCase):

    def test_the_engines_read_what_the_table_says(self):
        s = W["supported_schema"]
        self.assertEqual(s("_state.json#workflow"), W["STATE_SCHEMA"])
        self.assertEqual(s("_work/checkpoint.json"), W["WORK_SCHEMA"])
        self.assertEqual(s(F["FC_PATH"]), F["SCHEMA"])
        for k in INV["KINDS"].values():
            self.assertEqual(s(k["path"]), k["schema"])
        self.assertEqual(s(RV["CAND_PATH"]), RV["SCHEMA"])
        self.assertEqual(s(RV["LEDGER_PATH"]), RV["LEDGER_SCHEMA"])
        self.assertEqual(s("_design/reviews/REV-0001.json"), RV["REVIEW_SCHEMA"])
        self.assertEqual(s("_design/reviews/REV-0001.mandate.json"), "aisa-review-mandate/1")
        self.assertEqual(s("_release/r0001/handoff-index.json"), "handoff-index/1")

    def test_drafts_and_history_are_not_published_artefacts(self):
        for rel in ("_drafts/fc-1/functional-contracts.json",
                    "_design/history/candidates.r0001.json", "shared-understanding.md"):
            self.assertEqual(W["supported_schema"](rel), "")


class T36Alargado(unittest.TestCase):
    """Cada leitor, contra a mesma cópia pronta com um artefacto de versão futura."""

    LEITORES = {
        "_design/functional-contracts.json": [lambda e: F["read_current"](e),
                                              lambda e: I["stale"](e)],
        "_design/scope.json": [lambda e: INV["read_current"](e, "scope"),
                               lambda e: TR["scope_gate"](e)],
        "_design/work-packages.json": [lambda e: INV["read_current"](e, "work-packages"),
                                       lambda e: I["stale"](e)],
        "_design/candidates.json": [lambda e: RV["read_candidates"](e),
                                    lambda e: I["stale"](e)],
        "_design/reviews/ledger.json": [lambda e: RV["read_ledger"](e),
                                        lambda e: RV["show_reviews"](e)],
        "_design/reviews/REV-0001.json": [lambda e: RV["read_review"](e, "REV-0001")],
        "_design/reviews/REV-0001.mandate.json": [lambda e: RV["read_mandate"](e, "REV-0001"),
                                                  lambda e: I["stale"](e)],
    }

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.base = RT["pronto"](cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _copia(self, tmp):
        eng = Path(tmp) / "eng"
        shutil.copytree(self.base, eng)
        return eng

    def test_every_reader_refuses_a_future_version_and_touches_nothing(self):
        for rel, leitores in self.LEITORES.items():
            for i, ler in enumerate(leitores):
                with self.subTest(artefacto=rel, leitor=i), \
                        tempfile.TemporaryDirectory() as tmp:
                    eng = self._copia(tmp)
                    _futuro(eng, rel)
                    antes = pegada(eng)
                    with self.assertRaises(Exception) as err:
                        ler(eng)
                    self.assertEqual(getattr(err.exception, "code", None), "SCHEMA_UNSUPPORTED",
                                     err.exception)
                    self.assertEqual(pegada(eng), antes)

    def test_a_missing_schema_version_is_not_read_as_the_current_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self._copia(tmp)
            p = eng / "_design/scope.json"
            d = json.loads(p.read_text(encoding="utf-8"))
            del d["schema_version"]
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(Exception) as err:
                TR["scope_gate"](eng)
            self.assertEqual(err.exception.code, "SCHEMA_UNSUPPORTED")
            self.assertIn("`None`", str(err.exception))

    def test_a_publication_over_a_future_version_is_refused_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self._copia(tmp)
            _futuro(eng, "_design/work-packages.json")
            antes = pegada(eng)
            with self.assertRaises(INV["InventoryError"]) as err:
                INV["draft"](eng, "work-packages")
            self.assertEqual(err.exception.code, "SCHEMA_UNSUPPORTED")
            self.assertEqual(pegada(eng), antes)

    def test_a_release_index_of_another_version_does_not_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self._copia(tmp)
            pkg = Path(REL["build"](eng)["path"])
            self.assertTrue(REL["verify"](pkg)["ok"])
            _futuro(pkg.parent.parent, pkg.relative_to(pkg.parent.parent).as_posix()
                    + "/handoff-index.json")
            v = REL["verify"](pkg)
            self.assertEqual((v["ok"], v["code"]), (False, "SCHEMA_UNSUPPORTED"))


class D10(unittest.TestCase):

    def test_restore_has_no_force(self):
        self.assertNotIn("force", inspect.signature(M["restore"]).parameters)
        with tempfile.TemporaryDirectory() as tmp:
            eng = MT["make"](tmp, MT["RESOLVIDO"])
            p = subprocess.run([sys.executable, str(TOOLS / "migrate.py"), "restore",
                                "--engagement", str(eng), "--force"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn("--force", p.stderr)

    def test_a_decision_added_after_the_migration_survives_the_refused_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = MT["make"](tmp, MT["RESOLVIDO"])
            M["apply"](eng)
            md = (eng / "decisions.md").read_text(encoding="utf-8")
            O["run"](eng, "decisao-nova", {"decisions.md": md + "\n## D-099 — Nova\n"})
            with self.assertRaises(M["MigrationError"]) as err:
                M["restore"](eng)
            self.assertEqual(err.exception.code, "WORK_AFTER")
            self.assertIn("decisions.md", err.exception.detail["changed"])
            self.assertIn("D-099", (eng / "decisions.md").read_text(encoding="utf-8"))


class RollbackDeCodigo(unittest.TestCase):
    """O código do fim da F5, tal como está no commit, contra um engagement da F6."""

    @classmethod
    def setUpClass(cls):
        existe = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                                 FIM_F5 + "^{commit}"], capture_output=True)
        if existe.returncode != 0:
            raise AssertionError("o commit {} não está no clone: o CI precisa de "
                                 "`fetch-depth: 0`".format(FIM_F5))
        cls.velho = Path(tempfile.mkdtemp())
        arq = subprocess.run(["git", "-C", str(ROOT), "archive", FIM_F5, "library"],
                             capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(arq)) as tf:
            tf.extractall(cls.velho)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.velho, ignore_errors=True)

    def test_the_old_code_does_not_know_the_f6_artefacts(self):
        self.assertFalse((self.velho / "library/kernel/tools/inventory.py").exists())
        self.assertFalse((self.velho / "library/kernel/tools/release.py").exists())

    def test_the_old_code_publishes_without_touching_what_it_does_not_know(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = RT["pronto"](tmp)
            REL["build"](eng)
            desconhecidos = lambda: {k: v for k, v in pegada(eng).items()
                                     if k.startswith(("_design/scope", "_design/work-packages",
                                                      "_release/"))}
            antes = desconhecidos()
            self.assertTrue(any(k.startswith("_release/") for k in antes))
            R0 = runpy.run_path(str(self.velho / "library/kernel/tools/resolve.py"))
            d = R0["draft"](eng, ["decisions.md"])
            p = eng / "_drafts" / d["draft"] / "decisions.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n## D-090 — Escrito pelo código "
                         "da F5\n", encoding="utf-8", newline="\n")
            R0["publish"](eng, d["draft"])
            self.assertIn("D-090", (eng / "decisions.md").read_text(encoding="utf-8"))
            self.assertEqual(desconhecidos(), antes)
            # e o código de agora continua a ler o engagement e a ver a escrita antiga
            self.assertTrue(REL["verify"](Path(REL["build"](eng)["path"]))["ok"])


if __name__ == "__main__":
    unittest.main()
