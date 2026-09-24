# -*- coding: utf-8 -*-
"""handoff-v1 F3.1 — etapa `lens` do coverage: a cobertura das seis perspectivas.

Contrato: `library/kernel/coverage-contract.md` §4.8. Desenho: `docs/handoff-v1/F3/
DESENHO.md` §2.

    T18  uma análise cobre seis lentes -> cobertura válida, a passagem fecha, sem seis
         ficheiros nem seis execuções
    T19  texto lista as lentes sem tratar o risco -> um título não conta como prova (regra
         fixa); o revisor independente marca a perspectiva não tratada (achado visível)
    T07  `not_applicable` sem motivo -> inválido, não fecha cobertura

Stdlib apenas. Engagement sintético (`test_migration.make`).
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FIX = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
M = runpy.run_path(str(TOOLS / "migrate.py"))
C = runpy.run_path(str(TOOLS / "coverage.py"))

DIMS = ("business", "operations", "user", "data", "governance", "financial")
REVISTA = {"status": "completed",
           "performed_by": {"kind": "agent", "name": "revisor independente"},
           "method": "leitura por perspectiva contra a SU publicada",
           "completed_at": "2026-09-23T21:00:00Z", "limitations": [],
           "dimensions": {d: {"verdict": "treated", "note": "prova trata o risco"}
                          for d in DIMS}}


def engagement(tmp):
    projects = Path(tmp) / "projects"
    projects.mkdir()
    eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
    M["apply"](eng)
    return eng


def rascunho(eng, ronda="R-01", **dims):
    sk = C["lens_skeleton"](eng, ronda)
    sk["generated_at"] = "2026-09-23T20:00:00Z"
    for d in DIMS:
        sk["lens_coverage"]["dimensions"][d] = {
            "status": "assessed", "refs": ["C-001"], "justification": "base partilhada"}
    for d, v in dims.items():
        sk["lens_coverage"]["dimensions"][d] = v
    sk["lens_coverage"]["conflict_scan"] = {"refs": [], "note": "nenhum conflito entre "
                                                                "fontes"}
    return sk


def publica(eng, rec, tmp):
    p = Path(tmp) / "draft-{}.json".format(abs(hash(json.dumps(rec, sort_keys=True))))
    p.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return C["finalize"](eng, p)


def erros(out, codigo=None):
    diags = out.get("diagnostics") or (out.get("result") or {}).get("diagnostics") or []
    return [d for d in diags if d["severity"] == "error"
            and (codigo is None or d["code"] == codigo)]


class T18_UmaAnaliseSeisLentes(unittest.TestCase):

    def test_one_record_covers_six_perspectives_and_closes_the_round(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            out = publica(eng, rascunho(eng), tmp)
            self.assertTrue(out["published"], out.get("message"))
            self.assertFalse((eng / "lens-outputs").exists(),
                             "a cobertura exigiu ficheiros por lente")
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["closes"], st["reasons"])
            self.assertEqual(set(st["dimensions"]), set(DIMS))

    def test_without_the_independent_review_it_closes_as_to_be_reviewed(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publica(eng, rascunho(eng), tmp)
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["closes"])
            self.assertFalse(st["reviewed"])
            self.assertIn("por rever", " ".join(st["reasons"]))

    def test_reviewed_by_someone_else_it_closes_reviewed(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            rec["semantic_review"] = REVISTA
            publica(eng, rec, tmp)
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["closes"] and st["reviewed"], st["reasons"])

    def test_a_gap_routed_to_an_open_question_is_valid_and_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng, data={"status": "gap", "refs": ["U-001"],
                                      "justification": "dono dos dados por saber"})
            rec["semantic_review"] = REVISTA
            publica(eng, rec, tmp)
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["reviewed"], st["reasons"])
            self.assertEqual(st["coverage"], "gaps")
            self.assertIn("LENS:data", [g["item"] for g in st["state"]["gaps"]])

    def test_another_rounds_record_does_not_close_this_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publica(eng, rascunho(eng, ronda="R-01"), tmp)
            st = C["lens_round_state"](eng, "R-02")
            self.assertFalse(st["closes"])
            self.assertIn("R-01", " ".join(st["reasons"]))

    def test_a_su_change_after_the_record_makes_it_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publica(eng, rascunho(eng), tmp)
            su = eng / "shared-understanding.md"
            su.write_text(su.read_text(encoding="utf-8").replace(
                "Base partilhada", "Base partilhada e revista"), encoding="utf-8")
            st = C["lens_round_state"](eng, "R-01")
            self.assertFalse(st["closes"])
            self.assertEqual(st["state"]["freshness"], "stale")


class T19_TituloNaoEProva(unittest.TestCase):
    """A regra fixa; o julgamento é do revisor independente (caso seguinte)."""

    def test_an_assessed_perspective_citing_only_a_heading_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            for ref in ("## business", "lens-outputs/business.md#R-01", "frame.md",
                        "C-999"):
                with self.subTest(ref=ref):
                    out = publica(eng, rascunho(eng, business={
                        "status": "assessed", "refs": [ref],
                        "justification": "o texto fala de negócio"}), tmp)
                    self.assertFalse(out["published"])
                    self.assertEqual(out["reason"], "schema")

    def test_a_dead_reference_beside_real_proof_blocks_the_reviewed_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng, business={"status": "assessed",
                                          "refs": ["C-001", "## business"],
                                          "justification": "x"})
            rec["semantic_review"] = REVISTA
            out = publica(eng, rec, tmp)
            self.assertTrue(out["published"])
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["closes"])
            self.assertFalse(st["reviewed"])
            self.assertTrue(erros(st["state"], "COV-DEAD-REF"))

    def test_locators_of_the_threshold_classes_prove_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            (eng / "_capture").mkdir()
            (eng / "_capture" / "process-model.md").write_text("# modelo\n",
                                                               encoding="utf-8")
            out = publica(eng, rascunho(
                eng, business={"status": "assessed", "refs": ["answers.md#U-001"],
                               "justification": "o dono respondeu"},
                operations={"status": "assessed", "refs": ["_capture/process-model.md"],
                            "justification": "o processo está modelado"}), tmp)
            self.assertTrue(out["published"], erros(out))

    def test_the_independent_reviewer_marks_an_untreated_perspective(self):
        """T19: o texto lista a perspectiva, a referência existe, e o risco não está
        tratado — só a leitura independente o vê. Fica achado à vista, e a passagem não
        fica «revista»."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            rec["semantic_review"] = json.loads(json.dumps(REVISTA))
            rec["semantic_review"]["dimensions"]["governance"] = {
                "verdict": "not_treated",
                "note": "C-001 não diz nada sobre quem pode aprovar"}
            publica(eng, rec, tmp)
            st = C["lens_round_state"](eng, "R-01")
            self.assertTrue(st["closes"])
            self.assertFalse(st["reviewed"])
            self.assertEqual(st["coverage"], "gaps")
            self.assertIn("governance", " ".join(st["reasons"]))

    def test_the_reviewer_is_not_the_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            rec["semantic_review"] = dict(REVISTA, performed_by={
                "kind": "agent", "name": rec["lens_coverage"]["author"]["name"]})
            publica(eng, rec, tmp)
            st = C["lens_round_state"](eng, "R-01")
            self.assertEqual(st["semantic_review"], "pending")
            self.assertFalse(st["reviewed"])

    def test_not_applicable_ok_only_over_a_not_applicable_perspective(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            rec["semantic_review"] = json.loads(json.dumps(REVISTA))
            rec["semantic_review"]["dimensions"]["user"] = {"verdict": "not_applicable_ok",
                                                            "note": "x"}
            publica(eng, rec, tmp)
            self.assertEqual(C["lens_round_state"](eng, "R-01")["semantic_review"],
                             "pending")


class T07_NaoAplicavelSemMotivo(unittest.TestCase):

    def test_not_applicable_without_reason_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            out = publica(eng, rascunho(eng, user={"status": "not_applicable", "refs": [],
                                                   "justification": "  "}), tmp)
            self.assertFalse(out["published"])
            self.assertTrue(any("T07" in d["message"] for d in erros(out)))

    def test_not_applicable_with_reason_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            out = publica(eng, rascunho(eng, user={
                "status": "not_applicable", "refs": [],
                "justification": "integração sem utilizador humano"}), tmp)
            self.assertTrue(out["published"])


class Forma(unittest.TestCase):

    def test_all_six_perspectives_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            del rec["lens_coverage"]["dimensions"]["financial"]
            self.assertFalse(publica(eng, rec, tmp)["published"])

    def test_a_gap_needs_an_open_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            out = publica(eng, rascunho(eng, data={"status": "gap", "refs": ["C-001"],
                                                   "justification": "x"}), tmp)
            self.assertFalse(out["published"])

    def test_the_conflict_scan_is_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            for cs in ({"refs": [], "note": ""}, {"refs": ["X-404"], "note": ""}, None):
                with self.subTest(cs=cs):
                    rec = rascunho(eng)
                    rec["lens_coverage"]["conflict_scan"] = cs
                    self.assertFalse(publica(eng, rec, tmp)["published"])

    def test_lens_coverage_only_on_the_lens_stage_and_lens_has_no_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng)
            rec["target"] = {"file": "shared-understanding.md"}
            self.assertFalse(publica(eng, rec, tmp)["published"])


class Esqueleto(unittest.TestCase):

    def test_the_skeleton_inherits_perspectives_never_the_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rec = rascunho(eng, user={"status": "not_applicable", "refs": [],
                                      "justification": "sem utilizador"})
            rec["semantic_review"] = REVISTA
            publica(eng, rec, tmp)
            sk = C["lens_skeleton"](eng, "R-02")
            self.assertEqual(sk["lens_coverage"]["dimensions"]["user"]["status"],
                             "not_applicable")
            self.assertEqual(sk["semantic_review"]["status"], "not_started")
            self.assertEqual(sk["based_on"], ["coverage_v01.json"])
            self.assertEqual(sk["lens_coverage"]["round"], "R-02")

    def test_the_report_projects_the_perspectives(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            out = publica(eng, rascunho(eng), tmp)
            md = (eng / out["md"]).read_text(encoding="utf-8")
            self.assertIn("## Perspectivas", md)
            self.assertIn("| governance | assessed |", md)


class CLI(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run([sys.executable, str(TOOLS / "coverage.py")] + list(args),
                              capture_output=True, text=True, timeout=300,
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"))

    def test_lens_draft_and_round_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            p = self._run("lens-draft", "--engagement", str(eng), "--round", "R-01")
            self.assertEqual(p.returncode, 0, p.stderr)
            sk = json.loads(p.stdout)
            self.assertEqual(sk["stage"], "lens")
            p = self._run("round-state", "--engagement", str(eng), "--round", "R-01",
                          "--json")
            self.assertEqual(p.returncode, 4)
            self.assertFalse(json.loads(p.stdout)["closes"])
            publica(eng, rascunho(eng), tmp)
            p = self._run("round-state", "--engagement", str(eng), "--round", "R-01",
                          "--json")
            self.assertEqual(p.returncode, 0, p.stdout)
            p = self._run("check", "--engagement", str(eng), "--stage", "lens", "--json")
            self.assertEqual(json.loads(p.stdout)["stage"], "lens")


if __name__ == "__main__":
    unittest.main()
