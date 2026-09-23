# -*- coding: utf-8 -*-
"""handoff-v1 F5.2 — router explicável e mandatos publicados antes do revisor.

Desenho: `docs/handoff-v1/F5/DESENHO.md` §2 (Q3, Q5).

    T25  sem candidatos publicados, ou com um rascunho de candidatos aberto, nenhum mandato
         nasce: um candidato em construção nunca é revisto
    T28  o router devolve os papéis seleccionados com a evidência que os activou e os não
         chamados com o que se verificou; determinístico; headless dispensa UX
    T29  (mandato) as unidades do pack permitidas levam caminho, `sha256` e versão do pack;
         uma unidade fora do pack activo é recusada
"""
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
CA = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_review_candidates.py"))
RV = runpy.run_path(str(TOOLS / "review.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
UNIDADE = "library/packs/pp/architecture-templates/architecture-core.md"
PAPEIS = {"architecture-review", "data-integration", "security-operation", "ux-process",
          "cost-estimate"}


def publicado(tmp, route="platform-constrained", **over):
    eng = CA["engagement"](tmp, route)
    extra = {"imposed_platform": "Plataforma X", "imposition_ref": CA["AUTORIDADE"],
             "reduction_reason": "uma forma viável dentro da imposta"} \
        if route == "platform-constrained" else {}
    CA["publish"](eng, CA["conjunto"](eng, [CA["cand"]("O-001", **over)], **extra))
    return eng


def blueprint(eng, body):
    (eng / "_blueprint").mkdir(exist_ok=True)
    (eng / "_blueprint" / "ux-blueprint_v01.yaml").write_text(
        "version: v01\ndraft: false\n" + body, encoding="utf-8", newline="\n")


class Router(unittest.TestCase):

    def test_t28_every_role_is_evaluated_with_evidence_or_justification(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            r = RV["route"](eng)
            sel = {s["role"]: s["evidence"] for s in r["selected"]}
            nao = {n["role"]: n["justification"] for n in r["not_called"]}
            self.assertEqual(set(sel) | set(nao), PAPEIS)
            self.assertFalse(set(sel) & set(nao))
            self.assertIn("always_in:options", sel["architecture-review"][0])
            self.assertIn("C-004 (governance)", sel["security-operation"])
            self.assertIn("C-005 (user)", sel["ux-process"])
            self.assertIn("nenhum sinal — verificado", nao["data-integration"])
            self.assertIn("nenhum sinal — verificado", nao["cost-estimate"])
            self.assertEqual(r["candidate_revision"], 1)

    def test_t28_a_parked_row_never_selects(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            ux = next(s for s in RV["route"](eng)["selected"] if s["role"] == "ux-process")
            self.assertFalse([e for e in ux["evidence"] if e.startswith("U-003")])

    def test_t28_the_same_inputs_give_the_same_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            self.assertEqual(RV["route"](eng), RV["route"](eng))

    def test_t28_design_and_candidate_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp, order_of_magnitude={"value": "?"})
            blueprint(eng, "architecture:\n  record_authority:\n    - key: fornecedores\n"
                      "      access_mode: referenced\n  compositions:\n"
                      "    - component: envio-erp\n      boundary: outside-platform\n")
            sel = {s["role"]: s["evidence"] for s in RV["route"](eng)["selected"]}
            self.assertIn("external-access: _blueprint/ux-blueprint_v01.yaml#fornecedores",
                          sel["data-integration"])
            self.assertIn("outside-platform: _blueprint/ux-blueprint_v01.yaml#envio-erp",
                          sel["security-operation"])
            self.assertIn("om-unavailable: O-001", sel["cost-estimate"])

    def test_t28_a_headless_design_owes_no_ux_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            blueprint(eng, "architecture:\n  experience:\n    mode: none\n")
            nao = {n["role"]: n["justification"] for n in RV["route"](eng)["not_called"]}
            self.assertIn("não aplicável: headless", nao["ux-process"])


class Mandato(unittest.TestCase):

    def test_t25_no_mandate_without_published_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = CA["engagement"](tmp)
            with self.assertRaises(RV["ReviewError"]) as err:
                RV["mandate"](eng, "architecture-review", ["a forma cabe no volume?"])
            self.assertEqual(err.exception.code, "BLOCKING_GAP")
            self.assertFalse((eng / RV["REVIEWS_DIR"]).exists())

    def test_t25_no_mandate_while_a_candidates_draft_is_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            dr = RV["draft_candidates"](eng)
            with self.assertRaises(RV["ReviewError"]) as err:
                RV["mandate"](eng, "architecture-review", ["a forma cabe no volume?"])
            self.assertEqual(err.exception.code, "BLOCKING_GAP")
            self.assertEqual(err.exception.detail["drafts"], [dr["draft"]])

    def test_the_mandate_is_published_by_the_coordinator_with_its_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            m = RV["mandate"](eng, "security-operation", ["a segregação (C-004) é aplicada?"],
                              scope_ids=["O-001", "C-004"])
            self.assertEqual(m["task_id"], "REV-0001")
            self.assertTrue(m["receipt"])
            d = RV["read_mandate"](eng, "REV-0001")
            for k in ("task_id", "role", "objective", "scope_ids", "questions", "input_refs",
                      "candidate_revision", "knowledge_refs", "output_contract",
                      "stop_conditions", "budget", "prohibited_actions"):
                self.assertIn(k, d)
            self.assertEqual(d["candidate_revision"], 1)
            refs = {r["ref"]: r["sha256"] for r in d["input_refs"]}
            self.assertEqual(refs["_design/candidates.json"],
                             O["digest"](eng / "_design/candidates.json"))
            self.assertEqual(RV["mandate"](eng, "ux-process", ["x?"])["task_id"], "REV-0002")

    def test_t29_pack_units_carry_path_digest_and_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            d = RV["mandate"](eng, "architecture-review", ["x?"], knowledge=[UNIDADE])["data"]
            k = d["knowledge_refs"][0]
            self.assertEqual(k["ref"], UNIDADE)
            self.assertEqual(k["sha256"], O["digest"](ROOT / UNIDADE))
            self.assertEqual(k["pack"], "pp")
            self.assertRegex(k["pack_version"], r"^\d+\.\d+\.\d+$")

    def test_t29_a_unit_outside_the_active_pack_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            for fora in ("library/kernel/states.md", "library/packs/pp/" + "nao-existe.md"):
                with self.assertRaises(RV["ReviewError"]) as err:
                    RV["mandate"](eng, "architecture-review", ["x?"], knowledge=[fora])
                self.assertEqual(err.exception.code, "INTEGRITY_FAILURE")

    def test_an_unknown_role_or_no_question_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = publicado(tmp)
            for role, qs in (("business-analyst", ["x?"]), ("architecture-review", [" "])):
                with self.assertRaises(RV["ReviewError"]) as err:
                    RV["mandate"](eng, role, qs)
                self.assertEqual(err.exception.code, "INTEGRITY_FAILURE")

    def test_the_roles_in_the_rules_are_the_roles_in_the_table(self):
        text = (ROOT / "library/kernel/specialists.md").read_text(encoding="utf-8")
        self.assertEqual({r["role"] for r in RV["router_rules"]()}, PAPEIS)
        for p in PAPEIS:
            self.assertIn("| `{}` |".format(p), text)


if __name__ == "__main__":
    unittest.main()
