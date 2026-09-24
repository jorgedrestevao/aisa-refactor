# -*- coding: utf-8 -*-
"""handoff-v1 F5.1 — candidatos de Options publicados, com regras por rota.

Desenho: `docs/handoff-v1/F5/DESENHO.md` §1 (Q2).

    T27  plataforma imposta → viabilidade e padrões dentro dela, sem shortlist artificial de
         plataformas; um candidato viável basta, com motivo
    publicação: uma operação do coordenador, revisão corrente + cópia imutável; ids nunca
         reutilizados; base ou inputs mudados → `STALE_INPUT`
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
E2E = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_02_discovery.py"))
RV = runpy.run_path(str(TOOLS / "review.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
AUTORIDADE = "decisions.md#D-001"


def engagement(tmp, route="solution-choice"):
    eng = E2E["engagement"](tmp)
    E2E["publish_analysis"](eng)
    p = eng / "_state.json"
    st = json.loads(p.read_text(encoding="utf-8"))
    st["workflow"]["route"] = route
    if route == "platform-constrained":
        st["workflow"]["route_basis"] = {"justification": "plataforma imposta pela direcção "
                                         "de SI (sintético)", "source_refs": ["pedido.md#¶3"],
                                         "authority_ref": AUTORIDADE}
    p.write_text(json.dumps(st, ensure_ascii=False) + "\n", encoding="utf-8")
    return eng


def cand(cid, platform="Plataforma X", **over):
    c = {"id": cid, "name": "Candidato " + cid, "option_class": "aplicação na plataforma",
         "platform": platform, "technology": "{} — forma {}".format(platform, cid),
         "architecture": "registo de pedidos com aprovação e passagem a compras",
         "order_of_magnitude": {"value": "4–6 semanas", "source": "ANALOGY (sintético)"},
         "risks": ["regra de arredondamento por escolher (U-001)"],
         "reversibility": "média", "premise_refs": ["C-002"]}
    c.update(over)
    return c


def conjunto(eng, items, revision=1, **extra):
    route = json.loads((eng / "_state.json").read_text(encoding="utf-8"))["workflow"]["route"]
    d = {"schema_version": "handoff-candidates/1", "engagement_id": eng.name,
         "revision": revision, "route": route, "based_on": [{"ref": "frame.md"}],
         "retired_ids": [], "criteria": ["cumprir a regra de aprovação"], "exclusions": [],
         "items": items}
    d.update(extra)
    return d


def publish(eng, data):
    dr = RV["draft_candidates"](eng)
    Path(dr["path"]).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return RV["publish_candidates"](eng, dr["draft"])


def refused(test, eng, data, code):
    with test.assertRaises(RV["ReviewError"]) as err:
        publish(eng, data)
    test.assertEqual(err.exception.code, "INTEGRITY_FAILURE")
    test.assertIn(code, [p["code"] for p in err.exception.detail["problems"]])


class Publicacao(unittest.TestCase):

    def test_one_operation_with_immutable_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            r = publish(eng, conjunto(eng, [cand("O-001"), cand("O-002"), cand("O-003")]))
            self.assertTrue(r["operation_id"].startswith("candidates-"))
            h1 = (eng / "_design/history/candidates.r0001.json").read_bytes()
            publish(eng, conjunto(eng, [cand("O-001"), cand("O-002"), cand("O-003", name="x")],
                                  2))
            self.assertEqual((eng / "_design/history/candidates.r0001.json").read_bytes(), h1)
            self.assertEqual(RV["show_candidates"](eng)["revision"], 2)

    def test_ids_are_never_reused_and_the_route_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            tres = [cand("O-001"), cand("O-002"), cand("O-003")]
            publish(eng, conjunto(eng, tres))
            refused(self, eng, conjunto(eng, tres[:2], 2, reduction_reason="x"),
                    "SILENT_REMOVAL")
            refused(self, eng, conjunto(eng, tres, 2, route="change-impact"), "ROUTE")

    def test_a_changed_input_after_the_draft_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            dr = RV["draft_candidates"](eng)
            self.assertEqual(RV["open_candidate_drafts"](eng), [dr["draft"]])
            Path(dr["path"]).write_text(json.dumps(conjunto(eng, [cand("O-001"), cand("O-002"),
                                                                  cand("O-003")])),
                                        encoding="utf-8")
            su = eng / "shared-understanding.md"
            su.write_text(su.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(RV["ReviewError"]) as err:
                RV["publish_candidates"](eng, dr["draft"])
            self.assertEqual(err.exception.code, "STALE_INPUT")

    def test_a_dead_premise_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            refused(self, eng, conjunto(eng, [cand("O-001", premise_refs=["C-999"]),
                                              cand("O-002"), cand("O-003")]), "DEAD_REF")

    def test_a_missing_order_of_magnitude_source_is_a_visible_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            r = publish(eng, conjunto(eng, [cand("O-001", order_of_magnitude={"value": "x"}),
                                            cand("O-002"), cand("O-003")]))
            self.assertIn("NO_ORDER_OF_MAGNITUDE", [g["code"] for g in r["gaps"]])


class Rotas(unittest.TestCase):

    def test_solution_choice_never_shrinks_the_list_without_a_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            refused(self, eng, conjunto(eng, [cand("O-001"), cand("O-002")]),
                    "SHORTLIST_WITHOUT_REASON")
            publish(eng, conjunto(eng, [cand("O-001"), cand("O-002")],
                                  reduction_reason="só duas formas aplicam ao volume"))

    def test_t27_imposed_platform_single_viable_candidate_with_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp, "platform-constrained")
            r = publish(eng, conjunto(eng, [cand("O-001")], imposed_platform="Plataforma X",
                                      imposition_ref=AUTORIDADE,
                                      reduction_reason="uma forma viável dentro da imposta"))
            self.assertEqual(r["revision"], 1)

    def test_t27_no_candidate_outside_the_imposed_platform(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp, "platform-constrained")
            refused(self, eng, conjunto(eng, [cand("O-001"), cand("O-002", platform="Outra")],
                                        imposed_platform="Plataforma X",
                                        imposition_ref=AUTORIDADE),
                    "OUTSIDE_IMPOSED_PLATFORM")

    def test_t27_the_imposition_must_be_the_route_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp, "platform-constrained")
            refused(self, eng, conjunto(eng, [cand("O-001")], imposed_platform="Plataforma X",
                                        imposition_ref="decisions.md#D-999"), "IMPOSITION_REF")
            refused(self, eng, conjunto(eng, [cand("O-001")], imposition_ref=AUTORIDADE),
                    "NO_IMPOSED_PLATFORM")

    def test_change_impact_describes_the_delta_on_a_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp, "change-impact")
            refused(self, eng, conjunto(eng, [cand("O-001")]), "NO_BASELINE")
            refused(self, eng, conjunto(eng, [cand("O-001")], baseline_ref="D-001"), "NO_DELTA")
            publish(eng, conjunto(eng, [cand("O-001", delta="acrescenta o pedido urgente",
                                             impact_refs=["FC-0001"])], baseline_ref="D-001"))


if __name__ == "__main__":
    unittest.main()
