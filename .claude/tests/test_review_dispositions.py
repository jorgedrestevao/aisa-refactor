# -*- coding: utf-8 -*-
"""handoff-v1 F5.3 — pareceres, disposições e dialéctica limitada.

Desenho: `docs/handoff-v1/F5/DESENHO.md` §3.

    T26  um parecer de uma revisão anterior dos candidatos fica `stale`: não fecha achado da
         revisão corrente, e só se revalida o que o candidato novo afecta
    T29  (parecer) cada fonte usada estava no mandato, com o mesmo `sha256`, e não mudou
    T30  divergência material com contador: 2 chamadas sem síntese aceite → `escalated`; a
         quarta divergência na mesma revisão já nasce `escalated`; nunca aceite por esgotamento
    zero confirmação por maioria: receber e dispor pareceres nunca escreve na SU
"""
import runpy
import tempfile
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
CA = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_review_candidates.py"))
RT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_review_router.py"))
RV = runpy.run_path(str(TOOLS / "review.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
Q = "a forma escolhida aguenta o pico de fim de mês?"
IMPOSTA = {"imposed_platform": "Plataforma X", "imposition_ref": CA["AUTORIDADE"],
           "reduction_reason": "duas formas viáveis dentro da imposta"}


def dois(tmp):
    eng = CA["engagement"](tmp, "platform-constrained")
    CA["publish"](eng, CA["conjunto"](eng, [CA["cand"]("O-001"), CA["cand"]("O-002")],
                                      **IMPOSTA))
    return eng


def mandato(eng, role="architecture-review"):
    return RV["mandate"](eng, role, [Q], knowledge=[RT["UNIDADE"]])["data"]


def parecer(m, findings=None, **over):
    fontes = [r for r in m["input_refs"] if r["ref"] == "_design/candidates.json"] \
        + m["knowledge_refs"]
    p = {"task_id": m["task_id"], "role": m["role"], "input_revision": m["candidate_revision"],
         "coverage": [{"question": Q, "checked": "volume de fim de mês contra o limite"}],
         "findings": findings if findings is not None else [achado("O-001")],
         "assumptions": [], "unanswered": [], "recommended_actions": [],
         "sources_used": [{"ref": r["ref"], "sha256": r["sha256"]} for r in fontes]}
    p.update(over)
    return p


def achado(target, kind="recommendation", severity="blocking"):
    return {"target": target, "severity": severity, "kind": kind,
            "evidence": "o pico de fim de mês (C-003) excede o limite da forma",
            "failure_scenario": "pedidos urgentes ficam presos no fim de mês",
            "closing_condition": "prova de carga no volume de fim de mês"}


def refused(test, fn, code, problem=None):
    with test.assertRaises(RV["ReviewError"]) as err:
        fn()
    test.assertEqual(err.exception.code, code)
    if problem:
        test.assertIn(problem, [p["code"] for p in err.exception.detail["problems"]])
    return err.exception


class Parecer(unittest.TestCase):

    def test_a_valid_review_is_published_once_with_finding_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            r = RV["receive"](eng, m["task_id"], parecer(m))
            self.assertEqual(r["findings"], ["REV-0001.F01"])
            self.assertTrue(r["receipt"])
            self.assertTrue(RV["receive"](eng, m["task_id"], parecer(m))["replayed"])
            refused(self, lambda: RV["receive"](eng, m["task_id"], parecer(
                m, findings=[achado("O-002")])), "INTEGRITY_FAILURE")

    def test_every_question_is_covered_or_declared_unanswered(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            refused(self, lambda: RV["receive"](eng, m["task_id"], parecer(m, coverage=[])),
                    "INTEGRITY_FAILURE", "UNCOVERED_QUESTION")
            RV["receive"](eng, m["task_id"], parecer(m, coverage=[], unanswered=[
                {"question": Q, "reason": "sem volume medido nas fontes"}]))

    def test_the_review_reads_the_mandated_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            refused(self, lambda: RV["receive"](eng, m["task_id"], parecer(
                m, input_revision=2)), "INTEGRITY_FAILURE", "INPUT_REVISION")

    def test_t29_sources_outside_the_mandate_or_with_another_digest_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            fora = parecer(m)
            fora["sources_used"].append({"ref": "library/packs/pp/decision-tree.md",
                                         "sha256": O["digest"](ROOT / "library/packs/pp/"
                                                               "decision-tree.md")})
            refused(self, lambda: RV["receive"](eng, m["task_id"], fora),
                    "INTEGRITY_FAILURE", "SOURCE_NOT_IN_MANDATE")
            outro = parecer(m)
            outro["sources_used"][0]["sha256"] = "0" * 64
            refused(self, lambda: RV["receive"](eng, m["task_id"], outro),
                    "INTEGRITY_FAILURE", "SOURCE_DIGEST")

    def test_t29_a_source_changed_after_the_mandate_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            su = next(r for r in m["input_refs"] if r["ref"] == "shared-understanding.md")
            p = parecer(m)
            p["sources_used"].append(dict(su))
            f = eng / "shared-understanding.md"
            f.write_text(f.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            refused(self, lambda: RV["receive"](eng, m["task_id"], p), "STALE_INPUT")
            self.assertFalse((eng / "_design/reviews/REV-0001.json").exists())


class Stale(unittest.TestCase):

    def test_t26_a_new_revision_makes_the_review_stale_and_scopes_revalidation(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            RV["receive"](eng, m["task_id"], parecer(m, findings=[achado("O-001"),
                                                                  achado("O-002")]))
            self.assertEqual(RV["show_reviews"](eng)["open_findings"],
                             ["REV-0001.F01", "REV-0001.F02"])
            CA["publish"](eng, CA["conjunto"](eng, [CA["cand"]("O-001", architecture="outra"),
                                                    CA["cand"]("O-002")], 2, **IMPOSTA))
            s = RV["show_reviews"](eng)
            rev = s["reviews"][0]
            self.assertEqual(rev["state"], "stale")
            self.assertEqual({f["id"]: f["revalidate"] for f in rev["findings"]},
                             {"REV-0001.F01": True, "REV-0001.F02": False})
            self.assertEqual(s["open_findings"], [], "um parecer stale fechou ou abriu achado "
                             "da revisão corrente")
            refused(self, lambda: RV["dispose"](eng, "REV-0001.F02", "accepted", "corrigido"),
                    "STALE_INPUT")

    def test_a_mandate_without_review_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            mandato(eng, "ux-process")
            self.assertEqual(RV["show_reviews"](eng)["reviews"][0]["state"], "mandated")


class Disposicoes(unittest.TestCase):

    def test_each_disposition_carries_what_it_needs(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            RV["receive"](eng, m["task_id"], parecer(m))
            f = "REV-0001.F01"
            for disp, extra in (("rejected", {}), ("delegated", {"envelope": "x"}),
                                ("deferred", {}), ("escalated", {}), ("talvez", {})):
                refused(self, lambda: RV["dispose"](eng, f, disp, "motivo", **extra),
                        "INTEGRITY_FAILURE")
            refused(self, lambda: RV["dispose"](eng, f, "accepted", " "), "INTEGRITY_FAILURE")

    def test_dispositions_append_and_the_minority_opinion_stays(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = dois(tmp)
            m = mandato(eng)
            RV["receive"](eng, m["task_id"], parecer(m))
            antes = (eng / "_design/reviews/REV-0001.json").read_bytes()
            su = O["digest"](eng / "shared-understanding.md")
            RV["dispose"](eng, "REV-0001.F01", "deferred", "fica para a prova de carga",
                          impact="o pico pode exigir fila")
            self.assertEqual(RV["show_reviews"](eng)["open_findings"], ["REV-0001.F01"])
            RV["dispose"](eng, "REV-0001.F01", "rejected", "o volume cabe",
                          evidence="volumes.xlsx#B12")
            self.assertEqual(RV["show_reviews"](eng)["open_findings"], [])
            led = RV["read_ledger"](eng)["data"]
            self.assertEqual([d["disposition"] for d in led["dispositions"]],
                             ["deferred", "rejected"])
            self.assertEqual((eng / "_design/reviews/REV-0001.json").read_bytes(), antes)
            self.assertTrue((eng / "_design/history/review-ledger.r0001.json").is_file())
            self.assertEqual(O["digest"](eng / "shared-understanding.md"), su,
                             "um parecer escreveu na SU")


class Dialectica(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.eng = dois(self.tmp.name)
        a, b = mandato(self.eng), mandato(self.eng, "data-integration")
        RV["receive"](self.eng, a["task_id"], parecer(a))
        RV["receive"](self.eng, b["task_id"], parecer(b, findings=[achado("O-001", "fact")]))

    def tearDown(self):
        self.tmp.cleanup()

    def test_t30_two_calls_without_accepted_synthesis_escalate(self):
        d = RV["diverge"](self.eng, ["REV-0001.F01"], "fila ou processamento directo")
        div = d["data"]["divergences"][0]["id"]
        RV["dialectic_call"](self.eng, div, "contested")
        r = RV["dialectic_call"](self.eng, div, "contested")
        self.assertEqual(r["data"]["divergences"][0]["status"], "escalated")
        refused(self, lambda: RV["dialectic_call"](self.eng, div, "synthesis_accepted", "x"),
                "INTEGRITY_FAILURE")

    def test_t30_the_fourth_divergence_is_born_escalated(self):
        for i in range(3):
            RV["diverge"](self.eng, ["REV-0001.F01"], "divergência {}".format(i))
        d = RV["diverge"](self.eng, ["REV-0001.F01"], "a quarta")["data"]["divergences"]
        self.assertEqual([x["status"] for x in d], ["open", "open", "open", "escalated"])

    def test_a_fact_is_not_settled_by_synthesis_without_a_locator(self):
        d = RV["diverge"](self.eng, ["REV-0001.F01", "REV-0002.F01"], "o volume de pico")
        div = d["data"]["divergences"][0]
        self.assertEqual(div["kind"], "fact")
        refused(self, lambda: RV["dialectic_call"](self.eng, div["id"], "synthesis_accepted",
                                                   "concordam no volume"), "INTEGRITY_FAILURE")
        r = RV["dialectic_call"](self.eng, div["id"], "synthesis_accepted", "volume medido",
                                 locator="volumes.xlsx#B12")
        self.assertEqual(r["data"]["divergences"][0]["status"], "synthesized")

    def test_a_recommendation_synthesis_closes_the_divergence(self):
        d = RV["diverge"](self.eng, ["REV-0001.F01"], "fila ou directo")
        div = d["data"]["divergences"][0]["id"]
        r = RV["dialectic_call"](self.eng, div, "synthesis_accepted", "fila só no pico")
        self.assertEqual(r["data"]["divergences"][0]["status"], "synthesized")


if __name__ == "__main__":
    unittest.main()
