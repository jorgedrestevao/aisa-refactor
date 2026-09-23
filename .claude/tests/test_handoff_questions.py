# -*- coding: utf-8 -*-
"""handoff-v1 F1.5 — os campos de uma pergunta na SU (states.md -> Admission of a question).

Decisao Q3: tipo, impacto, ambito, fecho, bloqueio e referencias sao colunas das tabelas
Unknown e Conflicted. O parser unico (`dashboard.parse_su`) le-as pelo cabecalho; uma SU
sem elas continua a ler-se e nada e reclassificado.

Fixture: `.claude/tests/fixtures/su-schemas/handoff-v1-shared-understanding.md`
(sintetica, derivada de fx-hv1-02 e fx-hv1-04).
"""
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "dashboard.py"))
FX = ROOT / ".claude" / "tests" / "fixtures" / "su-schemas"
NOVA = (FX / "handoff-v1-shared-understanding.md").read_text(encoding="utf-8")
ANTIGA = (FX / "pre-v2.3-shared-understanding.md").read_text(encoding="utf-8")


def linhas(md):
    _h, rows, secs, diags = D["parse_su"](md)
    return {r["id"]: r for r in rows}, secs, diags


class Colunas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.r, cls.secs, cls.diags = linhas(NOVA)

    def test_the_question_fields_are_read_by_header(self):
        u = self.r["U-001"]
        self.assertTrue(u["handoff_cols"])
        self.assertEqual(u["tipo"], "design_choice")
        self.assertEqual(u["impacto_aspectos"], ["funcional", "aceitacao"])
        self.assertIn("1,02 €", u["impacto_texto"])
        self.assertIn("proposed_to_be", u["ambito"])
        self.assertTrue(u["fecho"])
        self.assertEqual(u["bloqueio"], "blocks_scope")
        self.assertIn("#C2", u["referencias"])

    def test_a_conflicted_row_is_recognised_as_the_new_schema(self):
        """Conflicted nao tem `tipo`; qualquer coluna da admissao marca o schema novo."""
        self.assertTrue(self.r["X-001"]["handoff_cols"])

    def test_the_role_that_answers_is_not_read_from_the_impact_column(self):
        """`impacto` era alias de `support` (coluna do Risky). Numa pergunta, o papel que
        responde nao pode passar a ser o texto do impacto."""
        self.assertEqual(self.r["U-001"]["support"], "role: responsável de compras com contabilidade")
        self.assertEqual(self.r["X-001"]["quem_decide"], "role: dono do processo")
        self.assertEqual(self.r["X-001"]["support"], "matriz de papéis ∧ entrevista")

    def test_risky_keeps_impact_as_its_payload(self):
        self.assertEqual(self.r["R-001"]["support"], "envio falha e repete")
        self.assertFalse(self.r["R-001"]["impacto_raw"])

    def test_an_impact_without_a_known_aspect_is_not_fabricated(self):
        u = self.r["U-003"]
        self.assertEqual(u["impacto_aspectos"], [])
        self.assertEqual(u["impacto_forma"], "nao-lida")

    def test_the_plan_words_map_to_the_five_aspects(self):
        self.assertEqual(self.r["U-004"]["impacto_aspectos"], ["viabilidade", "operacao"])


class Estacionada(unittest.TestCase):
    """T07 (metade da SU): sem impacto demonstravel estaciona-se com motivo; sem motivo
    nao e estacionamento e a pergunta continua aberta."""

    @classmethod
    def setUpClass(cls):
        cls.r, cls.secs, cls.diags = linhas(NOVA)

    def test_a_parked_question_with_a_reason_is_not_open(self):
        u = self.r["U-003"]
        self.assertTrue(u["parked"])
        self.assertTrue(u["resolved"])
        self.assertIn("sem impacto demonstrável", u["parked_reason"])

    def test_parking_without_a_reason_is_invalid_and_the_question_stays_open(self):
        u = self.r["U-005"]
        self.assertFalse(u["parked"])
        self.assertFalse(u["resolved"])
        self.assertTrue(any("U-005" in d["message"] and "sem motivo" in d["message"]
                            for d in self.diags))

    def test_a_parked_question_is_not_a_closure(self):
        _h, rows, _s, _d = D["parse_su"](NOVA)
        delta = D["round_delta"](rows, {})
        self.assertEqual(delta["estacionadas"], 1)
        por = delta["por_ronda"]
        fechadas = sum(x.get("fechadas", 0) for x in (por.values() if isinstance(por, dict)
                                                      else por))
        self.assertEqual(fechadas, 0)

    def test_the_section_counts_parked_rows(self):
        self.assertEqual(self.secs["sections"]["Unknown"]["estacionada"], 1)


class SUAntiga(unittest.TestCase):

    def test_a_su_without_the_columns_is_read_and_flagged_as_such(self):
        r, _s, _d = linhas(ANTIGA)
        perguntas = [x for x in r.values() if x["state"] == "Unknown"]
        self.assertTrue(perguntas)
        for x in perguntas:
            self.assertFalse(x["handoff_cols"])
            self.assertEqual(x["tipo"], "")
            self.assertFalse(x["parked"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
