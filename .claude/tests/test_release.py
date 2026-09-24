# -*- coding: utf-8 -*-
"""handoff-v1 F6.5 — release, segredos e aceitação do destinatário.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §5 (Q4, Q5, Q6).

    nível   calculado, nunca declarado: `preliminary` enquanto falta ou não bate;
            `ready_for_receiver_review` quando o rastreio, o gate de âmbito, a spec e a
            estimativa passam; `accepted_by_receiver` só com o bloco de aceitação não simulado
    T39     um ficheiro alterado, a mais ou a menos depois do release → não verifica
    T40     um segredo num rascunho publicado ou num ficheiro do pacote → recusado; a
            referência segura passa
    imutável  cada release numa revisão nova; nunca se escreve por cima
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_trace.py"))
SG = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_scope_gate.py"))
IT, AU = TT["IT"], SG["AU"]
VT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_vertical.py"))
REL = runpy.run_path(str(TOOLS / "release.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
SPEC = ("# Implementation Specification\n\n### Inventário de trabalho (inventário r1)\n\n"
        "| WP | Propósito |\n|---|---|\n| WP-0001 | Submissão idempotente |\n"
        "| WP-0002 | Aprovação com segregação |\n")


def _decisao(eng, bloco):
    d = R["draft"](eng, ["decisions.md"])
    p = eng / "_drafts" / d["draft"] / "decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + bloco, encoding="utf-8", newline="\n")
    R["publish"](eng, d["draft"])


def pronto(tmp, render=True, revalidar=True):
    """O pacote pronto. `revalidar=False` deixa os FC no sha do desenho anterior à mudança
    que a fixture faz — é o caso A5 da auditoria (`test_audit_f6f7.py`)."""
    eng = IT["engagement"](tmp)
    p = eng / IT["BP"]
    p.write_text(p.read_text(encoding="utf-8").replace(
        "name: valor_total, type: number, required: true",
        "name: valor_total, type: number, required: false"), encoding="utf-8")
    _decisao(eng, F["blueprint_approval_block"](eng, "01", AU["OWNER"],
                                                timestamp="2026-09-24T08:00:00Z"))
    if revalidar:
        IT["revalida_fc_desenho"](eng, "valor_total passou a opcional no desenho; nenhum "
                                       "contrato o exige")
    s = TT["escopo"](eng)
    s["items"][0]["excludes"].append(SG["U002_FORA"])
    IT["publish"](eng, "scope", s)
    IT["publish"](eng, "work-packages", IT["inventario"](eng, TT["wps"]()))
    if render:
        (eng / "_render").mkdir()
        (eng / "_render" / "fx_implementation-spec_v01.md").write_text(SPEC, encoding="utf-8")
        (eng / "_render" / "fx_estimate_v01.md").write_text(SG["EST"], encoding="utf-8")
    return eng


def rerender(eng):
    """A spec e a estimativa voltam a ser renderizadas sobre o inventário corrente (fixture:
    só a revisão citada muda — T32 compara ids e a revisão lida)."""
    import re
    rev = json.loads((eng / "_design/work-packages.json").read_text(encoding="utf-8"))["revision"]
    for p in (eng / "_render").glob("*.md"):
        p.write_text(re.sub(r"((?:[Ii]nvent[aá]rio|inventory)\s*r)\d+", r"\g<1>{}".format(rev),
                            p.read_text(encoding="utf-8")), encoding="utf-8")


class Build(unittest.TestCase):

    def test_ready_when_every_check_passes_and_the_index_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp)
            r = REL["build"](eng)
            self.assertEqual(r["delivery_level"], "ready_for_receiver_review", r["reasons"])
            pkg = Path(r["path"])
            idx = json.loads((pkg / "handoff-index.json").read_text(encoding="utf-8"))
            self.assertEqual(idx["scope_refs"], ["SCOPE-0001"])
            self.assertIn("FC-0002", [e["ref"] for e in idx["exclusions"]])
            self.assertIsNone(idx["receiver_acceptance"])
            self.assertEqual(idx["proofs"]["performed"], [])
            for f in ("functional-state.json", "trace.json", "scope-gate.json",
                      "library/kernel/handoff-contract.md", "_design/work-packages.json",
                      "_render/fx_estimate_v01.md"):
                self.assertTrue((pkg / f).is_file(), f)
            self.assertTrue(REL["verify"](pkg)["ok"])

    def test_preliminary_while_the_spec_or_estimate_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = REL["build"](pronto(tmp, render=False))
            self.assertEqual(r["delivery_level"], "preliminary")
            self.assertIn("implementation-spec não renderizada", r["reasons"])

    def test_a_blocked_scope_is_never_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = REL["build"](TT["montado"](tmp))
            self.assertEqual(r["delivery_level"], "preliminary")
            self.assertTrue(any("gate de âmbito bloqueado" in m for m in r["reasons"]))

    def test_each_release_is_a_new_immutable_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp)
            r1 = REL["build"](eng)
            antes = (Path(r1["path"]) / "handoff-index.json").read_bytes()
            r2 = REL["build"](eng)
            self.assertEqual((r1["revision"], r2["revision"]), (1, 2))
            self.assertEqual((Path(r1["path"]) / "handoff-index.json").read_bytes(), antes)
            with self.assertRaises(REL["ReleaseError"]):
                REL["build"](eng, out=r1["path"])


class IndiceDoRelease(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng = VT["percurso"](cls.tmp.name)[0]
        pkg = Path(REL["build"](cls.eng)["path"])
        cls.idx = json.loads((pkg / "handoff-index.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_r1_the_index_names_every_decision_it_rests_on(self):
        for d in ("D-001", "D-002", "D-003", "D-004"):
            self.assertIn("decisions.md#" + d, self.idx["authorization_refs"])

    def test_r2_the_index_says_what_each_review_read(self):
        rb = self.idx["reviews_basis"]["REV-0001"]
        self.assertEqual(rb["candidate_revision"], 1)
        self.assertEqual(rb["inputs"]["decisions.md"]["now"], "changed since the review")

    def test_r4_a_decision_dated_after_the_build_is_a_limitation(self):
        _decisao(self.eng, "\n## D-009 — nota\n\n- **Timestamp**: 2999-01-01T00:00:00Z\n")
        pkg = Path(REL["build"](self.eng)["path"])
        idx = json.loads((pkg / "handoff-index.json").read_text(encoding="utf-8"))
        self.assertTrue(any("D-009 (2999-01-01T00:00:00Z)" in m for m in idx["limitations"]))


class Verificacao(unittest.TestCase):

    def test_t39_a_changed_missing_or_extra_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(REL["build"](pronto(tmp))["path"])
            (pkg / "decisions.md").write_text("alterado", encoding="utf-8")
            (pkg / "extra.md").write_text("x", encoding="utf-8")
            (pkg / "trace.json").unlink()
            v = REL["verify"](pkg)
            self.assertFalse(v["ok"])
            self.assertEqual((v["mismatch"], v["extra"], v["missing"]),
                             (["decisions.md"], ["extra.md"], ["trace.json"]))

    def test_t40_a_secret_in_a_source_refuses_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp)
            (eng / "inputs" / "nota-chave.md").write_text(
                "Server=erp;Password=Sup3rS3cret99;", encoding="utf-8")
            with self.assertRaises(REL["ReleaseError"]) as err:
                REL["build"](eng)
            self.assertEqual(err.exception.detail["code"], "SECRET_IN_CONTENT")
            self.assertNotIn("Sup3rS3cret99", json.dumps(err.exception.detail))
            self.assertFalse((eng / "_release").exists())

    def test_t40_the_coordinator_refuses_a_secret_and_keeps_the_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp, render=False)
            with self.assertRaises(O["OperationError"]) as err:
                O["run"](eng, "t40", {"answers.md": "a chave: Password=Sup3rS3cret99"},
                         expected={"answers.md": O["digest"](eng / "answers.md")})
            self.assertEqual(err.exception.code, "SECRET_IN_CONTENT")
            self.assertEqual(O["response_from_error"](err.exception)["code"],
                             "INTEGRITY_FAILURE")
            r = O["run"](eng, "t40-ref", {"answers.md": "a chave: Password=<vault:erp-x-test>"},
                         expected={"answers.md": O["digest"](eng / "answers.md")})
            self.assertTrue(r)


class Aceitacao(unittest.TestCase):

    def test_q6_acceptance_is_its_own_block_and_simulation_is_labelled(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp)
            REL["build"](eng)
            with self.assertRaises(REL["ReleaseError"]):
                REL["acceptance_block"](eng, 1, "claude", "SCOPE-0001", "")
            sim = REL["acceptance_block"](eng, 1, AU["OWNER"], "SCOPE-0001", "nenhuma",
                                          simulated=True, timestamp="2026-09-24T10:00:00Z")
            _decisao(eng, sim)
            s = REL["status"](eng, 1)
            self.assertEqual(s["delivery_level"], "ready_for_receiver_review")
            self.assertTrue(s["acceptance"]["simulated"])
            real = REL["acceptance_block"](eng, 1, AU["OWNER"], "SCOPE-0001",
                                           "provas V2 antes do go-live",
                                           timestamp="2026-09-24T11:00:00Z")
            _decisao(eng, real)
            self.assertEqual(REL["status"](eng, 1)["delivery_level"], "accepted_by_receiver")

    def test_a_tampered_release_is_neither_accepted_nor_kept_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto(tmp)
            pkg = Path(REL["build"](eng)["path"])
            _decisao(eng, REL["acceptance_block"](eng, 1, AU["OWNER"], "SCOPE-0001", "",
                                                  timestamp="2026-09-24T11:00:00Z"))
            (pkg / "decisions.md").write_text("alterado", encoding="utf-8")
            self.assertEqual(REL["status"](eng, 1)["delivery_level"], "preliminary")
            with self.assertRaises(REL["ReleaseError"]):
                REL["acceptance_block"](eng, 1, AU["OWNER"], "SCOPE-0001", "")


if __name__ == "__main__":
    unittest.main()
