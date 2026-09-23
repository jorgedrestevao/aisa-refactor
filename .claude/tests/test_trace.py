# -*- coding: utf-8 -*-
"""handoff-v1 F6.2 — rastreabilidade vertical nos dois sentidos.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §2.

    órfãos  item do âmbito sem contrato (N1), FC do âmbito sem trabalho, trabalho sem
            aceitação, WP sem motivo de desenho; exclusão autorizada não gera achado
    T31     cada obrigação de prova do desenho tem WP que a prova e condição de aceitação
    T34     uma pergunta em aberto `proof_obligation` pode invalidar a viabilidade: bloqueia o
            compromisso e é nomeada, não fica numa checklist
    T37     headless: nenhuma obrigação de ecrã; a interface é «não aplicável»
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
IT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_inventory.py"))
DP = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_design_path.py"))
E2E = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_02_discovery.py"))
TR = runpy.run_path(str(TOOLS / "trace.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
BP = IT["BP"]
PO = BP + "#architecture/proof_obligations[0]"
PROVA = ("  proof_obligations:\n    - claim: \"a chave de submissão é única sob concorrência\"\n"
         "      level: V2\n      method: \"teste de carga\"\n      owner: developer\n"
         "      funded: yes\n")
PROOF_ROW = ("| U-009 | operations | A plataforma garante unicidade sob 50 submissões "
             "simultâneas? | proof_obligation | viabilidade: sem isto a submissão idempotente "
             "cai | submissão (proposed_to_be) | fonte: ensaio técnico | ensaio com 50 "
             "submissões | blocks_scope | Critical | ensaio | dimensionante: decide a forma | "
             "entrevista-processo.md#¶7 | R-01 |")


def escopo(eng, includes=("J-0001", "J-0003")):
    return IT["escopo"](eng, includes=[{"ref": r, "reason": "no âmbito"} for r in includes])


def wps(**over2):
    w1 = IT["wp"]()
    w2 = IT["wp"]("WP-0002", purpose="Aprovação com segregação", realizes=["FC-0003"],
                  acceptance=[{"fc": "FC-0003", "condition": "exemplo negativo"}])
    w2.update(over2)
    return [w1, w2]


def montado(tmp, includes=("J-0001", "J-0003"), items=None, prova=False):
    eng = IT["engagement"](tmp)
    if prova:
        p = eng / BP
        p.write_text(p.read_text(encoding="utf-8").replace("entities:", PROVA + "entities:"),
                     encoding="utf-8")
    IT["publish"](eng, "scope", escopo(eng, includes))
    IT["publish"](eng, "work-packages", IT["inventario"](eng, items or wps()))
    return eng


def codes(r):
    return sorted({(f["code"], f["ref"]) for f in r["findings"]})


class Orfaos(unittest.TestCase):

    def test_a_complete_scope_has_no_orphans_and_the_exclusion_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](montado(tmp))
            self.assertTrue(r["ok"], r["findings"])
            self.assertEqual({c["ref"]: c["wp"] for c in r["chains"]},
                             {"J-0001": ["WP-0001"], "J-0003": ["WP-0002"]})
            self.assertNotIn("FC-0002", json.dumps(r["findings"]))

    def test_n1_an_included_item_without_contract_is_an_orphan(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](montado(tmp, includes=("J-0001", "J-0003", "C-001")))
            self.assertIn(("NO_CONTRACT", "C-001"), codes(r))

    def test_a_requirement_realised_directly_by_work_is_not_an_orphan(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = wps() + [IT["wp"]("WP-0003", purpose="Âmbito geral", realizes=["C-001"],
                                      acceptance=[{"condition": "o pedido segue para compras"}])]
            r = TR["trace"](montado(tmp, includes=("J-0001", "J-0003", "C-001"), items=items))
            self.assertTrue(r["ok"], r["findings"])

    def test_a_contract_in_scope_without_work_or_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](montado(tmp, items=[IT["wp"]()]))
            self.assertIn(("NO_WORK", "FC-0003"), codes(r))
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](montado(tmp, items=wps(acceptance=[])))
            self.assertIn(("NO_TEST", "FC-0003"), codes(r))

    def test_work_without_a_design_reason_is_an_orphan(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = wps() + [IT["wp"]("WP-0003", purpose="Algo", realizes=[])]
            r = TR["trace"](montado(tmp, items=items))
            self.assertIn(("NO_DESIGN_REASON", "WP-0003"), codes(r))


class Provas(unittest.TestCase):

    def test_t31_a_proof_obligation_without_work_or_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](montado(tmp, prova=True))
            self.assertIn(("PROOF_WITHOUT_WORK", PO), codes(r))
        with tempfile.TemporaryDirectory() as tmp:
            items = wps() + [IT["wp"]("WP-0003", purpose="Prova de unicidade",
                                      realizes=["FC-0001"], proves=[PO], acceptance=[])]
            r = TR["trace"](montado(tmp, items=items, prova=True))
            self.assertIn(("PROOF_WITHOUT_ACCEPTANCE", PO), codes(r))

    def test_t31_a_proved_obligation_names_its_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = wps() + [IT["wp"]("WP-0003", purpose="Prova de unicidade",
                                      realizes=["FC-0001"], proves=[PO],
                                      acceptance=[{"condition": "50 submissões, 50 pedidos"}])]
            r = TR["trace"](montado(tmp, items=items, prova=True))
            self.assertTrue(r["ok"], r["findings"])
            self.assertEqual(r["proofs"][0]["wp"], ["WP-0003"])
            self.assertEqual(r["proofs"][0]["level"], "V2")

    def test_t34_an_open_viability_proof_blocks_even_with_work_planned(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = montado(tmp)
            E2E["publish_analysis"](eng, {"Unknown": [PROOF_ROW]})
            r = TR["trace"](eng)
            self.assertIn(("VIABILITY_PROOF_OPEN", "U-009"), codes(r))
            self.assertEqual(r["viability_blockers"][0]["bloqueio"], "blocks_scope")
            self.assertFalse(r["ok"])


class Headless(unittest.TestCase):

    def test_t37_no_screen_obligation_without_applicability(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = DP["headless"](tmp)
            sha = runpy.run_path(str(TOOLS / "operation.py"))["digest"](
                eng / "_blueprint" / "ux-blueprint_v01.yaml")
            dados = {"schema_version": "handoff-functional/1", "engagement_id": eng.name,
                     "revision": 1,
                     "based_on": [{"ref": "_blueprint/ux-blueprint_v01.yaml", "sha256": sha}],
                     "retired_ids": [], "items": [DP["fc_sync"]()]}
            F["publish"](eng, DP["FC"]["write_draft"](eng, dados))
            IT["publish"](eng, "scope", {
                "schema_version": "handoff-scope/1", "engagement_id": eng.name, "revision": 1,
                "based_on": [], "retired_ids": [], "items": [{
                    "id": "SCOPE-0010", "name": "Envio ao ERP-X", "authorized_by": None,
                    "includes": [{"ref": "J-0010", "reason": "o envio"}], "excludes": []}]})
            IT["publish"](eng, "work-packages", IT["inventario"](eng, [IT["wp"](
                "WP-0010", scope_id="SCOPE-0010", purpose="Envio nocturno",
                realizes=["FC-0010", "_blueprint/ux-blueprint_v01.yaml#architecture/"
                          "compositions[component=sincronizacao-nocturna]"],
                acceptance=[{"fc": "FC-0010", "condition": "não nasce segunda encomenda"}])]))
            r = TR["trace"](eng)
            self.assertEqual(r["applicability"]["ui"], "not_applicable (headless)")
            self.assertTrue(r["ok"], r["findings"])
            self.assertNotIn("screen", json.dumps(r["findings"]).lower())


if __name__ == "__main__":
    unittest.main()
