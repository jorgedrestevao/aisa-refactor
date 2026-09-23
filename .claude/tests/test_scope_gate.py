# -*- coding: utf-8 -*-
"""handoff-v1 F6.3 — estimativa contra o inventário, gate de âmbito e as lacunas N2/N3.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §3.

    T32  a estimativa cita cada WP uma vez e a revisão corrente do inventário; WP sem
         estimativa, estimado duas vezes, inexistente, revisão antiga → achados; a spec não
         leva durações no inventário; o backlog deriva do inventário
    T33  um bloqueio num item incluído bloqueia a entrega; um parcial só com exclusão
         autorizada e dependências coerentes
    N4   excluir o FC que produz um campo obrigatório do desenho é incoerente
    N2   o bloco de aprovação do desenho leva o `sha256` da versão; mudança depois →
         `stale`, sem impressão → `unverified`; ambos bloqueiam a versão final
    N3   um actor que o desenho não tem é aviso, não lacuna
"""
import re
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_trace.py"))
IT = TT["IT"]
AU = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_authorization.py"))
E2E = TT["E2E"]
TR = runpy.run_path(str(TOOLS / "trace.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
EST = ("| Unidade | Esforço |\n|---|---|\n| WP-0001 submissão | 3–5 d |\n"
       "| WP-0002 aprovação | 2–3 d |\n\nInventário r1.\n")
BLOCKS_ALL = ("| U-010 | governance | A plataforma pode guardar dados pessoais nesta região? | "
              "fact_gap | segurança: sem isto nada se constrói | todo o âmbito (proposed_to_be) "
              "| fonte: jurídico | parecer escrito | blocks_all | Critical | documento | "
              "dimensionante: condiciona tudo | pedido.md#¶3 | R-01 |")


def codes(findings):
    return sorted({(f["code"], f["ref"]) for f in findings})


class Estimativa(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng = TT["montado"](cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_t32_one_unit_per_wp_on_the_current_revision(self):
        self.assertTrue(TR["derived_check"](self.eng, EST)["ok"])

    def test_t32_missing_duplicated_unknown_and_stale(self):
        r = TR["derived_check"](self.eng, EST.replace("| WP-0002 aprovação | 2–3 d |\n", ""))
        self.assertIn(("UNESTIMATED_WP", "WP-0002"), codes(r["findings"]))
        r = TR["derived_check"](self.eng, EST + "| WP-0001 de novo | 1 d |\n")
        self.assertIn(("DUPLICATE_ESTIMATE", "WP-0001"), codes(r["findings"]))
        r = TR["derived_check"](self.eng, EST + "| WP-0009 | 1 d |\n")
        self.assertIn(("UNKNOWN_WP", "WP-0009"), codes(r["findings"]))
        r = TR["derived_check"](self.eng, EST.replace("Inventário r1", "Inventário r0"))
        self.assertIn("STALE_INVENTORY", [f["code"] for f in r["findings"]])
        r = TR["derived_check"](self.eng, EST.replace("Inventário r1.", ""))
        self.assertIn("NO_INVENTORY_REVISION", [f["code"] for f in r["findings"]])

    def test_t32_no_duration_in_the_spec_inventory(self):
        self.assertEqual(TR["spec_effort_check"]("| WP-0001 | submissão | 3 dias |"),
                         [{"code": "EFFORT_IN_SPEC", "ref": "WP-0001", "scope": "",
                           "detail": "a linha do inventário na spec leva duração: «3 dias»"}])
        self.assertEqual(TR["spec_effort_check"]("A chefia valida no mesmo dia útil.\n"
                                                 "| WP-0001 | submissão | —  |"), [])

    def test_the_backlog_derives_from_the_inventory(self):
        backlog = "| WP-0001 | história A |\n| WP-0001 | história B |\n| WP-0002 | C |\n" \
                  "inventário r1"
        self.assertTrue(TR["derived_check"](self.eng, backlog, "backlog")["ok"])
        r = TR["derived_check"](self.eng, "| WP-0001 | A |\ninventário r1", "backlog")
        self.assertIn(("MISSING_IN_BACKLOG", "WP-0002"), codes(r["findings"]))


class GateDeAmbito(unittest.TestCase):

    def test_n4_excluding_the_producer_of_a_required_field_is_incoherent(self):
        with tempfile.TemporaryDirectory() as tmp:
            g = TR["scope_gate"](TT["montado"](tmp))
            self.assertEqual(g["delivery"], "blocked")
            self.assertIn(("REQUIRED_FIELD_WITHOUT_PRODUCER", "pedidos.valor_total"),
                          codes(g["incoherent"]))

    def test_t33_a_coherent_partial_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = IT["engagement"](tmp)
            p = eng / IT["BP"]
            p.write_text(p.read_text(encoding="utf-8").replace(
                "name: valor_total, type: number, required: true",
                "name: valor_total, type: number, required: false"), encoding="utf-8")
            IT["publish"](eng, "scope", TT["escopo"](eng))
            IT["publish"](eng, "work-packages", IT["inventario"](eng, TT["wps"]()))
            g = TR["scope_gate"](eng)
            self.assertEqual(g["delivery"], "partial", g)
            self.assertEqual(g["excluded"], ["FC-0002"])

    def test_t33_a_blocker_in_an_included_item_blocks_the_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = IT["engagement"](tmp)
            s = TT["escopo"](eng)
            s["items"][0]["excludes"] = []
            IT["publish"](eng, "scope", s)
            IT["publish"](eng, "work-packages", IT["inventario"](eng, TT["wps"]() + [
                IT["wp"]("WP-0003", purpose="Valor", realizes=["FC-0002"],
                         acceptance=[{"fc": "FC-0002", "condition": "exemplo de fronteira"}])]))
            g = TR["scope_gate"](eng)
            self.assertEqual(g["delivery"], "blocked")
            self.assertIn(("FC_NOT_AUTHORIZABLE", "FC-0002"), codes(g["blockers"]))

    def test_work_for_an_excluded_item_is_incoherent(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = TT["wps"]() + [IT["wp"]("WP-0003", purpose="Valor", realizes=["FC-0002"]),
                                   IT["wp"]("WP-0004", purpose="Relatório",
                                            realizes=["FC-0001"], depends_on=["WP-0003"])]
            g = TR["scope_gate"](TT["montado"](tmp, items=items))
            self.assertIn(("WORK_FOR_EXCLUDED", "WP-0003"), codes(g["incoherent"]))
            self.assertIn(("DEPENDS_ON_EXCLUDED", "WP-0004"), codes(g["incoherent"]))

    def test_an_open_blocks_all_question_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            E2E["publish_analysis"](eng, {"Unknown": [BLOCKS_ALL]})
            self.assertIn(("BLOCKS_ALL_OPEN", "U-010"),
                          codes(TR["scope_gate"](eng)["blockers"]))


class AprovacaoDoDesenho(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.eng = IT["engagement"](self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_n2_the_approval_carries_the_design_fingerprint(self):
        self.assertEqual(F["blueprint_approval_state"](self.eng)["state"], "current")
        bloco = F["blueprint_approval_block"](self.eng, "01", AU["OWNER"],
                                              timestamp="2026-09-24T09:00:00Z")
        self.assertRegex(bloco, r"\*\*Blueprint sha256\*\*: [0-9a-f]{64}")
        with self.assertRaises(F["FunctionalError"]):
            F["blueprint_approval_block"](self.eng, "01", "claude",
                                          timestamp="2026-09-24T09:00:00Z")

    def test_n2_a_design_changed_after_approval_blocks_the_final_version(self):
        p = self.eng / IT["BP"]
        p.write_text(p.read_text(encoding="utf-8") + "\n# nota\n", encoding="utf-8")
        self.assertEqual(F["blueprint_approval_state"](self.eng)["state"], "stale")
        g = F["render_gate"](self.eng, text="FC-0001")
        self.assertIn("BLUEPRINT_APPROVAL_STALE", [b["code"] for b in g["blocked"]])

    def test_n2_an_approval_without_fingerprint_is_unverified(self):
        d = self.eng / "decisions.md"
        texto = d.read_text(encoding="utf-8")
        sem = re.sub(r"- \*\*Blueprint sha256\*\*: [0-9a-f]{64}\n", "", texto)
        self.assertNotEqual(sem, texto)
        d.write_text(sem, encoding="utf-8")
        self.assertEqual(F["blueprint_approval_state"](self.eng)["state"], "unverified")
        self.assertIn("BLUEPRINT_APPROVAL_UNVERIFIED",
                      [b["code"] for b in F["render_gate"](self.eng, text="FC-0001")["blocked"]])

    def test_n3_an_actor_the_design_lacks_is_a_warning_not_a_gap(self):
        v = F["show"](self.eng)["items"]["FC-0003"]
        self.assertEqual([w["code"] for w in v["warnings"]], ["ACTOR_NOT_IN_DESIGN"])
        self.assertTrue(v["authorizable"])


if __name__ == "__main__":
    unittest.main()
